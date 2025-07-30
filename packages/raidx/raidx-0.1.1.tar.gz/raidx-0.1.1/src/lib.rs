mod errors;
mod faidx;
mod sequence;

use faidx::Faidx;
use pyo3::prelude::*;
use pyo3::types::PySlice;
use sequence::Sequence;

#[pyclass]
pub struct Fasta {
    #[pyo3(get)]
    filename: String,
    faidx: Faidx,
    mutable: bool,
}

#[pymethods]
impl Fasta {
    #[new]
    #[pyo3(signature = (
        filename,
        indexname=None,
        default_seq=None,
        key_function=None,
        as_raw=false,
        strict_bounds=false,
        read_ahead=None,
        mutable=false,
        split_char=None,
        filt_function=None,
        one_based_attributes=true,
        read_long_names=false,
        duplicate_action="stop".to_string(),
        sequence_always_upper=false,
        rebuild=true,
        build_index=true
    ))]
    fn new(
        filename: String,
        indexname: Option<String>,
        default_seq: Option<String>,
        key_function: Option<PyObject>,
        as_raw: bool,
        strict_bounds: bool,
        read_ahead: Option<usize>,
        mutable: bool,
        split_char: Option<String>,
        filt_function: Option<PyObject>,
        one_based_attributes: bool,
        read_long_names: bool,
        duplicate_action: String,
        sequence_always_upper: bool,
        rebuild: bool,
        build_index: bool,
    ) -> PyResult<Self> {
        let faidx = Faidx::new(
            filename.clone(),
            indexname,
            as_raw,
            strict_bounds,
            sequence_always_upper,
            rebuild,
            build_index,
            one_based_attributes,
            default_seq,
            mutable,
            key_function,
            split_char,
            filt_function,
            read_long_names,
            duplicate_action,
            read_ahead,
        )?;

        Ok(Fasta {
            filename,
            faidx,
            mutable,
        })
    }

    fn __repr__(&self) -> String {
        format!("Fasta(\"{}\")", self.filename)
    }

    fn __getitem__(&self, key: Bound<PyAny>) -> PyResult<FastaRecord> {
        if let Ok(name) = key.extract::<String>() {
            if self.faidx.__contains__(name.clone()) {
                Ok(FastaRecord::new(name, &self.faidx, self.mutable))
            } else {
                Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                    "{} not in {}.",
                    name, self.filename
                )))
            }
        } else if let Ok(index) = key.extract::<usize>() {
            let keys = self.faidx.keys();
            if index < keys.len() {
                let name = keys[index].clone();
                Ok(FastaRecord::new(name, &self.faidx, self.mutable))
            } else {
                Err(PyErr::new::<pyo3::exceptions::PyIndexError, _>(
                    "Index out of range",
                ))
            }
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "Key must be string or integer",
            ))
        }
    }

    fn __contains__(&self, name: String) -> bool {
        self.faidx.__contains__(name)
    }

    fn __len__(&self) -> usize {
        self.faidx
            .keys()
            .iter()
            .map(|name| self.faidx.get_sequence_length(name).unwrap_or(0))
            .sum()
    }

    fn __iter__(slf: PyRef<Self>) -> PyResult<FastaIterator> {
        let keys = slf.faidx.keys();
        Ok(FastaIterator::new(keys, &slf.faidx, slf.mutable))
    }

    fn keys(&self) -> Vec<String> {
        self.faidx.keys()
    }

    fn values(&self) -> PyResult<Vec<FastaRecord>> {
        let mut records = Vec::new();
        for name in self.faidx.keys() {
            records.push(FastaRecord::new(name, &self.faidx, self.mutable));
        }
        Ok(records)
    }

    fn items(&self) -> PyResult<Vec<(String, FastaRecord)>> {
        let mut items = Vec::new();
        for name in self.faidx.keys() {
            let record = FastaRecord::new(name.clone(), &self.faidx, self.mutable);
            items.push((name, record));
        }
        Ok(items)
    }

    #[pyo3(signature = (name, start, end, rc=None))]
    fn get_seq(
        &self,
        name: String,
        start: usize,
        end: usize,
        rc: Option<bool>,
    ) -> PyResult<Sequence> {
        let seq = self.faidx.fetch(name, start, end)?;
        if rc.unwrap_or(false) {
            Ok(seq.__neg__())
        } else {
            Ok(seq)
        }
    }

    #[pyo3(signature = (name, intervals, rc=None))]
    fn get_spliced_seq(
        &self,
        name: String,
        intervals: Vec<(usize, usize)>,
        rc: Option<bool>,
    ) -> PyResult<Sequence> {
        let mut chunks = Vec::new();
        for (start, end) in intervals {
            chunks.push(self.faidx.fetch(name.clone(), start, end)?);
        }

        let mut seq_parts = Vec::new();
        let start = if !chunks.is_empty() {
            chunks[0].start
        } else {
            None
        };
        let end = if !chunks.is_empty() {
            chunks.last().unwrap().end
        } else {
            None
        };

        if rc.unwrap_or(false) {
            for chunk in chunks.iter().rev() {
                seq_parts.push(chunk.__neg__().seq);
            }
        } else {
            for chunk in chunks {
                seq_parts.push(chunk.seq);
            }
        }

        Ok(Sequence::new(name, seq_parts.join(""), start, end, false))
    }

    /// High-performance batch fetch for many sequences
    ///
    /// This method is optimized for genomics workloads where you need to fetch
    /// many sequences at once (e.g., 200,000+ regions). It uses parallel processing
    /// and optimized memory access patterns for maximum throughput.
    ///
    /// Args:
    ///     regions: List of (name, start, end) tuples specifying regions to fetch
    ///     rc: Optional boolean to reverse complement all sequences
    ///
    /// Returns:
    ///     List of Sequence objects in the same order as input regions
    ///
    /// Example:
    ///     >>> regions = [("chr1", 1000, 2000), ("chr2", 5000, 6000)]
    ///     >>> sequences = fasta.fetch_many(regions)
    #[pyo3(signature = (regions, rc=None))]
    fn fetch_many(
        &self,
        regions: Vec<(String, usize, usize)>,
        rc: Option<bool>,
    ) -> PyResult<Vec<Sequence>> {
        let mut sequences = self.faidx.fetch_many(regions)?;

        if rc.unwrap_or(false) {
            sequences = sequences.into_iter().map(|seq| seq.__neg__()).collect();
        }

        Ok(sequences)
    }

    /// Ultra-fast batch fetch for regions from the same chromosome
    ///
    /// This method is optimized for BED file processing where many regions
    /// come from the same chromosome. It's significantly faster than fetch_many
    /// when all regions are from the same chromosome.
    ///
    /// Args:
    ///     name: Chromosome/sequence name
    ///     regions: List of (start, end) tuples
    ///     rc: Optional boolean to reverse complement all sequences
    ///
    /// Returns:
    ///     List of Sequence objects in the same order as input regions
    ///
    /// Example:
    ///     >>> regions = [(1000, 2000), (5000, 6000), (10000, 11000)]
    ///     >>> sequences = fasta.fetch_many_same_chr("chr1", regions)
    #[pyo3(signature = (name, regions, rc=None))]
    fn fetch_many_same_chr(
        &self,
        name: String,
        regions: Vec<(usize, usize)>,
        rc: Option<bool>,
    ) -> PyResult<Vec<Sequence>> {
        let mut sequences = self.faidx.fetch_many_same_chr(name, regions)?;

        if rc.unwrap_or(false) {
            sequences = sequences.into_iter().map(|seq| seq.__neg__()).collect();
        }

        Ok(sequences)
    }

    fn close(&self) {
        // Implementation for closing file handles
    }

    fn __enter__(slf: PyRef<Self>) -> Py<Self> {
        slf.into()
    }

    #[pyo3(signature = (_exc_type=None, _exc_value=None, _traceback=None))]
    fn __exit__(
        &self,
        _exc_type: Option<Bound<PyAny>>,
        _exc_value: Option<Bound<PyAny>>,
        _traceback: Option<Bound<PyAny>>,
    ) {
        self.close();
    }
}

