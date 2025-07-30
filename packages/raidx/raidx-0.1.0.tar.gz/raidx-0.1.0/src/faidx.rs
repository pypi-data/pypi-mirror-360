use crate::errors::{FaidxError, Result};
use crate::sequence::Sequence;
use memmap2::Mmap;
use pyo3::prelude::*;
use std::collections::HashMap;
use std::fs::File;
use std::io::{BufRead, BufReader, Read, Seek, SeekFrom};
use std::path::Path;

#[derive(Debug, Clone)]
pub struct IndexRecord {
    pub rlen: usize, // sequence length
    pub offset: u64, // byte offset to sequence start
    pub lenc: usize, // line length (characters)
    pub lenb: usize, // line length (bytes, including newline)
}

#[pyclass]
pub struct Faidx {
    filename: String,
    indexname: String,
    index: HashMap<String, IndexRecord>,
    file_mmap: Option<Mmap>,
    file_handle: Option<File>,
    as_raw: bool,
    pub strict_bounds: bool,
    sequence_always_upper: bool,
    one_based_attributes: bool,
    default_seq: Option<String>,
    // These fields are kept for pyfaidx compatibility but not yet fully implemented
    _mutable: bool,
    _key_function: Option<PyObject>,
    _split_char: Option<String>,
    _filt_function: Option<PyObject>,
    _read_long_names: bool,
    _duplicate_action: String,
    _read_ahead: Option<usize>,
}

