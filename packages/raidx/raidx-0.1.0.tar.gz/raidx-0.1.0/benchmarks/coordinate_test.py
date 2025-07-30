#!/usr/bin/env python3
"""
Test script to verify coordinate system behavior in raidx vs pyfaidx.

This script helps debug coordinate-related issues and ensures consistent
behavior between slicing and get_seq methods.
"""

import tempfile
import os


def create_test_fasta():
    """Create a simple test FASTA file with known sequence."""
    content = """>test_seq
ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
        f.write(content)
        return f.name


def test_coordinates():
    """Test coordinate systems in both libraries."""
    fasta_file = create_test_fasta()
    
    try:
        print("Testing coordinate systems with known sequence:")
        print("Sequence: ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz")
        print("Positions:")
        print("          1111111111222222222233333333334444444444555555555566")  
        print("0123456789012345678901234567890123456789012345678901234567890123")
        print()

        # Test raidx
        print("=== RAIDX ===")
        try:
            import raidx
            fa = raidx.Fasta(fasta_file)
            seq_name = fa.keys()[0]
            
            # Test slicing (0-based, exclusive end)
            slice_result = str(fa[seq_name][10:15])  # Should be KLMNO (positions 10-14)
            print(f"Slicing [10:15]: '{slice_result}' (length: {len(slice_result)})")
            
            # Test get_seq (1-based, inclusive)
            get_seq_result = str(fa.get_seq(seq_name, 11, 15))  # Should be KLMNO (positions 11-15)
            print(f"get_seq(11, 15): '{get_seq_result}' (length: {len(get_seq_result)})")
            
            # Test our benchmark coordinates
            slice_100 = str(fa[seq_name][10:20])  # 10 bases
            get_seq_10 = str(fa.get_seq(seq_name, 11, 20))  # 10 bases (1-based inclusive)
            print(f"Slice [10:20]: '{slice_100}' (length: {len(slice_100)})")
            print(f"get_seq(11, 20): '{get_seq_10}' (length: {len(get_seq_10)})")
            
        except ImportError:
            print("raidx not available")
        except Exception as e:
            print(f"raidx error: {e}")

        print()

        # Test pyfaidx
        print("=== PYFAIDX ===")
        try:
            import pyfaidx
            fa = pyfaidx.Fasta(fasta_file)
            seq_name = list(fa.keys())[0]
            
            # Test slicing (0-based, exclusive end)
            slice_result = str(fa[seq_name][10:15])  # Should be KLMNO (positions 10-14)
            print(f"Slicing [10:15]: '{slice_result}' (length: {len(slice_result)})")
            
            # Test get_seq (1-based, inclusive)
            get_seq_result = str(fa.get_seq(seq_name, 11, 15))  # Should be KLMNO (positions 11-15)
            print(f"get_seq(11, 15): '{get_seq_result}' (length: {len(get_seq_result)})")
            
            # Test our benchmark coordinates
            slice_100 = str(fa[seq_name][10:20])  # 10 bases
            get_seq_10 = str(fa.get_seq(seq_name, 11, 20))  # 10 bases (1-based inclusive)
            print(f"Slice [10:20]: '{slice_100}' (length: {len(slice_100)})")
            print(f"get_seq(11, 20): '{get_seq_10}' (length: {len(get_seq_10)})")
            
        except ImportError:
            print("pyfaidx not available")
        except Exception as e:
            print(f"pyfaidx error: {e}")

    finally:
        # Cleanup
        try:
            os.unlink(fasta_file)
            if os.path.exists(fasta_file + ".fai"):
                os.unlink(fasta_file + ".fai")
        except:
            pass


if __name__ == "__main__":
    test_coordinates() 