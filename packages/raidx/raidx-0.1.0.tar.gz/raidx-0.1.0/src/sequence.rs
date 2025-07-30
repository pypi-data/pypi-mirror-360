use pyo3::prelude::*;
use pyo3::types::PySlice;
// use std::collections::HashMap; // temporarily unused due to disabled array interface

// Pre-computed complement lookup table for better performance
static COMPLEMENT_TABLE: [u8; 256] = {
    let mut table = [b'N'; 256];
    table[b'A' as usize] = b'T';
    table[b'T' as usize] = b'A';
    table[b'C' as usize] = b'G';
    table[b'G' as usize] = b'C';
    table[b'a' as usize] = b't';
    table[b't' as usize] = b'a';
    table[b'c' as usize] = b'g';
    table[b'g' as usize] = b'c';
    table[b'N' as usize] = b'N';
    table[b'n' as usize] = b'n';
    table[b'Y' as usize] = b'R';
    table[b'R' as usize] = b'Y';
    table[b'W' as usize] = b'W';
    table[b'S' as usize] = b'S';
    table[b'K' as usize] = b'M';
    table[b'M' as usize] = b'K';
    table[b'D' as usize] = b'H';
    table[b'V' as usize] = b'B';
    table[b'H' as usize] = b'D';
    table[b'B' as usize] = b'V';
    table[b'X' as usize] = b'X';
    table[b'y' as usize] = b'r';
    table[b'r' as usize] = b'y';
    table[b'w' as usize] = b'w';
    table[b's' as usize] = b's';
    table[b'k' as usize] = b'm';
    table[b'm' as usize] = b'k';
    table[b'd' as usize] = b'h';
    table[b'v' as usize] = b'b';
    table[b'h' as usize] = b'd';
    table[b'b' as usize] = b'v';
    table[b'x' as usize] = b'x';
    table
};

#[pyclass]
#[derive(Clone)]
pub struct Sequence {
    #[pyo3(get, set)]
    pub name: String,
    #[pyo3(get, set)]
    pub seq: String,
    #[pyo3(get, set)]
    pub start: Option<usize>,
    #[pyo3(get, set)]
    pub end: Option<usize>,
    #[pyo3(get, set)]
    pub comp: bool,
}

#[pymethods]
impl Sequence {
    #[new]
    #[pyo3(signature = (name="".to_string(), seq="".to_string(), start=None, end=None, comp=false))]
    pub fn new(
        name: String,
        seq: String,
        start: Option<usize>,
        end: Option<usize>,
        comp: bool,
    ) -> Self {
        Self {
            name,
            seq,
            start,
            end,
            comp,
        }
    }