#[pymethods]
impl Faidx {
    #[new]
    #[pyo3(signature = (
        filename,
        indexname=None,
        as_raw=false,
        strict_bounds=false,
        sequence_always_upper=false,
        rebuild=true,
        build_index=true,
        one_based_attributes=true,
        default_seq=None,
        mutable=false,
        key_function=None,
        split_char=None,
        filt_function=None,
        read_long_names=false,
        duplicate_action="stop".to_string(),
        read_ahead=None
    ))]
    pub fn new(
        filename: String,
        indexname: Option<String>,
        as_raw: bool,
        strict_bounds: bool,
        sequence_always_upper: bool,
        rebuild: bool,
        build_index: bool,
        one_based_attributes: bool,
        default_seq: Option<String>,
        mutable: bool,
        key_function: Option<PyObject>,
        split_char: Option<String>,
        filt_function: Option<PyObject>,
        read_long_names: bool,
        duplicate_action: String,
        read_ahead: Option<usize>,
    ) -> PyResult<Self> {
        let mut faidx = Faidx {
            indexname: indexname.unwrap_or_else(|| format!("{}.fai", filename)),
            filename: filename.clone(),
            index: HashMap::new(),
            file_mmap: None,
            file_handle: None,
            as_raw,
            strict_bounds,
            sequence_always_upper,
            one_based_attributes,
            default_seq,
            _mutable: mutable,
            _key_function: key_function,
            _split_char: split_char,
            _filt_function: filt_function,
            _read_long_names: read_long_names,
            _duplicate_action: duplicate_action,
            _read_ahead: read_ahead,
        };

        // Check if file exists
        if !Path::new(&filename).exists() {
            return Err(FaidxError::FastaNotFound(filename).into());
        }

        // Try to use memory mapping for better performance
        let _file_mode = if mutable { "r+b" } else { "rb" };
        match File::options().read(true).write(mutable).open(&filename) {
            Ok(file) => {
                if !mutable {
                    match unsafe { Mmap::map(&file) } {
                        Ok(mmap) => faidx.file_mmap = Some(mmap),
                        Err(_) => faidx.file_handle = Some(file),
                    }
                } else {
                    faidx.file_handle = Some(file);
                }
            }
            Err(e) => return Err(FaidxError::IoError(e).into()),
        }

        let index_exists = Path::new(&faidx.indexname).exists();
        let index_is_stale = if index_exists {
            // Check if FASTA is newer than index
            let fasta_mtime = std::fs::metadata(&filename)
                .ok()
                .and_then(|m| m.modified().ok());
            let index_mtime = std::fs::metadata(&faidx.indexname)
                .ok()
                .and_then(|m| m.modified().ok());

            match (fasta_mtime, index_mtime) {
                (Some(f), Some(i)) => f > i,
                _ => false,
            }
        } else {
            false
        };

        if build_index && (!index_exists || (index_is_stale && rebuild)) {
            faidx.build_index()?;
        }

        faidx.read_index()?;
        Ok(faidx)
    }

    pub fn fetch(&self, name: String, start: usize, end: usize) -> PyResult<Sequence> {
        use std::cmp::min;

        let Some(record) = self.index.get(&name) else {
            return Err(FaidxError::FetchError(format!("Sequence '{}' not found", name)).into());
        };

        // Check bounds
        let length = record.rlen;
        if start > length || end > length {
            if self.strict_bounds {
                return Err(PyErr::new::<pyo3::exceptions::PyIndexError, _>(format!(
                    "coordinates {}-{} are out of bounds for sequence '{}' of length {}",
                    start, end, name, length
                )));
            } else {
                eprintln!(
                    "WARNING: coordinates {}-{} are out of bounds for sequence '{}' of length {}",
                    start, end, name, length
                );

                if start > length {
                    // Return empty sequence if start is completely out of bounds
                    return Ok(Sequence::new(
                        name.to_string(),
                        String::new(),
                        Some(start),
                        Some(start),
                        false,
                    ));
                }
            }
        }

        // Clamp coordinates to valid range when strict_bounds=False
        let clamped_start = if self.strict_bounds {
            start
        } else {
            min(start, length)
        };
        let clamped_end = if self.strict_bounds {
            end
        } else {
            min(end, length)
        };

        if clamped_start == 0 || clamped_end == 0 {
            if self.strict_bounds {
                return Err(PyErr::new::<pyo3::exceptions::PyIndexError, _>(
                    "coordinates cannot be 0 (1-based indexing)",
                ));
            } else {
                eprintln!("WARNING: coordinates cannot be 0 (1-based indexing)");
                return Ok(Sequence::new(
                    name.to_string(),
                    String::new(),
                    Some(clamped_start),
                    Some(clamped_end),
                    false,
                ));
            }
        }

        if clamped_start > clamped_end {
            if self.strict_bounds {
                return Err(PyErr::new::<pyo3::exceptions::PyIndexError, _>(format!(
                    "start coordinate {} is greater than end coordinate {}",
                    clamped_start, clamped_end
                )));
            } else {
                eprintln!(
                    "WARNING: start coordinate {} is greater than end coordinate {}",
                    clamped_start, clamped_end
                );
                return Ok(Sequence::new(
                    name.to_string(),
                    String::new(),
                    Some(clamped_start),
                    Some(clamped_end),
                    false,
                ));
            }
        }

        let seq_len = clamped_end - clamped_start + 1;

        // Optimized sequence extraction
        let mut seq = if let Some(ref mmap) = self.file_mmap {
            // Use memory mapping for fastest access
            Self::extract_sequence_from_mmap(mmap, record, clamped_start, seq_len)?
        } else if let Some(ref file) = self.file_handle {
            // Fall back to file I/O with proper seeking
            Self::extract_sequence_from_file_optimized(file, record, clamped_start, seq_len)?
        } else {
            return Err(FaidxError::IoError(std::io::Error::new(
                std::io::ErrorKind::Other,
                "No file handle available",
            ))
            .into());
        };

        // Trim to exact length requested (should already be correct due to early exit)
        seq.truncate(seq_len);

        // Pad with default sequence if needed
        if seq.len() < seq_len {
            if let Some(ref default_seq) = self.default_seq {
                let pad_len = seq_len - seq.len();
                seq.push_str(&default_seq.repeat(pad_len));
            }
        }

        if self.sequence_always_upper {
            // Optimized uppercase conversion
            unsafe {
                let bytes = seq.as_mut_vec();
                for byte in bytes.iter_mut() {
                    if *byte >= b'a' && *byte <= b'z' {
                        *byte -= 32;
                    }
                }
            }
        }

        let result_start = if self.one_based_attributes {
            Some(clamped_start)
        } else {
            Some(clamped_start - 1)
        };
        let result_end = Some(clamped_end);

        if self.as_raw {
            Ok(Sequence::new(name.to_string(), seq, None, None, false))
        } else {
            Ok(Sequence::new(
                name.to_string(),
                seq,
                result_start,
                result_end,
                false,
            ))
        }
    }

    /// Ultra-fast method for fetching entire sequences - bypasses all bounds checking
    pub fn fetch_entire_sequence(&self, name: String) -> PyResult<Sequence> {
        let Some(record) = self.index.get(&name) else {
            return Err(FaidxError::FetchError(format!("Sequence '{}' not found", name)).into());
        };

        let seq_len = record.rlen;

        // Direct extraction without any bounds checking or coordinate calculations
        let mut seq = if let Some(ref mmap) = self.file_mmap {
            // Use memory mapping for fastest access
            Self::extract_sequence_from_mmap(mmap, record, 1, seq_len)?
        } else if let Some(ref file) = self.file_handle {
            // Fall back to file I/O
            Self::extract_sequence_from_file_optimized(file, record, 1, seq_len)?
        } else {
            return Err(FaidxError::IoError(std::io::Error::new(
                std::io::ErrorKind::Other,
                "No file handle available",
            ))
            .into());
        };

        // Apply sequence transformations if needed
        if self.sequence_always_upper {
            // Optimized uppercase conversion
            unsafe {
                let bytes = seq.as_mut_vec();
                for byte in bytes.iter_mut() {
                    if *byte >= b'a' && *byte <= b'z' {
                        *byte -= 32;
                    }
                }
            }
        }

        let result_start = if self.one_based_attributes {
            Some(1)
        } else {
            Some(0)
        };
        let result_end = Some(seq_len);

        if self.as_raw {
            Ok(Sequence::new(name.to_string(), seq, None, None, false))
        } else {
            Ok(Sequence::new(
                name.to_string(),
                seq,
                result_start,
                result_end,
                false,
            ))
        }
    }

    pub fn __contains__(&self, name: String) -> bool {
        self.index.contains_key(&name)
    }

    #[getter]
    pub fn keys(&self) -> Vec<String> {
        self.index.keys().cloned().collect()
    }

    pub fn __repr__(&self) -> String {
        format!("Faidx(\"{}\")", self.filename)
    }
}

