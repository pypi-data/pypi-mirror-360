"""
RaidX Benchmarking Suite

This package contains performance benchmarks for the raidx library,
comparing it against pyfaidx and other FASTA processing libraries.

Usage:
    # Run all benchmarks
    pytest benchmarks/

    # Run specific benchmark categories
    pytest benchmarks/benchmark_file_ops.py
    pytest benchmarks/benchmark_sequence_ops.py

    # Run benchmarks with reporting
    pytest benchmarks/ --benchmark-only --benchmark-save=my_benchmark

    # Compare with previous results
    pytest benchmarks/ --benchmark-compare=baseline

For standalone benchmarking outside pytest, use the CLI tools:
    python -m benchmarks.cli your_file.fasta
"""

__version__ = "1.0.0" 