    pub fn __getitem__(&self, key: Bound<PyAny>) -> PyResult<Sequence> {
        if let Ok(slice) = key.downcast::<PySlice>() {
            let seq_len = self.seq.len() as isize;
            let indices = slice.indices(seq_len)?;

            let step = indices.step as isize;
            let (start_idx, end_idx, sliced_seq) = if step == 1 {
                // Optimized normal forward slice - most common case
                let start = if indices.start >= 0 {
                    indices.start as usize
                } else {
                    0
                };
                let end = if indices.stop >= 0 {
                    std::cmp::min(indices.stop as usize, self.seq.len())
                } else {
                    self.seq.len()
                };

                // Use direct byte slicing for maximum performance
                let slice_len = end.saturating_sub(start);
                if start < self.seq.len() && end > start && slice_len > 0 {
                    // Direct byte slice - fastest possible
                    let seq_slice = &self.seq[start..end];
                    (start, end, seq_slice.to_string())
                } else {
                    (start, end, String::new())
                }
            } else if step == -1 {
                // Optimized full reverse slice
                let start = if indices.start >= 0 {
                    std::cmp::min(indices.start as usize, self.seq.len().saturating_sub(1))
                } else {
                    self.seq.len().saturating_sub(1)
                };
                let end = if indices.stop >= 0 {
                    indices.stop as usize
                } else {
                    0
                };

                if start >= end {
                    let actual_end = if end == 0 && indices.stop < 0 {
                        0
                    } else {
                        end + 1
                    };

                    // Optimized reverse using byte operations
                    let slice_bytes = &self.seq.as_bytes()[actual_end..=start];
                    let mut reversed_bytes = Vec::with_capacity(slice_bytes.len());
                    for &byte in slice_bytes.iter().rev() {
                        reversed_bytes.push(byte);
                    }
                    let seq = unsafe { String::from_utf8_unchecked(reversed_bytes) };
                    (actual_end, start + 1, seq)
                } else {
                    (start, start, String::new())
                }
            } else if step > 0 {
                // Forward slice with step - optimized
                let start = if indices.start >= 0 {
                    indices.start as usize
                } else {
                    0
                };
                let end = if indices.stop >= 0 {
                    std::cmp::min(indices.stop as usize, self.seq.len())
                } else {
                    self.seq.len()
                };

                if start < end {
                    let slice_bytes = &self.seq.as_bytes()[start..end];
                    let mut result_bytes = Vec::new();
                    let mut i = 0;
                    while i < slice_bytes.len() {
                        result_bytes.push(slice_bytes[i]);
                        i += step as usize;
                    }
                    let seq = unsafe { String::from_utf8_unchecked(result_bytes) };
                    (start, end, seq)
                } else {
                    (start, end, String::new())
                }
            } else {
                // Negative step (other than -1) - optimized
                let start = if indices.start >= 0 {
                    std::cmp::min(indices.start as usize, self.seq.len().saturating_sub(1))
                } else {
                    self.seq.len().saturating_sub(1)
                };
                let end = if indices.stop >= 0 {
                    indices.stop as usize
                } else {
                    0
                };

                if start >= end {
                    let actual_end = if end == 0 && indices.stop < 0 {
                        0
                    } else {
                        end + 1
                    };

                    let slice_bytes = &self.seq.as_bytes()[actual_end..=start];
                    let mut result_bytes = Vec::new();
                    let mut i = slice_bytes.len();
                    while i > 0 {
                        i -= 1;
                        result_bytes.push(slice_bytes[i]);
                        if i < (-step) as usize {
                            break;
                        }
                        i = i.saturating_sub((-step) as usize - 1);
                    }
                    let seq = unsafe { String::from_utf8_unchecked(result_bytes) };
                    (actual_end, start + 1, seq)
                } else {
                    (start, start, String::new())
                }
            };

            // Calculate new coordinates
            let (new_start, new_end) =
                if let (Some(orig_start), Some(_orig_end)) = (self.start, self.end) {
                    if step < 0 {
                        // For reverse, swap and adjust coordinates
                        (Some(orig_start + start_idx), Some(orig_start + end_idx - 1))
                    } else {
                        (Some(orig_start + start_idx), Some(orig_start + end_idx - 1))
                    }
                } else {
                    (None, None)
                };

            Ok(Sequence::new(
                self.name.clone(),
                sliced_seq,
                new_start,
                new_end,
                self.comp,
            ))
        } else if let Ok(index) = key.extract::<isize>() {
            let seq_len = self.seq.len() as isize;
            let idx = if index < 0 {
                (seq_len + index) as usize
            } else {
                index as usize
            };

            if idx < self.seq.len() {
                // Fast single character access using byte indexing
                let byte = self.seq.as_bytes()[idx];
                let c = char::from(byte);
                let pos = if let Some(start) = self.start {
                    Some(start + idx)
                } else {
                    None
                };
                Ok(Sequence::new(
                    self.name.clone(),
                    c.to_string(),
                    pos,
                    pos,
                    self.comp,
                ))
            } else {
                Err(PyErr::new::<pyo3::exceptions::PyIndexError, _>(
                    "Index out of range",
                ))
            }
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "Invalid index type",
            ))
        }
    }

    fn __str__(&self) -> String {
        self.seq.clone()
    }

    fn __repr__(&self) -> String {
        format!(">{}\n{}", self.fancy_name(), self.seq)
    }

    fn __len__(&self) -> usize {
        self.seq.len()
    }

    fn __eq__(&self, other: Bound<PyAny>) -> bool {
        if let Ok(other_str) = other.extract::<String>() {
            self.seq == other_str
        } else if let Ok(other_seq) = other.extract::<PyRef<Sequence>>() {
            self.seq == other_seq.seq
        } else {
            false
        }
    }

    pub fn __neg__(&self) -> Sequence {
        // Ultra-optimized reverse complement using byte operations
        let bytes = self.seq.as_bytes();
        let mut result_bytes = Vec::with_capacity(bytes.len());

        for &byte in bytes.iter().rev() {
            result_bytes.push(COMPLEMENT_TABLE[byte as usize]);
        }

        let result = unsafe { String::from_utf8_unchecked(result_bytes) };

        let (start, end) = if let (Some(s), Some(e)) = (self.start, self.end) {
            (Some(e), Some(s))
        } else {
            (self.start, self.end)
        };

        Sequence::new(self.name.clone(), result, start, end, !self.comp)
    }

    #[getter]
    fn fancy_name(&self) -> String {
        let mut name = self.name.clone();
        if let (Some(start), Some(end)) = (self.start, self.end) {
            name = format!("{}:{}-{}", name, start, end);
        }
        if self.comp {
            name += " (complement)";
        }
        name
    }

    // Deprecated - kept for compatibility
    #[getter]
    fn long_name(&self) -> String {
        self.fancy_name()
    }

    #[getter]
    fn complement(&self) -> Sequence {
        let comp_seq = complement_sequence_optimized(&self.seq);
        Sequence {
            name: self.name.clone(),
            seq: comp_seq,
            start: self.start,
            end: self.end,
            comp: !self.comp,
        }
    }

    #[getter]
    pub fn reverse(&self) -> Sequence {
        // Ultra-optimized byte-level reverse
        let bytes = self.seq.as_bytes();
        let mut result_bytes = Vec::with_capacity(bytes.len());

        for &byte in bytes.iter().rev() {
            result_bytes.push(byte);
        }

        let result = unsafe { String::from_utf8_unchecked(result_bytes) };

        let (start, end) = if let (Some(s), Some(e)) = (self.start, self.end) {
            (Some(e), Some(s))
        } else {
            (self.start, self.end)
        };

        Sequence {
            name: self.name.clone(),
            seq: result,
            start,
            end,
            comp: self.comp,
        }
    }

    #[getter]
    fn orientation(&self) -> Option<i8> {
        if let (Some(start), Some(end)) = (self.start, self.end) {
            if start < end && !self.comp {
                Some(1)
            } else if start > end && self.comp {
                Some(-1)
            } else {
                None
            }
        } else {
            None
        }
    }

    #[getter]
    fn gc(&self) -> f64 {
        if self.seq.is_empty() {
            return 0.0;
        }

        // Ultra-optimized byte-level GC counting
        let bytes = self.seq.as_bytes();
        let mut gc_count = 0;

        // Process in chunks of 8 for better performance
        let mut i = 0;
        while i + 8 <= bytes.len() {
            for j in i..i + 8 {
                match bytes[j] {
                    b'G' | b'C' | b'g' | b'c' => gc_count += 1,
                    _ => {}
                }
            }
            i += 8;
        }

        // Process remaining bytes
        while i < bytes.len() {
            match bytes[i] {
                b'G' | b'C' | b'g' | b'c' => gc_count += 1,
                _ => {}
            }
            i += 1;
        }

        gc_count as f64 / bytes.len() as f64
    }

    #[getter]
    fn gc_strict(&self) -> f64 {
        if self.seq.is_empty() {
            return 0.0;
        }

        let bytes = self.seq.as_bytes();
        let mut valid_count = 0;
        let mut gc_count = 0;

        for &byte in bytes {
            match byte {
                b'A' | b'C' | b'G' | b'T' | b'a' | b'c' | b'g' | b't' => {
                    valid_count += 1;
                    if byte == b'G' || byte == b'C' || byte == b'g' || byte == b'c' {
                        gc_count += 1;
                    }
                }
                _ => {}
            }
        }

        if valid_count == 0 {
            0.0
        } else {
            gc_count as f64 / valid_count as f64
        }
    }

    #[getter]
    fn gc_iupac(&self) -> f64 {
        if self.seq.is_empty() {
            return 0.0;
        }

        let mut valid_count = 0;
        let mut gc_content = 0.0;

        for byte in self.seq.as_bytes() {
            let c = (*byte as char).to_ascii_uppercase();
            match c {
                'A' | 'C' | 'G' | 'T' => {
                    valid_count += 1;
                    if c == 'G' || c == 'C' {
                        gc_content += 1.0;
                    }
                }
                'M' | 'R' | 'Y' | 'K' => {
                    valid_count += 1;
                    gc_content += 0.5;
                }
                'S' => {
                    valid_count += 1;
                    gc_content += 1.0;
                }
                'B' | 'V' => {
                    valid_count += 1;
                    gc_content += 0.67;
                }
                'H' | 'D' => {
                    valid_count += 1;
                    gc_content += 0.33;
                }
                'N' => {
                    valid_count += 1;
                    gc_content += 0.25;
                }
                'W' => {
                    valid_count += 1;
                    // W = A or T, so 0.0 GC content
                }
                _ => {}
            }
        }

        if valid_count == 0 {
            0.0
        } else {
            gc_content / valid_count as f64
        }
    }

    // Numpy array interface support (temporarily disabled due to PyO3 0.25 compatibility)
    // #[getter]
    // fn __array_interface__(&self) -> HashMap<String, PyObject> {
    //     Python::with_gil(|py| {
    //         let mut interface = HashMap::new();
    //         interface.insert("shape".to_string(), (self.seq.len(),).into_py(py));
    //         interface.insert("typestr".to_string(), "|S1".into_py(py));
    //         interface.insert("version".to_string(), 3.into_py(py));
    //         // Note: data would need special handling for memoryview
    //         interface
    //     })
    // }
}

fn complement_sequence_optimized(seq: &str) -> String {
    // Ultra-optimized byte-level lookup using pre-allocated vector
    let bytes = seq.as_bytes();
    let mut result_bytes = Vec::with_capacity(bytes.len());

    for &byte in bytes {
        result_bytes.push(COMPLEMENT_TABLE[byte as usize]);
    }

    unsafe { String::from_utf8_unchecked(result_bytes) }
}
