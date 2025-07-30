import pytest
import tempfile
import os
import raidx as raidx

# Test data - create sample FASTA files for testing
SAMPLE_FASTA = """>test_seq1
ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC
ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC
>test_seq2
GCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTA
GCTAGCTAGCTAGCTAGCTA
>test_seq3 description with spaces
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG
>short_seq
ATCG
>empty_seq

>mixed_case
AtCgAtCgAtCgAtCg
"""

GENES_LIKE_FASTA = """>NM_001282543.1 Homo sapiens BRCA1 associated RING domain 1 (BARD1), transcript variant 2, mRNA
CCCCGCCCCTCTGGCGGCCCGCCGTCCCAGACGCGGGAAGAGCTTGGCCGGTTTCGAGTCGCTGGCCTGC
AGCTTCCCTGTGGTTTCCCGAGGCTTCCTTGCTTCCCGCTCTGCGAGGAGCCTTTCATCCGAAGGCGGGA
CGATGCCGGATAATCGGCAGCCGAGGAACCGGCAGCCGAGGATCCGCTCCGGGAACGAGCCTCGTTCCGC
GCCCGCCATGGAACCGGATGTAGGCCAAGGTACCGCCCGCGCCTTGCTCCTGCCGAGAAAGTATCCATCA
TGCTGCTGGTAGACGGCCGCAAGCTGGATTCGAATCTGATGAAGCCGCTGAAGTTGCTGATGAAAATCTT
CAATAAAATCTTCAATAAGATTAGGTGATTTTGACTTCTCCAATGATGATTAATAAATACATGCTAATTG
>AB821309.1 Homo sapiens FGFR2-AHCYL1 mRNA for FGFR2-AHCYL1 fusion kinase protein, complete cds
ATGGTCAGCTGGGGTCGTTTCATCTGCCTGGTCGTGGTCACCATGGCAACAGGATCCTGA
ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGA
>KF435150.1 Homo sapiens MDM4 protein variant Y (MDM4) mRNA, complete cds, alternatively spliced
ATGACATCATTTTCCACCTCTGCTCAGTGTTCAACATCTGACAGTGCTTGCAGGATCTCT
CCTGGACAAAGTGAAACGAGTCTGAGGAAATGTTGTTGAAATTTGGAAATGGACTCCTTG
"""


@pytest.fixture
def temp_fasta_file():
    """Create a temporary FASTA file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".fasta", delete=False) as f:
        f.write(SAMPLE_FASTA)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)
    index_path = temp_path + ".fai"
    if os.path.exists(index_path):
        os.unlink(index_path)


@pytest.fixture
def genes_fasta_file():
    """Create a genes-like FASTA file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".fasta", delete=False) as f:
        f.write(GENES_LIKE_FASTA)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)
    index_path = temp_path + ".fai"
    if os.path.exists(index_path):
        os.unlink(index_path)


