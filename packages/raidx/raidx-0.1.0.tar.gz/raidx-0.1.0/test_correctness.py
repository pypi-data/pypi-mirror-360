#!/usr/bin/env python3

import sys
import hashlib

def test_sequence_correctness():
    """Test that raidx produces identical results to pyfaidx for full sequences"""
    
    # Test file - use the simple test file we created
    test_file = 'data/test/test.fasta'
    
    try:
        import raidx
        import pyfaidx
        
        print("Testing sequence correctness...")
        print("=" * 50)
        
        # Load both implementations
        raidx_fa = raidx.Fasta(test_file)
        pyfaidx_fa = pyfaidx.Fasta(test_file)
        
        # Test all sequences in the file
        success = True
        
        for seq_name in raidx_fa.keys():
            print(f"\nTesting sequence: {seq_name}")
            
            # Get full sequences
            raidx_seq = raidx_fa[seq_name][:].seq
            pyfaidx_seq = str(pyfaidx_fa[seq_name][:])
            
            # Compare lengths
            print(f"  raidx length:  {len(raidx_seq)}")
            print(f"  pyfaidx length: {len(pyfaidx_seq)}")
            
            if len(raidx_seq) != len(pyfaidx_seq):
                print(f"  ❌ Length mismatch!")
                success = False
                continue
            
            # Compare content
            if raidx_seq == pyfaidx_seq:
                print(f"  ✅ Sequences match perfectly")
            else:
                print(f"  ❌ Sequence content differs!")
                success = False
                
                # Show where they differ
                for i, (r_char, p_char) in enumerate(zip(raidx_seq, pyfaidx_seq)):
                    if r_char != p_char:
                        print(f"    First difference at position {i}: raidx='{r_char}' pyfaidx='{p_char}'")
                        # Show context around the difference
                        start = max(0, i-10)
                        end = min(len(raidx_seq), i+11)
                        print(f"    raidx  context: '{raidx_seq[start:end]}'")
                        print(f"    pyfaidx context: '{pyfaidx_seq[start:end]}'")
                        break
            
            # Compare hashes for extra verification
            raidx_hash = hashlib.md5(raidx_seq.encode()).hexdigest()
            pyfaidx_hash = hashlib.md5(pyfaidx_seq.encode()).hexdigest()
            
            print(f"  raidx MD5:  {raidx_hash}")
            print(f"  pyfaidx MD5: {pyfaidx_hash}")
            
            if raidx_hash != pyfaidx_hash:
                print(f"  ❌ Hash mismatch confirms content difference!")
                success = False
        
        print("\n" + "=" * 50)
        if success:
            print("✅ ALL TESTS PASSED - Sequences are identical!")
        else:
            print("❌ TESTS FAILED - Sequences differ!")
            
        return success
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure both raidx and pyfaidx are installed")
        return False
    except Exception as e:
        print(f"Error during testing: {e}")
        return False

def test_large_file_if_available():
    """Test with the large genome file if available"""
    large_file = 'data/ref/GRCh38_no_alt_analysis_set_GCA_000001405.15.fasta'
    
    try:
        import os
        if not os.path.exists(large_file):
            print(f"\nLarge test file not found: {large_file}")
            print("Skipping large file test")
            return True
            
        import raidx
        import pyfaidx
        
        print(f"\nTesting large file: {large_file}")
        print("=" * 50)
        
        # Load both implementations
        raidx_fa = raidx.Fasta(large_file)
        pyfaidx_fa = pyfaidx.Fasta(large_file)
        
        # Test just chr1 and chr2 (the ones from the benchmark)
        test_chromosomes = ['chr1', 'chr2']
        
        success = True
        for chr_name in test_chromosomes:
            if chr_name in raidx_fa.keys():
                print(f"\nTesting {chr_name}...")
                
                # Get full sequences
                raidx_seq = raidx_fa[chr_name][:].seq
                pyfaidx_seq = str(pyfaidx_fa[chr_name][:])
                
                print(f"  Length: {len(raidx_seq):,} bp")
                
                if raidx_seq == pyfaidx_seq:
                    print(f"  ✅ {chr_name} sequences match perfectly")
                else:
                    print(f"  ❌ {chr_name} sequences differ!")
                    success = False
                    
                    # Find first difference
                    for i, (r_char, p_char) in enumerate(zip(raidx_seq, pyfaidx_seq)):
                        if r_char != p_char:
                            print(f"    First difference at position {i:,}: raidx='{r_char}' pyfaidx='{p_char}'")
                            break
            else:
                print(f"  {chr_name} not found in file")
        
        return success
        
    except Exception as e:
        print(f"Error testing large file: {e}")
        return False

if __name__ == "__main__":
    print("raidx vs pyfaidx Correctness Test")
    print("=" * 50)
    
    # Test with small file first
    small_success = test_sequence_correctness()
    
    # Test with large file if available  
    large_success = test_large_file_if_available()
    
    if small_success and large_success:
        print("\n🎉 ALL CORRECTNESS TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n💥 CORRECTNESS TESTS FAILED!")
        sys.exit(1) 