#!/usr/bin/env python3
"""
RaidX vs PyFaidx Performance Benchmark Tool

This script compares the performance of raidx (Rust implementation) 
against pyfaidx (Python implementation) for FASTA file operations.

Usage:
    python benchmark_raidx.py <fasta_file> [options]

Example:
    python benchmark_raidx.py genome.fasta --iterations 1000 --random-access 100
"""

import argparse
import time
import random
import statistics
import sys
import os
from typing import List, Tuple, Dict, Any
from pathlib import Path

try:
    import raidx
    RAIDX_AVAILABLE = True
except ImportError:
    RAIDX_AVAILABLE = False
    print("Warning: raidx not available. Install it with: pip install .")

try:
    import pyfaidx
    PYFAIDX_AVAILABLE = True
except ImportError:
    PYFAIDX_AVAILABLE = False
    print("Warning: pyfaidx not available. Install it with: pip install pyfaidx")

class BenchmarkResults:
    """Class to store and format benchmark results."""
    
    def __init__(self):
        self.results = {}
    
    def add_result(self, test_name: str, library: str, times: List[float], **metadata):
        """Add benchmark result."""
        if test_name not in self.results:
            self.results[test_name] = {}
        
        self.results[test_name][library] = {
            'times': times,
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'min': min(times),
            'max': max(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0,
            'metadata': metadata
        }
    
    def print_results(self):
        """Print formatted benchmark results."""
        print("\n" + "="*80)
        print("BENCHMARK RESULTS")
        print("="*80)
        
        for test_name, libs in self.results.items():
            print(f"\n{test_name}")
            print("-" * len(test_name))
            
            # Print table header
            print(f"{'Library':<12} {'Mean (ms)':<12} {'Median (ms)':<14} {'Min (ms)':<10} {'Max (ms)':<10} {'StdDev':<10}")
            print("-" * 70)
            
            # Print results for each library
            for lib_name, data in libs.items():
                mean_ms = data['mean'] * 1000
                median_ms = data['median'] * 1000
                min_ms = data['min'] * 1000
                max_ms = data['max'] * 1000
                stdev_ms = data['stdev'] * 1000
                
                print(f"{lib_name:<12} {mean_ms:<12.3f} {median_ms:<14.3f} {min_ms:<10.3f} {max_ms:<10.3f} {stdev_ms:<10.3f}")
            
            # Calculate speedup if both libraries present
            if len(libs) == 2:
                lib_names = list(libs.keys())
                if 'raidx' in lib_names and 'pyfaidx' in lib_names:
                    pyfaidx_mean = libs['pyfaidx']['mean']
                    raidx_mean = libs['raidx']['mean']
                    speedup = pyfaidx_mean / raidx_mean
                    print(f"\nSpeedup: {speedup:.2f}x faster")
                    
                    if speedup > 1:
                        print(f"raidx is {speedup:.2f}x faster than pyfaidx")
                    else:
                        print(f"pyfaidx is {1/speedup:.2f}x faster than raidx")
            
            # Print metadata if available
            for lib_name, data in libs.items():
                if data['metadata']:
                    meta_str = ", ".join(f"{k}={v}" for k, v in data['metadata'].items())
                    print(f"{lib_name} metadata: {meta_str}")


class FastaBenchmark:
    """Main benchmark class."""
    
    def __init__(self, fasta_file: str, iterations: int = 100):
        self.fasta_file = fasta_file
        self.iterations = iterations
        self.results = BenchmarkResults()
        
        # Verify file exists
        if not os.path.exists(fasta_file):
            raise FileNotFoundError(f"FASTA file not found: {fasta_file}")
        
        # Get file info
        self.file_size = os.path.getsize(fasta_file) / (1024 * 1024)  # MB
        print(f"Benchmarking file: {fasta_file}")
        print(f"File size: {self.file_size:.2f} MB")
    
    def time_function(self, func, *args, **kwargs) -> List[float]:
        """Time a function multiple iterations and return list of times."""
        times = []
        for _ in range(self.iterations):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        return times
    
    def benchmark_file_opening(self):
        """Benchmark file opening/initialization."""
        print("\nBenchmarking file opening...")
        
        def open_pyfaidx():
            fa = pyfaidx.Fasta(self.fasta_file)
            return len(fa.keys())
        
        def open_raidx():
            fa = raidx.Fasta(self.fasta_file)
            return len(fa.keys())
        
        if PYFAIDX_AVAILABLE:
            times = self.time_function(open_pyfaidx)
            self.results.add_result("File Opening", "pyfaidx", times)
        
        if RAIDX_AVAILABLE:
            times = self.time_function(open_raidx)
            self.results.add_result("File Opening", "raidx", times)
    
    def benchmark_sequence_access(self, seq_name: str = None):
        """Benchmark accessing sequences by name."""
        print("\nBenchmarking sequence access...")
        
        # Get a sequence name if not provided
        if seq_name is None:
            if PYFAIDX_AVAILABLE:
                fa = pyfaidx.Fasta(self.fasta_file)
                seq_name = list(fa.keys())[0]
            elif RAIDX_AVAILABLE:
                fa = raidx.Fasta(self.fasta_file)
                seq_name = fa.keys()[0]
            else:
                print("No libraries available for sequence access benchmark")
                return
        
        def access_pyfaidx():
            fa = pyfaidx.Fasta(self.fasta_file)
            return len(fa[seq_name])
        
        def access_raidx():
            fa = raidx.Fasta(self.fasta_file)
            return len(fa[seq_name])
        
        if PYFAIDX_AVAILABLE:
            times = self.time_function(access_pyfaidx)
            self.results.add_result("Sequence Access", "pyfaidx", times, sequence=seq_name)
        
        if RAIDX_AVAILABLE:
            times = self.time_function(access_raidx)
            self.results.add_result("Sequence Access", "raidx", times, sequence=seq_name)
    
    def benchmark_slicing(self, seq_name: str = None, start: int = 1000, length: int = 100):
        """Benchmark sequence slicing operations."""
        print(f"\nBenchmarking sequence slicing ({start}:{start+length})...")
        
        # Get a sequence name if not provided
        if seq_name is None:
            if PYFAIDX_AVAILABLE:
                fa = pyfaidx.Fasta(self.fasta_file)
                seq_name = list(fa.keys())[0]
            elif RAIDX_AVAILABLE:
                fa = raidx.Fasta(self.fasta_file)
                seq_name = fa.keys()[0]
            else:
                print("No libraries available for slicing benchmark")
                return
        
        def slice_pyfaidx():
            fa = pyfaidx.Fasta(self.fasta_file)
            seq = fa[seq_name][start:start+length]
            return str(seq)
        
        def slice_raidx():
            fa = raidx.Fasta(self.fasta_file)
            seq = fa[seq_name][start:start+length]
            return str(seq)
        
        if PYFAIDX_AVAILABLE:
            times = self.time_function(slice_pyfaidx)
            self.results.add_result("Sequence Slicing", "pyfaidx", times, 
                                   start=start, length=length, sequence=seq_name)
        
        if RAIDX_AVAILABLE:
            times = self.time_function(slice_raidx)
            self.results.add_result("Sequence Slicing", "raidx", times,
                                   start=start, length=length, sequence=seq_name)
    
    def benchmark_iteration(self, max_sequences: int = 10):
        """Benchmark iterating through sequences."""
        print(f"\nBenchmarking iteration over first {max_sequences} sequences...")
        
        def iterate_pyfaidx():
            fa = pyfaidx.Fasta(self.fasta_file)
            count = 0
            for record in fa:
                count += len(record)
                if count >= max_sequences:
                    break
            return count
        
        def iterate_raidx():
            fa = raidx.Fasta(self.fasta_file)
            count = 0
            for record in fa:
                count += len(record)
                if count >= max_sequences:
                    break
            return count
        
        if PYFAIDX_AVAILABLE:
            times = self.time_function(iterate_pyfaidx)
            self.results.add_result("Sequence Iteration", "pyfaidx", times, max_sequences=max_sequences)
        
        if RAIDX_AVAILABLE:
            times = self.time_function(iterate_raidx)
            self.results.add_result("Sequence Iteration", "raidx", times, max_sequences=max_sequences)
    
    def benchmark_random_access(self, num_accesses: int = 50):
        """Benchmark random access patterns."""
        print(f"\nBenchmarking random access ({num_accesses} random slices)...")
        
        # Get sequence info for generating random coordinates
        if PYFAIDX_AVAILABLE:
            fa = pyfaidx.Fasta(self.fasta_file)
            seq_names = list(fa.keys())
            seq_lengths = {name: len(fa[name]) for name in seq_names}
        elif RAIDX_AVAILABLE:
            fa = raidx.Fasta(self.fasta_file)
            seq_names = fa.keys()[:5]  # Limit to first 5 sequences
            seq_lengths = {name: len(fa[name]) for name in seq_names}
        else:
            print("No libraries available for random access benchmark")
            return
        
        # Generate random access patterns
        access_patterns = []
        for _ in range(num_accesses):
            seq_name = random.choice(seq_names)
            seq_len = seq_lengths[seq_name]
            if seq_len > 1000:  # Only if sequence is long enough
                start = random.randint(1, max(1, seq_len - 100))
                length = random.randint(10, min(100, seq_len - start))
                access_patterns.append((seq_name, start, length))
        
        def random_access_pyfaidx():
            fa = pyfaidx.Fasta(self.fasta_file)
            results = []
            for seq_name, start, length in access_patterns:
                seq = fa[seq_name][start:start+length]
                results.append(str(seq))
            return len(results)
        
        def random_access_raidx():
            fa = raidx.Fasta(self.fasta_file)
            results = []
            for seq_name, start, length in access_patterns:
                seq = fa[seq_name][start:start+length]
                results.append(str(seq))
            return len(results)
        
        if PYFAIDX_AVAILABLE:
            times = self.time_function(random_access_pyfaidx)
            self.results.add_result("Random Access", "pyfaidx", times, num_accesses=num_accesses)
        
        if RAIDX_AVAILABLE:
            times = self.time_function(random_access_raidx)
            self.results.add_result("Random Access", "raidx", times, num_accesses=num_accesses)
    
    def benchmark_reverse_complement(self, seq_name: str = None, start: int = 1000, length: int = 100):
        """Benchmark reverse complement operations."""
        print(f"\nBenchmarking reverse complement operations...")
        
        # Get a sequence name if not provided
        if seq_name is None:
            if PYFAIDX_AVAILABLE:
                fa = pyfaidx.Fasta(self.fasta_file)
                seq_name = list(fa.keys())[0]
            elif RAIDX_AVAILABLE:
                fa = raidx.Fasta(self.fasta_file)
                seq_name = fa.keys()[0]
            else:
                print("No libraries available for reverse complement benchmark")
                return
        
        def rc_pyfaidx():
            fa = pyfaidx.Fasta(self.fasta_file)
            seq = fa[seq_name][start:start+length]
            rc_seq = -seq  # Reverse complement
            return str(rc_seq)
        
        def rc_raidx():
            fa = raidx.Fasta(self.fasta_file)
            seq = fa[seq_name][start:start+length]
            rc_seq = -seq  # Reverse complement
            return str(rc_seq)
        
        if PYFAIDX_AVAILABLE:
            times = self.time_function(rc_pyfaidx)
            self.results.add_result("Reverse Complement", "pyfaidx", times,
                                   start=start, length=length, sequence=seq_name)
        
        if RAIDX_AVAILABLE:
            times = self.time_function(rc_raidx)
            self.results.add_result("Reverse Complement", "raidx", times,
                                   start=start, length=length, sequence=seq_name)
    
    def benchmark_get_seq_method(self, seq_name: str = None, start: int = 1000, length: int = 100):
        """Benchmark get_seq method calls."""
        print(f"\nBenchmarking get_seq method calls...")
        
        # Get a sequence name if not provided
        if seq_name is None:
            if PYFAIDX_AVAILABLE:
                fa = pyfaidx.Fasta(self.fasta_file)
                seq_name = list(fa.keys())[0]
            elif RAIDX_AVAILABLE:
                fa = raidx.Fasta(self.fasta_file)
                seq_name = fa.keys()[0]
            else:
                print("No libraries available for get_seq benchmark")
                return
        
        def get_seq_pyfaidx():
            fa = pyfaidx.Fasta(self.fasta_file)
            seq = fa.get_seq(seq_name, start, start + length - 1)
            return str(seq)
        
        def get_seq_raidx():
            fa = raidx.Fasta(self.fasta_file)
            seq = fa.get_seq(seq_name, start, start + length - 1)
            return str(seq)
        
        if PYFAIDX_AVAILABLE:
            times = self.time_function(get_seq_pyfaidx)
            self.results.add_result("get_seq Method", "pyfaidx", times,
                                   start=start, length=length, sequence=seq_name)
        
        if RAIDX_AVAILABLE:
            times = self.time_function(get_seq_raidx)
            self.results.add_result("get_seq Method", "raidx", times,
                                   start=start, length=length, sequence=seq_name)
    
    def run_all_benchmarks(self, **kwargs):
        """Run all benchmark tests."""
        print(f"Running benchmarks with {self.iterations} iterations each...")
        
        # Basic benchmarks
        self.benchmark_file_opening()
        self.benchmark_sequence_access()
        self.benchmark_slicing()
        self.benchmark_get_seq_method()
        self.benchmark_reverse_complement()
        
        # More intensive benchmarks
        self.benchmark_iteration(max_sequences=kwargs.get('max_sequences', 10))
        self.benchmark_random_access(num_accesses=kwargs.get('random_accesses', 50))
        
        # Print results
        self.results.print_results()


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark raidx vs pyfaidx performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python benchmark_raidx.py genome.fasta
  python benchmark_raidx.py genome.fasta --iterations 1000
  python benchmark_raidx.py genome.fasta --random-access 200 --max-sequences 20
        """
    )
    
    parser.add_argument('fasta_file', help='Path to FASTA file to benchmark')
    parser.add_argument('--iterations', '-i', type=int, default=100,
                       help='Number of iterations per test (default: 100)')
    parser.add_argument('--random-access', '-r', type=int, default=50,
                       help='Number of random access operations (default: 50)')
    parser.add_argument('--max-sequences', '-s', type=int, default=10,
                       help='Maximum sequences for iteration test (default: 10)')
    parser.add_argument('--sequence', type=str, default=None,
                       help='Specific sequence name to test (default: first sequence)')
    
    args = parser.parse_args()
    
    # Check if libraries are available
    if not PYFAIDX_AVAILABLE and not RAIDX_AVAILABLE:
        print("Error: Neither pyfaidx nor raidx is available.")
        print("Install at least one with:")
        print("  pip install pyfaidx  # for pyfaidx")
        print("  pip install .       # for raidx (in this project directory)")
        sys.exit(1)
    
    try:
        benchmark = FastaBenchmark(args.fasta_file, args.iterations)
        benchmark.run_all_benchmarks(
            random_accesses=args.random_access,
            max_sequences=args.max_sequences
        )
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 