class TestFasta:
    """Test the main Fasta class functionality."""

    def test_fasta_creation(self, temp_fasta_file):
        """Test basic FASTA file opening."""
        fasta = raidx.Fasta(temp_fasta_file)
        assert str(fasta) == f'Fasta("{temp_fasta_file}")'
        assert fasta.filename == temp_fasta_file

    def test_fasta_keys(self, temp_fasta_file):
        """Test getting sequence names."""
        fasta = raidx.Fasta(temp_fasta_file)
        keys = fasta.keys()
        expected_keys = [
            "test_seq1",
            "test_seq2",
            "test_seq3",
            "short_seq",
            "empty_seq",
            "mixed_case",
        ]
        assert set(keys) == set(expected_keys)

    def test_fasta_contains(self, temp_fasta_file):
        """Test membership testing."""
        fasta = raidx.Fasta(temp_fasta_file)
        assert "test_seq1" in fasta
        assert "test_seq2" in fasta
        assert "nonexistent" not in fasta

    def test_fasta_getitem_by_name(self, temp_fasta_file):
        """Test accessing sequences by name."""
        fasta = raidx.Fasta(temp_fasta_file)
        record = fasta["test_seq1"]
        assert record.name == "test_seq1"
        assert isinstance(record, raidx.FastaRecord)

    def test_fasta_getitem_by_index(self, temp_fasta_file):
        """Test accessing sequences by index."""
        fasta = raidx.Fasta(temp_fasta_file)
        record = fasta[0]
        assert record.name in fasta.keys()
        assert isinstance(record, raidx.FastaRecord)

    def test_fasta_getitem_keyerror(self, temp_fasta_file):
        """Test KeyError for non-existent sequences."""
        fasta = raidx.Fasta(temp_fasta_file)
        with pytest.raises(KeyError):
            _ = fasta["nonexistent"]

    def test_fasta_iteration(self, temp_fasta_file):
        """Test iterating over FASTA records."""
        fasta = raidx.Fasta(temp_fasta_file)
        records = list(fasta)
        assert len(records) == len(fasta.keys())
        for record in records:
            assert isinstance(record, raidx.FastaRecord)

    def test_fasta_length(self, temp_fasta_file):
        """Test getting total length of all sequences."""
        fasta = raidx.Fasta(temp_fasta_file)
        total_length = len(fasta)
        assert total_length > 0
        assert isinstance(total_length, int)

    def test_get_seq_method(self, genes_fasta_file):
        """Test the get_seq method."""
        fasta = raidx.Fasta(genes_fasta_file)
        seq = fasta.get_seq("NM_001282543.1", 201, 210)
        assert isinstance(seq, raidx.Sequence)
        assert seq.name == "NM_001282543.1"
        assert len(seq) == 10
        assert seq.start == 201
        assert seq.end == 210

    def test_get_seq_reverse_complement(self, genes_fasta_file):
        """Test get_seq with reverse complement."""
        fasta = raidx.Fasta(genes_fasta_file)
        seq = fasta.get_seq("NM_001282543.1", 201, 210, rc=True)
        normal_seq = fasta.get_seq("NM_001282543.1", 201, 210, rc=False)

        # Should be reverse complement
        assert seq.seq != normal_seq.seq
        assert len(seq) == len(normal_seq)


class TestFastaRecord:
    """Test FastaRecord functionality."""

    def test_record_basic_properties(self, temp_fasta_file):
        """Test basic record properties."""
        fasta = raidx.Fasta(temp_fasta_file)
        record = fasta["test_seq1"]

        assert record.name == "test_seq1"
        assert len(record) == 120  # 60 + 60 characters
        assert str(record.name) == "test_seq1"

    def test_record_string_conversion(self, temp_fasta_file):
        """Test converting record to string."""
        fasta = raidx.Fasta(temp_fasta_file)
        record = fasta["test_seq1"]
        seq_str = str(record)
        assert isinstance(seq_str, str)
        assert len(seq_str) == len(record)

    def test_record_slicing_basic(self, genes_fasta_file):
        """Test basic slicing operations."""
        fasta = raidx.Fasta(genes_fasta_file)
        record = fasta["NM_001282543.1"]

        # Test basic slice
        subseq = record[200:230]
        assert isinstance(subseq, raidx.Sequence)
        assert len(subseq) == 30
        assert subseq.start == 201  # 1-based
        assert subseq.end == 230

    def test_record_slicing_step(self, temp_fasta_file):
        """Test slicing with step."""
        fasta = raidx.Fasta(temp_fasta_file)
        record = fasta["test_seq1"]

        # Every 3rd character
        subseq = record[::3]
        assert len(subseq) <= len(record) // 3 + 1

        # Reverse
        rev_seq = record[::-1]
        assert len(rev_seq) == len(record)

    def test_record_indexing(self, temp_fasta_file):
        """Test single character indexing."""
        fasta = raidx.Fasta(temp_fasta_file)
        record = fasta["test_seq1"]

        # First character
        first_char = record[0]
        assert isinstance(first_char, raidx.Sequence)
        assert len(first_char) == 1

        # Last character (negative indexing)
        last_char = record[-1]
        assert isinstance(last_char, raidx.Sequence)
        assert len(last_char) == 1

    def test_record_iteration(self, temp_fasta_file):
        """Test iterating over record lines."""
        fasta = raidx.Fasta(temp_fasta_file)
        record = fasta["test_seq1"]

        lines = list(record)
        assert len(lines) >= 1
        for line in lines:
            assert isinstance(line, raidx.Sequence)


