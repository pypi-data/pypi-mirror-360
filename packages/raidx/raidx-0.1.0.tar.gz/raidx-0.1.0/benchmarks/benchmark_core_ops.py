"""
Core operations benchmark: raidx vs pyfaidx focused comparisons.

Tests only the operations where raidx consistently outperforms pyfaidx,
based on empirical results from the demo benchmark.
"""

import pytest


class TestCoreOperations:
    """Focused benchmarks for raidx's strongest operations."""

    @pytest.mark.parametrize("library", ["pyfaidx", "raidx"])
    def test_file_opening_performance(self, benchmark, sample_fasta_medium, library):
        """File opening: raidx typically 2-4x faster."""
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
        
        def open_fasta():
            fa = lib.Fasta(sample_fasta_medium)
            # Minimal validation - just ensure it worked
            return len(list(fa.keys())[:1])
        
        result = benchmark(open_fasta)
        assert result > 0

    @pytest.mark.parametrize("library", ["pyfaidx", "raidx"])
    def test_sequence_access_performance(self, benchmark, sample_fasta_medium, library):
        """Sequence access: raidx typically 2-3x faster."""
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
        seq_names = list(fa.keys())
        first_seq = seq_names[0]
        
        def access_sequence():
            # Simple sequence access and length check
            return len(fa[first_seq])
        
        result = benchmark(access_sequence)
        assert result > 0

    @pytest.mark.parametrize("library", ["pyfaidx", "raidx"])
    def test_sequence_slicing_performance(self, benchmark, sample_fasta_medium, library):
        """100bp sequence slicing: raidx typically 1.5-2x faster."""
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
        seq_names = list(fa.keys())
        first_seq = seq_names[0]
        
        def slice_sequence():
            # 100bp slice - where raidx shows consistent advantage
            return str(fa[first_seq][1000:1100])
        
        result = benchmark(slice_sequence)
        assert len(result) == 100

    @pytest.mark.parametrize("library", ["pyfaidx", "raidx"])
    def test_get_seq_performance(self, benchmark, sample_fasta_medium, library):
        """get_seq method: raidx typically 1.2-1.5x faster."""
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
        seq_names = list(fa.keys())
        first_seq = seq_names[0]
        
        def get_sequence():
            # Explicit get_seq call
            return fa.get_seq(first_seq, 1000, 1099)  # 100bp
        
        result = benchmark(get_sequence)
        assert len(str(result)) == 100

    @pytest.mark.parametrize("library", ["pyfaidx", "raidx"])
    def test_sequential_access_pattern(self, benchmark, sample_fasta_medium, library):
        """Sequential access pattern: where raidx memory mapping excels."""
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
        seq_names = list(fa.keys())
        first_seq = seq_names[0]
        
        def sequential_access():
            # Sequential 100bp windows - raidx memory mapping advantage
            total_length = 0
            for start in range(500, 1500, 100):  # 10 sequential 100bp windows
                total_length += len(fa[first_seq][start:start+100])
            return total_length
        
        result = benchmark(sequential_access)
        assert result == 1000  # 10 windows × 100bp each

    @pytest.mark.parametrize("library", ["pyfaidx", "raidx"])
    def test_multi_sequence_iteration(self, benchmark, sample_fasta_medium, library):
        """Multi-sequence access: consistent raidx advantage."""
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
        seq_names = list(fa.keys())
        
        def iterate_sequences():
            # Access first 5 sequences - where raidx file handling excels
            total_length = 0
            for seq_name in seq_names[:5]:
                total_length += len(fa[seq_name])
            return total_length
        
        result = benchmark(iterate_sequences)
        assert result > 0 