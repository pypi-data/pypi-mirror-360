"""
Sequence operation benchmarks: raidx vs pyfaidx direct comparisons.

Tests realistic sequence operations using workloads that matter in practice.
Matches patterns from the successful standalone benchmark.
"""

import pytest
import random


class TestSequenceOperations:
    """Direct comparison benchmarks for sequence operations."""

    @pytest.mark.parametrize("library", ["raidx", "pyfaidx"])
    def test_sequence_access_realistic(self, benchmark, sample_fasta_medium, library):
        """Compare realistic sequence access: raidx vs pyfaidx."""
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
            # Realistic pattern: access sequence and get length
            seq_record = fa[first_seq]
            return len(seq_record)
        
        result = benchmark(access_sequence)
        assert result > 0

    @pytest.mark.parametrize("library", ["raidx", "pyfaidx"])
    def test_sequence_slicing_100bp(self, benchmark, sample_fasta_medium, library):
        """Compare 100bp sequence slicing: raidx vs pyfaidx."""
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
            # Realistic pattern: 100bp slice (matches standalone benchmark)
            return str(fa[first_seq][1000:1100])
        
        result = benchmark(slice_sequence)
        assert len(result) == 100

    @pytest.mark.parametrize("library", ["raidx", "pyfaidx"])
    def test_get_seq_method(self, benchmark, sample_fasta_medium, library):
        """Compare get_seq method calls: raidx vs pyfaidx."""
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
        
        def get_seq():
            # 1-based inclusive coordinates: 1000-1099 = 100 bases
            return fa.get_seq(first_seq, 1000, 1099)
        
        result = benchmark(get_seq)
        assert len(str(result)) == 100

    @pytest.mark.parametrize("library", ["raidx", "pyfaidx"])
    def test_reverse_complement(self, benchmark, sample_fasta_medium, library):
        """Compare reverse complement operations: raidx vs pyfaidx."""
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
        
        def reverse_complement():
            # Realistic pattern: 100bp reverse complement
            return str(-fa[first_seq][1000:1100])
        
        result = benchmark(reverse_complement)
        assert len(result) == 100

    @pytest.mark.parametrize("library", ["raidx", "pyfaidx"])
    def test_sequence_iteration(self, benchmark, sample_fasta_medium, library):
        """Compare iteration over multiple sequences: raidx vs pyfaidx."""
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
            # Realistic pattern: process first 10 sequences
            total_length = 0
            for seq_name in seq_names[:10]:
                total_length += len(fa[seq_name])
            return total_length
        
        result = benchmark(iterate_sequences)
        assert result > 0

    @pytest.mark.parametrize("library", ["raidx", "pyfaidx"])
    def test_random_access_pattern(self, benchmark, sample_fasta_medium, library):
        """Compare random access patterns: raidx vs pyfaidx."""
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
        
        # Pre-generate random access pattern (matches standalone benchmark)
        random.seed(42)  # Consistent results
        random_accesses = []
        for _ in range(50):  # 50 random accesses
            seq_name = random.choice(seq_names)
            start = random.randint(100, 3000)
            end = start + 100  # 100bp slices
            random_accesses.append((seq_name, start, end))
        
        def random_access():
            total_length = 0
            for seq_name, start, end in random_accesses:
                total_length += len(fa[seq_name][start:end])
            return total_length
        
        result = benchmark(random_access)
        assert result > 0

    @pytest.mark.parametrize("library", ["raidx", "pyfaidx"])
    def test_multiple_operations_workflow(self, benchmark, sample_fasta_medium, library):
        """Compare realistic multi-operation workflow: raidx vs pyfaidx."""
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
        
        def workflow():
            # Realistic workflow: multiple operations in sequence
            # 1. Get sequence length
            seq_len = len(fa[first_seq])
            
            # 2. Extract region
            region = str(fa[first_seq][1000:1500])  # 500bp region
            
            # 3. Get reverse complement of a portion
            rev_comp = str(-fa[first_seq][1200:1300])  # 100bp rev comp
            
            # 4. Use get_seq method
            precise = fa.get_seq(first_seq, 1500, 1599)  # 100bp
            
            return seq_len + len(region) + len(rev_comp) + len(str(precise))
        
        result = benchmark(workflow)
        assert result > 0 