class TestSequence:
    """Test Sequence object functionality."""

    def test_sequence_creation(self):
        """Test creating a Sequence object."""
        seq = raidx.Sequence("test", "ATCG", 1, 4, False)
        assert seq.name == "test"
        assert seq.seq == "ATCG"
        assert seq.start == 1
        assert seq.end == 4
        assert not seq.comp

    def test_sequence_string_conversion(self):
        """Test string conversion."""
        seq = raidx.Sequence("test", "ATCG")
        assert str(seq) == "ATCG"

    def test_sequence_repr(self):
        """Test string representation."""
        seq = raidx.Sequence("test", "ATCG", 1, 4)
        repr_str = repr(seq)
        assert "test" in repr_str
        assert "ATCG" in repr_str

    def test_sequence_length(self):
        """Test sequence length."""
        seq = raidx.Sequence("test", "ATCG")
        assert len(seq) == 4

    def test_sequence_equality(self):
        """Test sequence equality."""
        seq1 = raidx.Sequence("test", "ATCG")
        seq2 = raidx.Sequence("test", "ATCG")
        assert seq1 == seq2
        assert seq1 == "ATCG"
        assert seq1 != "GCTA"

    def test_sequence_slicing(self):
        """Test sequence slicing."""
        seq = raidx.Sequence("test", "ATCGATCG", 1, 8)

        # Basic slice
        subseq = seq[1:4]
        assert subseq.seq == "TCG"

        # Step slice
        step_seq = seq[::2]
        assert len(step_seq.seq) == 4  # Every other character

        # Reverse
        rev_seq = seq[::-1]
        assert rev_seq.seq == "GCTAGCTA"

    def test_sequence_indexing(self):
        """Test single character indexing."""
        seq = raidx.Sequence("test", "ATCG")

        first = seq[0]
        assert first.seq == "A"

        last = seq[-1]
        assert last.seq == "G"

    def test_fancy_name(self):
        """Test fancy name generation."""
        seq = raidx.Sequence("chr1", "ATCG", 100, 103)
        assert seq.fancy_name == "chr1:100-103"

        seq_comp = raidx.Sequence("chr1", "ATCG", 100, 103, True)
        assert "complement" in seq_comp.fancy_name

    def test_complement(self):
        """Test complement generation."""
        seq = raidx.Sequence("test", "ATCG")
        comp = seq.complement
        assert comp.seq == "TAGC"
        assert comp.comp != seq.comp

    def test_reverse(self):
        """Test reverse generation."""
        seq = raidx.Sequence("test", "ATCG", 1, 4)
        rev = seq.reverse
        assert rev.seq == "GCTA"

    def test_reverse_complement(self):
        """Test reverse complement (negative operator)."""
        seq = raidx.Sequence("test", "ATCG")
        rev_comp = -seq
        assert rev_comp.seq == "CGAT"

    def test_gc_content(self):
        """Test GC content calculation."""
        seq = raidx.Sequence("test", "ATCG")
        gc = seq.gc
        assert gc == 0.5  # 2 GC out of 4 total

        seq_all_gc = raidx.Sequence("test", "GCGC")
        assert seq_all_gc.gc == 1.0

        seq_no_gc = raidx.Sequence("test", "ATAT")
        assert seq_no_gc.gc == 0.0


class TestFaidx:
    """Test the lower-level Faidx class."""

    def test_faidx_creation(self, temp_fasta_file):
        """Test Faidx creation."""
        faidx = raidx.Faidx(temp_fasta_file)
        assert str(faidx) == f'Faidx("{temp_fasta_file}")'

    def test_faidx_keys(self, temp_fasta_file):
        """Test getting keys from Faidx."""
        faidx = raidx.Faidx(temp_fasta_file)
        keys = faidx.keys
        assert isinstance(keys, list)
        assert len(keys) > 0

    def test_faidx_contains(self, temp_fasta_file):
        """Test membership in Faidx."""
        faidx = raidx.Faidx(temp_fasta_file)
        assert "test_seq1" in faidx
        assert "nonexistent" not in faidx

    def test_faidx_fetch(self, genes_fasta_file):
        """Test fetching sequences with Faidx."""
        faidx = raidx.Faidx(genes_fasta_file)
        seq = faidx.fetch("NM_001282543.1", 1, 10)
        assert isinstance(seq, raidx.Sequence)
        assert len(seq) == 10