impl Faidx {
    /// Fast sequence extraction from memory map with dynamic optimization
    fn extract_sequence_from_mmap(
        mmap: &Mmap,
        record: &IndexRecord,
        start: usize,
        seq_len: usize,
    ) -> Result<String> {
        // Handle empty sequences first
        if record.rlen == 0 || seq_len == 0 || record.lenc == 0 {
            return Ok(String::new());
        }

        // Calculate precise starting position in FASTA (1-based to 0-based)
        let seq_start_pos = start - 1;
        let lines_before = seq_start_pos / record.lenc; // Now safe - lenc != 0
        let pos_in_line = seq_start_pos % record.lenc;
        let byte_offset =
            record.offset + lines_before as u64 * record.lenb as u64 + pos_in_line as u64;

        // Bounds check
        if byte_offset as usize >= mmap.len() {
            return Ok(String::new());
        }

        // Calculate precise bytes needed including newlines
        let approx_lines = (seq_len + record.lenc - 1) / record.lenc;
        let newline_overhead = approx_lines * (record.lenb - record.lenc);
        let read_size = seq_len + newline_overhead + record.lenb; // Add one line buffer
        let end_offset = std::cmp::min(byte_offset as usize + read_size, mmap.len());

        // Get the raw memory slice
        let raw_data = &mmap[byte_offset as usize..end_offset];

        // Pre-allocate with exact capacity
        let mut result_bytes = Vec::with_capacity(seq_len);

        // Dynamic batch sizing for optimal performance
        let batch_size = if seq_len > 100_000 { 1024 } else { 64 };

        // Optimized batched processing
        let mut i = 0;
        while i + batch_size <= raw_data.len() && result_bytes.len() < seq_len {
            let batch = &raw_data[i..i + batch_size];

            for &byte in batch {
                if result_bytes.len() >= seq_len {
                    break;
                }
                if byte != b'\n' && byte != b'\r' {
                    result_bytes.push(byte);
                }
            }
            i += batch_size;
        }

        // Process remaining bytes
        while i < raw_data.len() && result_bytes.len() < seq_len {
            let byte = raw_data[i];
            if byte != b'\n' && byte != b'\r' {
                result_bytes.push(byte);
            }
            i += 1;
        }

        // Ensure exact length
        result_bytes.truncate(seq_len);

        // Convert to string - safe since FASTA files contain ASCII
        Ok(unsafe { String::from_utf8_unchecked(result_bytes) })
    }

    /// Optimized sequence extraction from file handle using bulk operations
    fn extract_sequence_from_file_optimized(
        file: &File,
        record: &IndexRecord,
        start: usize,
        seq_len: usize,
    ) -> Result<String> {
        // Handle empty sequences first
        if record.rlen == 0 || seq_len == 0 || record.lenc == 0 {
            return Ok(String::new());
        }

        // Calculate starting position in FASTA (1-based to 0-based)
        let seq_start_pos = start - 1;
        let lines_before = seq_start_pos / record.lenc; // Now safe - lenc != 0
        let pos_in_line = seq_start_pos % record.lenc;
        let byte_offset =
            record.offset + lines_before as u64 * record.lenb as u64 + pos_in_line as u64;

        // Since we can't easily get the filename here, let's use unsafe but more carefully
        let mut file_ref = unsafe { &*(file as *const File as *mut File) };
        file_ref.seek(SeekFrom::Start(byte_offset))?;

        // Pre-allocate result vector with exact capacity for maximum efficiency
        let mut result_bytes = Vec::with_capacity(seq_len);

        // Use large buffer for optimal I/O performance
        const BUFFER_SIZE: usize = 1_048_576; // 1MB buffer
        let mut buffer = vec![0u8; BUFFER_SIZE];

        // Read and filter in large chunks for maximum throughput
        while result_bytes.len() < seq_len {
            match file_ref.read(&mut buffer) {
                Ok(0) => break, // EOF
                Ok(bytes_read) => {
                    // Ultra-fast filtering using bulk operations
                    let chunk = &buffer[..bytes_read];

                    // Process chunk efficiently
                    for &byte in chunk.iter() {
                        if result_bytes.len() >= seq_len {
                            break;
                        }
                        if byte != b'\n' && byte != b'\r' {
                            result_bytes.push(byte);
                        }
                    }
                }
                Err(e) => return Err(crate::errors::FaidxError::IoError(e)),
            }
        }

        // Truncate to exact length
        result_bytes.truncate(seq_len);

        // Convert to string - safe since FASTA files are ASCII
        Ok(unsafe { String::from_utf8_unchecked(result_bytes) })
    }

