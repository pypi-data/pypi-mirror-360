"""
File operation benchmarks: raidx vs pyfaidx direct comparisons.

Tests realistic file operations that matter in real-world usage.
"""

import pytest


class TestFileOperations:
    """Direct comparison benchmarks for file operations."""

    @pytest.mark.parametrize("library", ["raidx", "pyfaidx"])
    def test_file_opening_medium(self, benchmark, sample_fasta_medium, library):
        """Compare file opening performance: raidx vs pyfaidx."""
        if library == "raidx":
            try:
                import raidx as lib
            except ImportError:
                pytest.skip("raidx not available")
        else:
            try:
                import pyfaidx as lib
            except ImportError:
                pytest.skip("pyfaidx not available")
        
        def open_and_validate():
            fa = lib.Fasta(sample_fasta_medium)
            # Validate by accessing key count (realistic check)
            return len(list(fa.keys()))
        
        result = benchmark(open_and_validate)
        assert result > 0

    @pytest.mark.parametrize("library", ["raidx", "pyfaidx"])
    def test_sequence_listing_medium(self, benchmark, sample_fasta_medium, library):
        """Compare sequence name listing: raidx vs pyfaidx."""
        if library == "raidx":
            try:
                import raidx as lib
            except ImportError:
                pytest.skip("raidx not available")
        else:
            try:
                import pyfaidx as lib
            except ImportError:
                pytest.skip("pyfaidx not available")
        
        fa = lib.Fasta(sample_fasta_medium)
        
        def list_all_sequences():
            # Convert to list to force full evaluation
            return list(fa.keys())
        
        result = benchmark(list_all_sequences)
        assert len(result) > 0

    @pytest.mark.parametrize("library", ["raidx", "pyfaidx"])
    @pytest.mark.slow
    def test_file_opening_large(self, benchmark, sample_fasta_large, library):
        """Compare file opening with large files: raidx vs pyfaidx."""
        if library == "raidx":
            try:
                import raidx as lib
            except ImportError:
                pytest.skip("raidx not available")
        else:
            try:
                import pyfaidx as lib
            except ImportError:
                pytest.skip("pyfaidx not available")
        
        def open_and_validate():
            fa = lib.Fasta(sample_fasta_large)
            # Realistic validation - check first few sequences exist
            keys = list(fa.keys())
            return len(keys)
        
        result = benchmark(open_and_validate)
        assert result > 0 