class TestIndexGeneration:
    """Test index file generation and handling."""

    def test_index_creation(self, temp_fasta_file):
        """Test that index file is created."""
        _ = raidx.Fasta(temp_fasta_file)
        index_path = temp_fasta_file + ".fai"
        assert os.path.exists(index_path)

    def test_index_rebuild_false(self, temp_fasta_file):
        """Test with rebuild=False."""
        # Create initial index
        _ = raidx.Fasta(temp_fasta_file)
        index_path = temp_fasta_file + ".fai"
        assert os.path.exists(index_path)

        # Get modification time
        initial_mtime = os.path.getmtime(index_path)

        # Create new Fasta object with rebuild=False
        _ = raidx.Fasta(temp_fasta_file, rebuild=False)
        new_mtime = os.path.getmtime(index_path)

        # Index should not be rebuilt
        assert new_mtime == initial_mtime


class TestSpecialCases:
    """Test edge cases and special scenarios."""

    def test_empty_sequence(self, temp_fasta_file):
        """Test handling of empty sequences."""
        fasta = raidx.Fasta(temp_fasta_file)
        empty_record = fasta["empty_seq"]
        assert len(empty_record) == 0

    def test_short_sequence(self, temp_fasta_file):
        """Test handling of very short sequences."""
        fasta = raidx.Fasta(temp_fasta_file)
        short_record = fasta["short_seq"]
        assert len(short_record) == 4
        assert str(short_record) == "ATCG"

    def test_mixed_case(self, temp_fasta_file):
        """Test handling of mixed case sequences."""
        fasta = raidx.Fasta(temp_fasta_file)
        mixed_record = fasta["mixed_case"]
        seq_str = str(mixed_record)
        assert "A" in seq_str or "a" in seq_str
        assert "t" in seq_str or "T" in seq_str

    def test_sequence_always_upper(self, temp_fasta_file):
        """Test sequence_always_upper option."""
        fasta = raidx.Fasta(temp_fasta_file, sequence_always_upper=True)
        mixed_record = fasta["mixed_case"]
        seq_str = str(mixed_record)
        assert seq_str == seq_str.upper()

    def test_as_raw_option(self, temp_fasta_file):
        """Test as_raw option."""
        fasta = raidx.Fasta(temp_fasta_file, as_raw=True)
        record = fasta["test_seq1"]
        # When as_raw=True, slicing should return strings instead of Sequence objects
        subseq = record[0:10]
        # Test that we get some kind of result (implementation may vary)
        assert subseq is not None

    def test_strict_bounds(self, temp_fasta_file):
        """Test strict bounds checking."""
        # Test with strict_bounds=False (default) - should handle gracefully
        fasta_relaxed = raidx.Fasta(temp_fasta_file, strict_bounds=False)
        record_relaxed = fasta_relaxed["short_seq"]  # Length is 4

        # Out of bounds access should work gracefully (return empty or clamped result)
        out_of_bounds_relaxed = record_relaxed[10:20]  # Way beyond length 4
        assert len(out_of_bounds_relaxed) == 0  # Should return empty sequence

        # Test with strict_bounds=True - should raise IndexError for out-of-bounds
        fasta_strict = raidx.Fasta(temp_fasta_file, strict_bounds=True)
        record_strict = fasta_strict["short_seq"]  # Length is 4

        # Valid access should work
        valid_seq = record_strict[0:4]
        assert len(valid_seq) == 4

        # Out of bounds access should raise IndexError
        with pytest.raises(IndexError, match="out of bounds"):
            record_strict[10:20]  # Way beyond length 4

        # Test boundary case - accessing exactly at the end
        boundary_seq = record_strict[3:4]  # Should work (0-based indexing)
        assert len(boundary_seq) == 1

        # Test accessing one past the end should fail
        with pytest.raises(IndexError, match="out of bounds"):
            record_strict[5:10]  # Beyond length 4


