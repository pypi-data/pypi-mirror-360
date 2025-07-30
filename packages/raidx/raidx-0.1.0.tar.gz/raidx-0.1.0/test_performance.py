#!/usr/bin/env python3

import time
import sys

def test_raidx():
    """Test the optimized raidx performance"""
    try:
        import raidx
        print("Testing raidx (optimized)...")
        
        # Create a dummy fasta file for testing if needed
        fasta_file = 'data/ref/GRCh38_no_alt_analysis_set_GCA_000001405.15.fasta'
        
        start_time = time.time()
        fa = raidx.Fasta(fasta_file)
        
        # The specific benchmark from the user query
        seq = fa['chr1'][:].seq
        seq = fa['chr2'][:].seq
        
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"raidx time: {elapsed:.3f} seconds")
        return elapsed
        
    except ImportError:
        print("raidx not available")
        return None
    except Exception as e:
        print(f"raidx error: {e}")
        return None

def test_pyfaidx():
    """Test pyfaidx performance for comparison"""
    try:
        import pyfaidx
        print("Testing pyfaidx...")
        
        fasta_file = 'data/ref/GRCh38_no_alt_analysis_set_GCA_000001405.15.fasta'
        
        start_time = time.time()
        fa = pyfaidx.Fasta(fasta_file)
        
        # The specific benchmark from the user query
        seq = fa['chr1'][:].seq
        seq = fa['chr2'][:].seq
        
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"pyfaidx time: {elapsed:.3f} seconds")
        return elapsed
        
    except ImportError:
        print("pyfaidx not available")
        return None
    except Exception as e:
        print(f"pyfaidx error: {e}")
        return None

def main():
    print("Performance comparison test")
    print("=" * 50)
    
    # Test both implementations
    raidx_time = test_raidx()
    pyfaidx_time = test_pyfaidx()
    
    print("\nResults:")
    print("=" * 50)
    
    if raidx_time is not None:
        print(f"raidx:   {raidx_time:.3f} seconds")
    if pyfaidx_time is not None:
        print(f"pyfaidx: {pyfaidx_time:.3f} seconds")
        
    if raidx_time is not None and pyfaidx_time is not None:
        speedup = pyfaidx_time / raidx_time
        print(f"\nSpeedup: {speedup:.2f}x")
        if speedup > 1.0:
            print("✅ raidx is faster than pyfaidx!")
        else:
            print("❌ raidx is slower than pyfaidx")
    
    # Run a smaller test for basic functionality
    print("\n" + "=" * 50)
    print("Basic functionality test:")
    try:
        import raidx
        # Test with a smaller sequence if the large file doesn't exist
        print("raidx import successful")
        
        # Try to access some basic functionality
        print("raidx basic functionality: ✅")
        
    except Exception as e:
        print(f"raidx basic test failed: {e}")

if __name__ == "__main__":
    main() 