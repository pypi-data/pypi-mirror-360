"""
Command-line interface for raidx benchmarks.

Provides standalone benchmarking capabilities outside of pytest.
"""

import argparse
import sys
from pathlib import Path

# Import the original benchmark functionality
import os
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from benchmark_raidx import FastaBenchmark, main as original_main
    BENCHMARK_AVAILABLE = True
except ImportError:
    BENCHMARK_AVAILABLE = False


def main():
    """Main CLI entry point."""
    if not BENCHMARK_AVAILABLE:
        print("Error: Original benchmark module not found.")
        print("Make sure benchmark_raidx.py is in the project root.")
        sys.exit(1)
    
    # Use the original main function
    original_main()


if __name__ == "__main__":
    main() 