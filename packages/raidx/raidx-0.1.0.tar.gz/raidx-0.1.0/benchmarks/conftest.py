"""
Pytest configuration and fixtures for benchmarks.
"""

import os
import tempfile
import random
from pathlib import Path
import pytest


@pytest.fixture(scope="session")
def sample_fasta_small():
    """Create a small sample FASTA file for quick benchmarks."""
    return create_sample_fasta(num_sequences=5, seq_length=2000, name_suffix="small")


@pytest.fixture(scope="session")
def sample_fasta_medium():
    """Create a medium sample FASTA file for standard benchmarks."""
    return create_sample_fasta(num_sequences=20, seq_length=5000, name_suffix="medium")


@pytest.fixture(scope="session")
def sample_fasta_large():
    """Create a large sample FASTA file for performance benchmarks."""
    return create_sample_fasta(num_sequences=50, seq_length=10000, name_suffix="large")


def create_sample_fasta(num_sequences: int, seq_length: int, name_suffix: str) -> str:
    """Create a sample FASTA file for benchmarking."""
    bases = ['A', 'T', 'G', 'C']
    
    # Create in benchmarks/data directory
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    filename = data_dir / f"sample_{name_suffix}.fasta"
    
    # Only create if it doesn't exist
    if filename.exists():
        return str(filename)
    
    with open(filename, 'w') as f:
        for i in range(num_sequences):
            # Write header
            f.write(f">sequence_{i+1}_{name_suffix} Sample sequence {i+1}\n")
            
            # Write sequence in lines of 80 characters
            sequence = ''.join(random.choice(bases) for _ in range(seq_length))
            for j in range(0, len(sequence), 80):
                f.write(sequence[j:j+80] + '\n')
    
    return str(filename)


@pytest.fixture(scope="session")
def raidx_available():
    """Check if raidx is available for testing."""
    try:
        import raidx
        return True
    except ImportError:
        return False


@pytest.fixture(scope="session")
def pyfaidx_available():
    """Check if pyfaidx is available for testing."""
    try:
        import pyfaidx
        return True
    except ImportError:
        return False


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add benchmark marker to all benchmark functions
        if "benchmark" in item.name:
            item.add_marker(pytest.mark.benchmark)
        
        # Add slow marker to large data tests
        if "large" in item.name:
            item.add_marker(pytest.mark.slow)


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "benchmark: mark test as a benchmark"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    ) 