#[pyclass]
pub struct FastaRecord {
    #[pyo3(get)]
    name: String,
    faidx_ptr: *const Faidx,
    // Note: mutable functionality not yet implemented
    _mutable: bool,
}

unsafe impl Send for FastaRecord {}
unsafe impl Sync for FastaRecord {}

impl FastaRecord {
    fn new(name: String, faidx: &Faidx, mutable: bool) -> Self {
        Self {
            name,
            faidx_ptr: faidx as *const Faidx,
            _mutable: mutable,
        }
    }

    fn get_faidx(&self) -> &Faidx {
        unsafe { &*self.faidx_ptr }
    }
}

#[pymethods]
impl FastaRecord {
    fn __repr__(&self) -> String {
        format!("FastaRecord(\"{}\")", self.name)
    }

    fn __getitem__(&self, key: Bound<PyAny>) -> PyResult<Sequence> {
        if let Ok(slice) = key.downcast::<PySlice>() {
            let length = self.__len__();
            let faidx = self.get_faidx();

            // Ultra-fast path: Check slice attributes first for [:] pattern
            let start_obj = slice.getattr("start")?;
            let stop_obj = slice.getattr("stop")?;
            let step_obj = slice.getattr("step")?;

            // Check if this is a full sequence slice ([:] or [::1])
            if start_obj.is_none()
                && stop_obj.is_none()
                && (step_obj.is_none() || step_obj.extract::<isize>().unwrap_or(1) == 1)
            {
                // Direct fetch of entire sequence - absolute fastest path
                return faidx.fetch_entire_sequence(self.name.clone());
            }

            // Secondary fast path: Check for explicit full range [0:length:1]
            if let (Ok(start_val), Ok(stop_val), Ok(step_val)) = (
                start_obj.extract::<isize>(),
                stop_obj.extract::<isize>(),
                step_obj.extract::<isize>(),
            ) {
                if start_val == 0 && stop_val == length as isize && step_val == 1 {
                    return faidx.fetch_entire_sequence(self.name.clone());
                }
            }

            // For all other cases, use the existing optimized logic
            let indices = slice.indices(length as isize)?;
            let step = indices.step;

            if step == 1 {
                // Optimized normal forward slice
                let start = if indices.start >= 0 {
                    indices.start as usize + 1
                } else {
                    1
                };
                let stop = if indices.stop >= 0 {
                    if faidx.strict_bounds {
                        // Don't clamp when strict bounds is enabled
                        indices.stop as usize
                    } else {
                        // Clamp to sequence length when strict bounds is disabled
                        std::cmp::min(indices.stop as usize, length)
                    }
                } else {
                    length
                };

                // Direct fetch - most efficient path
                faidx.fetch(self.name.clone(), start, stop)
            } else {
                // For complex slicing, use the existing slower path
                if faidx.strict_bounds {
                    let start = if indices.start >= 0 {
                        indices.start as usize + 1
                    } else {
                        if step < 0 {
                            length
                        } else {
                            1
                        }
                    };
                    let stop = if indices.stop >= 0 {
                        indices.stop as usize
                    } else {
                        if step < 0 {
                            1
                        } else {
                            length
                        }
                    };

                    let (fetch_start, fetch_stop) = if step < 0 {
                        (std::cmp::min(start, stop), std::cmp::max(start, stop))
                    } else {
                        (start, stop)
                    };

                    let full_seq = faidx.fetch(self.name.clone(), fetch_start, fetch_stop)?;
                    full_seq.__getitem__(slice.clone().into_any())
                } else {
                    let start = if indices.start >= 0 {
                        std::cmp::max(1, std::cmp::min(indices.start as usize + 1, length))
                    } else {
                        if step < 0 {
                            length
                        } else {
                            1
                        }
                    };
                    let stop = if indices.stop >= 0 {
                        std::cmp::max(1, std::cmp::min(indices.stop as usize, length))
                    } else {
                        if step < 0 {
                            1
                        } else {
                            length
                        }
                    };

                    let (fetch_start, fetch_stop) = if step < 0 {
                        (std::cmp::min(start, stop), std::cmp::max(start, stop))
                    } else {
                        (start, stop)
                    };

                    let full_seq = faidx.fetch(self.name.clone(), fetch_start, fetch_stop)?;
                    full_seq.__getitem__(slice.clone().into_any())
                }
            }
        } else if let Ok(index) = key.extract::<isize>() {
            let length = self.__len__() as isize;
            let pos = if index < 0 {
                (length + index + 1) as usize
            } else {
                (index + 1) as usize
            };
            self.get_faidx().fetch(self.name.clone(), pos, pos)
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "Invalid index type",
            ))
        }
    }

    fn __len__(&self) -> usize {
        self.get_faidx()
            .get_sequence_length(&self.name)
            .unwrap_or(0)
    }

    fn __str__(&self) -> PyResult<String> {
        let seq = self
            .get_faidx()
            .fetch(self.name.clone(), 1, self.__len__())?;
        Ok(seq.seq)
    }

    fn __iter__(slf: PyRef<Self>) -> PyResult<SequenceIterator> {
        let faidx = slf.get_faidx();
        let line_len = faidx.get_line_length(&slf.name).unwrap_or(70);
        let total_len = slf.__len__();
        Ok(SequenceIterator::new(
            slf.name.clone(),
            slf.faidx_ptr,
            line_len,
            total_len,
        ))
    }

    fn __reversed__(&self) -> PyResult<Vec<Sequence>> {
        let faidx = self.get_faidx();
        let line_len = faidx.get_line_length(&self.name).unwrap_or(70);
        let mut lines = Vec::new();
        let total_len = self.__len__();
        let mut start = 1;

        while start <= total_len {
            let end = std::cmp::min(start + line_len - 1, total_len);
            let seq = faidx.fetch(self.name.clone(), start, end)?;
            lines.push(seq);
            start = end + 1;
        }

        let mut reversed_lines = Vec::new();
        for line in lines.iter().rev() {
            let rev_seq = line.reverse();
            reversed_lines.push(rev_seq);
        }

        Ok(reversed_lines)
    }

    #[getter]
    fn long_name(&self) -> PyResult<String> {
        self.get_faidx().get_long_name(&self.name)
    }

    #[getter]
    fn unpadded_len(&self) -> PyResult<usize> {
        let full_seq = self
            .get_faidx()
            .fetch(self.name.clone(), 1, self.__len__())?;
        let mut length = full_seq.seq.len();

        // Count N's from the beginning
        for c in full_seq.seq.chars() {
            if c.to_ascii_uppercase() == 'N' {
                length -= 1;
            } else {
                break;
            }
        }

        // Count N's from the end
        for c in full_seq.seq.chars().rev() {
            if c.to_ascii_uppercase() == 'N' {
                length -= 1;
            } else {
                break;
            }
        }

        Ok(length)
    }
}