    pub fn get_sequence_length(&self, name: &str) -> Option<usize> {
        self.index.get(name).map(|record| record.rlen)
    }

    pub fn get_line_length(&self, name: &str) -> Option<usize> {
        self.index.get(name).map(|record| record.lenc)
    }

    pub fn get_long_name(&self, rname: &str) -> PyResult<String> {
        let _record = self
            .index
            .get(rname)
            .ok_or_else(|| FaidxError::FetchError(format!("Sequence '{}' not found", rname)))?;

        // This is a simplified implementation - in practice you'd need to read from the file
        // to get the full header line
        Ok(rname.to_string())
    }

    fn build_index(&mut self) -> Result<()> {
        let file = File::open(&self.filename)?;
        let mut reader = BufReader::new(file);
        let mut line = String::new();
        let mut current_name = String::new();
        let mut current_offset = 0u64;
        let mut current_rlen = 0usize;
        let mut current_lenc = 0usize;
        let mut current_lenb = 0usize;
        let mut line_count = 0usize;
        let mut index_entries = Vec::new();

        loop {
            line.clear();
            let bytes_read = reader.read_line(&mut line)?;
            if bytes_read == 0 {
                break; // EOF
            }

            if line.starts_with('>') {
                // Save previous sequence if any
                if !current_name.is_empty() {
                    index_entries.push((
                        current_name.clone(),
                        IndexRecord {
                            rlen: current_rlen,
                            offset: current_offset,
                            lenc: current_lenc,
                            lenb: current_lenb,
                        },
                    ));
                }

                // Start new sequence
                current_name = line[1..]
                    .trim()
                    .split_whitespace()
                    .next()
                    .unwrap_or("")
                    .to_string();
                current_offset = reader.stream_position()?;
                current_rlen = 0;
                current_lenc = 0;
                current_lenb = 0;
                line_count = 0;
            } else {
                // Sequence line
                let line_clen = line.trim_end_matches(&['\r', '\n']).len();
                let line_blen = line.len();

                if line_count == 0 {
                    current_lenc = line_clen;
                    current_lenb = line_blen;
                }

                current_rlen += line_clen;
                line_count += 1;
            }
        }

        // Save last sequence
        if !current_name.is_empty() {
            index_entries.push((
                current_name,
                IndexRecord {
                    rlen: current_rlen,
                    offset: current_offset,
                    lenc: current_lenc,
                    lenb: current_lenb,
                },
            ));
        }

        // Write index file
        self.write_index(&index_entries)?;

        // Update internal index
        self.index = index_entries.into_iter().collect();

        Ok(())
    }

    fn write_index(&self, entries: &[(String, IndexRecord)]) -> Result<()> {
        use std::io::Write;
        let mut file = File::create(&self.indexname)?;

        for (name, record) in entries {
            writeln!(
                file,
                "{}\t{}\t{}\t{}\t{}",
                name, record.rlen, record.offset, record.lenc, record.lenb
            )?;
        }

        Ok(())
    }

    fn read_index(&mut self) -> Result<()> {
        let file = File::open(&self.indexname)
            .map_err(|_| FaidxError::IndexNotFound(self.indexname.clone()))?;
        let reader = BufReader::new(file);

        for line in reader.lines() {
            let line = line?;
            let parts: Vec<&str> = line.trim().split('\t').collect();

            if parts.len() != 5 {
                continue;
            }

            let name = parts[0].to_string();
            let rlen = parts[1]
                .parse()
                .map_err(|_| FaidxError::IndexingError("Invalid rlen".to_string()))?;
            let offset = parts[2]
                .parse()
                .map_err(|_| FaidxError::IndexingError("Invalid offset".to_string()))?;
            let lenc = parts[3]
                .parse()
                .map_err(|_| FaidxError::IndexingError("Invalid lenc".to_string()))?;
            let lenb = parts[4]
                .parse()
                .map_err(|_| FaidxError::IndexingError("Invalid lenb".to_string()))?;

            self.index.insert(
                name,
                IndexRecord {
                    rlen,
                    offset,
                    lenc,
                    lenb,
                },
            );
        }

        Ok(())
    }
}