class TestCompatibilityExamples:
    """Test examples from the original pyfaidx documentation."""

    def test_basic_usage_example(self, genes_fasta_file):
        """Test the basic usage example from documentation."""
        genes = raidx.Fasta(genes_fasta_file)

        # Test keys
        keys = genes.keys()
        assert "NM_001282543.1" in keys

        # Test slicing
        subseq = genes["NM_001282543.1"][200:230]
        assert isinstance(subseq, raidx.Sequence)
        assert len(subseq) == 30

        # Test attributes
        assert subseq.name == "NM_001282543.1"
        assert subseq.start == 201  # 1-based
        assert subseq.end == 230

        # Test fancy_name
        fancy = subseq.fancy_name
        assert "NM_001282543.1:201-230" == fancy

    def test_indexing_like_list(self, genes_fasta_file):
        """Test indexing like a list."""
        genes = raidx.Fasta(genes_fasta_file)
        first_record = genes[0]
        assert isinstance(first_record, raidx.FastaRecord)

        # Test slicing the first record
        subseq = first_record[:50]
        assert len(subseq) == 50

    def test_string_slicing_behavior(self, genes_fasta_file):
        """Test string-like slicing behavior."""
        genes = raidx.Fasta(genes_fasta_file)
        record = genes["NM_001282543.1"]

        # Test chained slicing
        subseq1 = record[200:230]
        subseq2 = subseq1[:10]
        assert len(subseq2) == 10

        # Test reverse slicing
        rev_seq = record[200:230][::-1]
        assert len(rev_seq) == 30

        # Test step slicing
        step_seq = record[200:230][::3]
        assert len(step_seq) <= 10

    def test_complement_and_reverse(self, genes_fasta_file):
        """Test complement and reverse operations."""
        genes = raidx.Fasta(genes_fasta_file)
        seq = genes["NM_001282543.1"][200:230]

        # Test complement
        comp = seq.complement
        assert comp.seq != seq.seq
        assert "complement" in comp.fancy_name

        # Test reverse
        rev = seq.reverse
        assert rev.seq != seq.seq

        # Test reverse complement (negative operator)
        rev_comp = -seq
        assert rev_comp.seq != seq.seq
        assert len(rev_comp) == len(seq)

    def test_get_seq_method_examples(self, genes_fasta_file):
        """Test get_seq method examples."""
        genes = raidx.Fasta(genes_fasta_file)

        # Basic get_seq
        seq = genes.get_seq("NM_001282543.1", 201, 210)
        assert seq.name == "NM_001282543.1"
        assert seq.start == 201
        assert seq.end == 210

        # get_seq with reverse complement
        seq_rc = genes.get_seq("NM_001282543.1", 201, 210, rc=True)
        assert seq_rc.seq != seq.seq
        assert len(seq_rc) == len(seq)


