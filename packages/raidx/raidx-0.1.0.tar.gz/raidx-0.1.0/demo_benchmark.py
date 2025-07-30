#!/usr/bin/env python3
"""
Demo script for RaidX benchmark tool.

This script creates a sample FASTA file and demonstrates how to use the benchmark tool.
"""

import os
import tempfile
import subprocess
import sys
from pathlib import Path

def create_sample_fasta(filename: str, num_sequences: int = 5, seq_length: int = 10000):
    """Create a sample FASTA file for benchmarking."""
    import random
    
    bases = ['A', 'T', 'G', 'C']
    
    with open(filename, 'w') as f:
        for i in range(num_sequences):
            # Write header
            f.write(f">sequence_{i+1} Sample sequence {i+1}\n")
            
            # Write sequence in lines of 80 characters
            sequence = ''.join(random.choice(bases) for _ in range(seq_length))
            for j in range(0, len(sequence), 80):
                f.write(sequence[j:j+80] + '\n')
    
    print(f"Created sample FASTA file: {filename}")
    print(f"  - {num_sequences} sequences")
    print(f"  - {seq_length} bases per sequence")
    print(f"  - Total size: {os.path.getsize(filename) / 1024:.1f} KB")


def run_benchmark_demo():
    """Run a demonstration of the benchmark tool."""
    
    # Create a temporary FASTA file
    temp_fasta = "sample_demo.fasta"
    
    try:
        # Create sample data
        print("Creating sample FASTA file...")
        create_sample_fasta(temp_fasta, num_sequences=10, seq_length=5000)
        
        # Run benchmark with different configurations
        print("\n" + "="*60)
        print("RUNNING BENCHMARK DEMONSTRATION")
        print("="*60)
        
        # Quick benchmark (few iterations)
        print("\n1. Quick benchmark (10 iterations):")
        print("-" * 40)
        cmd = [sys.executable, "benchmark_raidx.py", temp_fasta, "--iterations", "10"]
        subprocess.run(cmd)
        
        # More detailed benchmark
        print("\n2. Detailed benchmark (50 iterations, more operations):")
        print("-" * 60)
        cmd = [sys.executable, "benchmark_raidx.py", temp_fasta, 
               "--iterations", "50", "--random-access", "100", "--max-sequences", "5"]
        subprocess.run(cmd)
        
    except Exception as e:
        print(f"Demo failed: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists(temp_fasta):
            os.remove(temp_fasta)
        if os.path.exists(temp_fasta + ".fai"):
            os.remove(temp_fasta + ".fai")
    
    return True


def main():
    """Main demo function."""
    print("RaidX Benchmark Demo")
    print("===================")
    
    # Check if benchmark script exists
    if not os.path.exists("benchmark_raidx.py"):
        print("Error: benchmark_raidx.py not found in current directory")
        sys.exit(1)
    
    # Check if we can import the required libraries
    raidx_available = False
    pyfaidx_available = False
    
    try:
        import raidx
        raidx_available = True
        print("✓ raidx is available")
    except ImportError:
        print("✗ raidx is not available")
    
    try:
        import pyfaidx
        pyfaidx_available = True
        print("✓ pyfaidx is available")
    except ImportError:
        print("✗ pyfaidx is not available")
    
    if not raidx_available and not pyfaidx_available:
        print("\nError: Neither raidx nor pyfaidx is available.")
        print("Install at least one of them:")
        print("  pip install pyfaidx     # for pyfaidx")
        print("  pip install .          # for raidx (in this project)")
        sys.exit(1)
    
    # Run the demo
    print(f"\nRunning demo with libraries: raidx={raidx_available}, pyfaidx={pyfaidx_available}")
    success = run_benchmark_demo()
    
    if success:
        print("\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nTo run benchmarks on your own FASTA files:")
        print("  python benchmark_raidx.py your_file.fasta")
        print("  python benchmark_raidx.py your_file.fasta --iterations 1000")
        print("  python benchmark_raidx.py your_file.fasta --help")
    else:
        print("Demo failed. Check error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main() 