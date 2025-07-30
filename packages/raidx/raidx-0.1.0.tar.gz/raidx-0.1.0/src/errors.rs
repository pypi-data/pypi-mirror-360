use pyo3::{exceptions::PyException, PyErr};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum FaidxError {
    #[error("FASTA file not found: {0}")]
    FastaNotFound(String),

    #[error("Index file not found: {0}")]
    IndexNotFound(String),

    #[error("Fetch error: {0}")]
    FetchError(String),

    #[error("Indexing error: {0}")]
    IndexingError(String),

    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),

    #[error("Invalid region: {0}")]
    InvalidRegion(String),
}

impl From<FaidxError> for PyErr {
    fn from(err: FaidxError) -> PyErr {
        match err {
            FaidxError::FastaNotFound(msg) => {
                PyException::new_err(format!("FastaNotFoundError: {}", msg))
            }
            FaidxError::IndexNotFound(msg) => {
                PyException::new_err(format!("IndexNotFoundError: {}", msg))
            }
            FaidxError::FetchError(msg) => PyException::new_err(format!("FetchError: {}", msg)),
            FaidxError::IndexingError(msg) => {
                PyException::new_err(format!("FastaIndexingError: {}", msg))
            }
            FaidxError::IoError(err) => PyException::new_err(format!("IOError: {}", err)),
            FaidxError::InvalidRegion(msg) => PyException::new_err(format!("RegionError: {}", msg)),
        }
    }
}

pub type Result<T> = std::result::Result<T, FaidxError>;