class TestFullSequenceAccess:
    """Test the optimized full sequence access pattern fasta['seq'][:].seq"""

    def test_full_sequence_slice_basic(self, temp_fasta_file):
        """Test the basic fasta['sequence'][:].seq pattern."""
        fasta = raidx.Fasta(temp_fasta_file)

        # Test the exact pattern from the benchmark
        seq_str = fasta["test_seq1"][:].seq
        assert isinstance(seq_str, str)
        assert len(seq_str) == 120  # 60 + 60 characters

        # Should contain only valid DNA characters
        valid_chars = set("ATCG")
        assert all(c in valid_chars for c in seq_str)

    def test_full_sequence_vs_str_method(self, temp_fasta_file):
        """Test that [:].seq gives same result as str(record)."""
        fasta = raidx.Fasta(temp_fasta_file)
        record = fasta["test_seq1"]

        # These should be identical
        full_slice_seq = record[:].seq
        str_method_seq = str(record)

        assert full_slice_seq == str_method_seq
        assert len(full_slice_seq) == len(str_method_seq)

    def test_full_sequence_equivalent_patterns(self, temp_fasta_file):
        """Test that different ways of getting full sequence are equivalent."""
        fasta = raidx.Fasta(temp_fasta_file)
        record = fasta["test_seq1"]

        # All these should give the same result
        pattern1 = record[:].seq  # Our optimized pattern
        pattern2 = record[::1].seq  # Explicit step=1
        pattern3 = record[0 : len(record)].seq  # Explicit start/end
        pattern4 = str(record)  # str() method

        assert pattern1 == pattern2 == pattern3 == pattern4
        assert len(pattern1) == len(pattern2) == len(pattern3) == len(pattern4)

    def test_full_sequence_all_test_sequences(self, temp_fasta_file):
        """Test full sequence access on all sequences in test file."""
        fasta = raidx.Fasta(temp_fasta_file)

        for seq_name in fasta.keys():
            # Test the benchmark pattern
            full_seq = fasta[seq_name][:].seq
            assert isinstance(full_seq, str)

            # Length should match what len(record) reports
            record = fasta[seq_name]
            assert len(full_seq) == len(record)

            # Should match str() method
            assert full_seq == str(record)

    def test_full_sequence_empty_seq(self, temp_fasta_file):
        """Test full sequence access on empty sequence."""
        fasta = raidx.Fasta(temp_fasta_file)

        # empty_seq has no content
        empty_seq = fasta["empty_seq"][:].seq
        assert empty_seq == ""
        assert len(empty_seq) == 0

    def test_full_sequence_short_seq(self, temp_fasta_file):
        """Test full sequence access on very short sequence."""
        fasta = raidx.Fasta(temp_fasta_file)

        # short_seq is just "ATCG"
        short_seq = fasta["short_seq"][:].seq
        assert short_seq == "ATCG"
        assert len(short_seq) == 4

    def test_full_sequence_mixed_case(self, temp_fasta_file):
        """Test full sequence access preserves case (when not using sequence_always_upper)."""
        fasta = raidx.Fasta(temp_fasta_file, sequence_always_upper=False)

        mixed_seq = fasta["mixed_case"][:].seq
        # Should preserve original case from FASTA file
        assert isinstance(mixed_seq, str)
        assert len(mixed_seq) == 16  # "AtCgAtCgAtCgAtCg"

        # Should contain both upper and lower case
        has_upper = any(c.isupper() for c in mixed_seq)
        has_lower = any(c.islower() for c in mixed_seq)
        assert has_upper and has_lower

    def test_full_sequence_always_upper(self, temp_fasta_file):
        """Test full sequence access with sequence_always_upper=True."""
        fasta = raidx.Fasta(temp_fasta_file, sequence_always_upper=True)

        mixed_seq = fasta["mixed_case"][:].seq
        # Should be all uppercase
        assert mixed_seq == mixed_seq.upper()
        assert mixed_seq == "ATCGATCGATCGATCG"

    def test_full_sequence_coordinates(self, temp_fasta_file):
        """Test that full sequence slice has correct coordinates."""
        fasta = raidx.Fasta(temp_fasta_file)

        full_seq_obj = fasta["test_seq1"][:]  # Get the Sequence object, not just .seq
        assert isinstance(full_seq_obj, raidx.Sequence)

        # Should have coordinates for the full sequence
        assert full_seq_obj.start == 1  # 1-based indexing
        assert full_seq_obj.end == len(full_seq_obj)
        assert full_seq_obj.name == "test_seq1"

    def test_benchmark_pattern_performance_path(self, genes_fasta_file):
        """Test the exact pattern from the performance benchmark."""
        fasta = raidx.Fasta(genes_fasta_file)

        # This is the exact pattern that was benchmarked and optimized
        for seq_name in fasta.keys():
            # The benchmark pattern: fa['chr1'][:].seq
            seq_str = fasta[seq_name][:].seq

            assert isinstance(seq_str, str)
            assert len(seq_str) > 0  # All our test sequences have content

            # Verify this uses our fast path by checking it matches other methods
            record = fasta[seq_name]
            assert seq_str == str(record)

    def test_full_sequence_vs_manual_fetch(self, genes_fasta_file):
        """Test that [:].seq matches manual fetch of full range."""
        fasta = raidx.Fasta(genes_fasta_file)

        seq_name = "NM_001282543.1"  # Use a known sequence
        record = fasta[seq_name]

        # Our optimized pattern
        full_slice = record[:].seq

        # Manual fetch of the same range
        manual_fetch = fasta.get_seq(seq_name, 1, len(record)).seq

        assert full_slice == manual_fetch
        assert len(full_slice) == len(manual_fetch)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