#[pyclass]
pub struct FastaIterator {
    keys: Vec<String>,
    index: usize,
    faidx_ptr: *const Faidx,
    _mutable: bool,
}

#[pymethods]
impl FastaIterator {
    fn __iter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }

    fn __next__(&mut self) -> Option<FastaRecord> {
        if self.index < self.keys.len() {
            let name = self.keys[self.index].clone();
            self.index += 1;
            let faidx = unsafe { &*self.faidx_ptr };
            Some(FastaRecord::new(name, faidx, self._mutable))
        } else {
            None
        }
    }
}

impl FastaIterator {
    fn new(keys: Vec<String>, faidx: &Faidx, mutable: bool) -> Self {
        Self {
            keys,
            index: 0,
            faidx_ptr: faidx as *const Faidx,
            _mutable: mutable,
        }
    }
}

unsafe impl Send for FastaIterator {}
unsafe impl Sync for FastaIterator {}

#[pyclass]
pub struct SequenceIterator {
    name: String,
    faidx_ptr: *const Faidx,
    line_len: usize,
    total_len: usize,
    current_start: usize,
}

#[pymethods]
impl SequenceIterator {
    fn __iter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }

    fn __next__(&mut self) -> PyResult<Option<Sequence>> {
        if self.current_start > self.total_len {
            return Ok(None);
        }

        let end = std::cmp::min(self.current_start + self.line_len - 1, self.total_len);
        let faidx = unsafe { &*self.faidx_ptr };
        let seq = faidx.fetch(self.name.clone(), self.current_start, end)?;
        self.current_start = end + 1;
        Ok(Some(seq))
    }
}

impl SequenceIterator {
    fn new(name: String, faidx_ptr: *const Faidx, line_len: usize, total_len: usize) -> Self {
        Self {
            name,
            faidx_ptr,
            line_len,
            total_len,
            current_start: 1,
        }
    }
}

unsafe impl Send for SequenceIterator {}
unsafe impl Sync for SequenceIterator {}

// For mutable FASTA records
#[pyclass]
pub struct MutableFastaRecord;

#[pymethods]
impl MutableFastaRecord {
    fn __setitem__(&self, _key: Bound<PyAny>, _value: String) -> PyResult<()> {
        // Implementation for mutable setitem
        Err(PyErr::new::<pyo3::exceptions::PyNotImplementedError, _>(
            "Mutable FASTA records not yet implemented",
        ))
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn raidx(_py: Python, m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<Fasta>()?;
    m.add_class::<Faidx>()?;
    m.add_class::<Sequence>()?;
    m.add_class::<FastaRecord>()?;
    m.add_class::<FastaIterator>()?;
    m.add_class::<SequenceIterator>()?;
    m.add_class::<MutableFastaRecord>()?;
    Ok(())
}
