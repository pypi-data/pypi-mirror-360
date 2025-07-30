# RaidX vs PyFaidx Benchmark Tool

A comprehensive benchmark tool to compare the performance of `raidx` (Rust implementation) against `pyfaidx` (Python implementation) for FASTA file operations.

## Features

The benchmark tool tests the following operations:

- **File Opening**: Time to open and initialize FASTA files
- **Sequence Access**: Accessing sequences by name
- **Sequence Slicing**: Extracting subsequences using slice notation
- **get_seq Method**: Using the `get_seq()` method for sequence retrieval
- **Reverse Complement**: Computing reverse complements of sequences
- **Iteration**: Iterating through sequences in the file
- **Random Access**: Random access patterns across multiple sequences

## Requirements

Install the required dependencies:

```bash
# Install pyfaidx (reference implementation)
pip install pyfaidx

# Install raidx (this Rust implementation)
pip install .  # from the raidx project directory
```

**Note**: You need at least one of these libraries installed to run benchmarks. The tool will automatically detect which libraries are available.

## Quick Start

### Run Demo

Test the benchmark tool with a sample FASTA file:

```bash
python demo_benchmark.py
```

This will:
1. Create a sample FASTA file
2. Run benchmarks with both quick and detailed configurations
3. Display performance comparisons
4. Clean up temporary files

### Benchmark Your Own Files

```bash
# Basic benchmark with default settings
python benchmark_raidx.py your_genome.fasta

# More iterations for better statistics
python benchmark_raidx.py your_genome.fasta --iterations 1000

# Intensive testing with more operations
python benchmark_raidx.py your_genome.fasta --iterations 500 --random-access 200 --max-sequences 20

# Help and options
python benchmark_raidx.py --help
```

## Command Line Options

```
positional arguments:
  fasta_file            Path to FASTA file to benchmark

optional arguments:
  -h, --help            Show help message and exit
  --iterations, -i      Number of iterations per test (default: 100)
  --random-access, -r   Number of random access operations (default: 50)
  --max-sequences, -s   Maximum sequences for iteration test (default: 10)
  --sequence            Specific sequence name to test (default: first sequence)
```

## Example Output

```
Benchmarking file: genome.fasta
File size: 245.67 MB

Benchmarking file opening...
Benchmarking sequence access...
Benchmarking sequence slicing (1000:1100)...
Benchmarking get_seq method calls...
Benchmarking reverse complement operations...
Benchmarking iteration over first 10 sequences...
Benchmarking random access (50 random slices)...

================================================================================
BENCHMARK RESULTS
================================================================================

File Opening
------------
Library      Mean (ms)    Median (ms)    Min (ms)   Max (ms)   StdDev    
----------------------------------------------------------------------
pyfaidx      245.678      243.123        201.456    312.789    23.456    
raidx        12.345       11.987         9.876      18.654     1.987     

Speedup: 19.91x faster
raidx is 19.91x faster than pyfaidx

Sequence Slicing
----------------
Library      Mean (ms)    Median (ms)    Min (ms)   Max (ms)   StdDev    
----------------------------------------------------------------------
pyfaidx      8.765        8.432          7.123      12.456     0.987     
raidx        0.432        0.398          0.287      0.765      0.098     

Speedup: 20.29x faster
raidx is 20.29x faster than pyfaidx

...
```

## Understanding the Results

### Metrics Explained

- **Mean**: Average time across all iterations
- **Median**: Middle value when times are sorted (less affected by outliers)
- **Min/Max**: Fastest and slowest individual times
- **StdDev**: Standard deviation (lower values indicate more consistent performance)
- **Speedup**: How many times faster one library is compared to the other

### What to Expect

Generally, you can expect:

- **raidx** to be significantly faster for most operations due to Rust's performance
- **File opening** to show the biggest differences (index parsing and memory mapping)
- **Sequence slicing** to show substantial improvements
- **Random access** patterns to benefit greatly from raidx optimizations

### Performance Tips

1. **Use larger iteration counts** (`--iterations 1000+`) for more reliable statistics
2. **Test with your actual data** - performance can vary significantly based on:
   - File size
   - Number of sequences
   - Sequence lengths
   - Access patterns
3. **Consider file system caching** - run benchmarks multiple times and look at subsequent runs
4. **Test different access patterns** with `--random-access` and `--max-sequences`

## Benchmark Test Descriptions

### File Opening
Times the initialization of FASTA objects, including index reading/creation.

### Sequence Access
Measures time to access a sequence by name and get its length.

### Sequence Slicing
Tests extracting subsequences using Python slice notation `[start:end]`.

### get_seq Method
Benchmarks the `get_seq(name, start, end)` method calls.

### Reverse Complement
Tests computing reverse complements using the `-sequence` operator.

### Iteration
Measures time to iterate through multiple sequences in the file.

### Random Access
Tests random access patterns with multiple sequences and coordinates.

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure both libraries are installed
   ```bash
   pip install pyfaidx
   pip install .  # for raidx
   ```

2. **File Not Found**: Ensure your FASTA file path is correct
   ```bash
   ls -la your_file.fasta
   ```

3. **Index Issues**: If you get index-related errors, try rebuilding:
   ```bash
   rm your_file.fasta.fai  # Remove old index
   python benchmark_raidx.py your_file.fasta  # Will rebuild automatically
   ```

4. **Memory Issues**: For very large files, reduce the number of iterations:
   ```bash
   python benchmark_raidx.py large_file.fasta --iterations 10
   ```

### Performance Considerations

- **SSD vs HDD**: Performance will vary significantly based on storage type
- **Available RAM**: Large files may benefit from more available memory
- **File compression**: Compressed FASTA files (.gz) may show different performance patterns
- **Python version**: Newer Python versions may show better performance

## Contributing

If you find issues or want to add new benchmark tests:

1. Test cases should be in the `FastaBenchmark` class
2. Follow the existing pattern of timing functions multiple iterations
3. Add results to the `BenchmarkResults` class
4. Include appropriate metadata for context

## License

This benchmark tool is provided under the same license as the raidx project. 