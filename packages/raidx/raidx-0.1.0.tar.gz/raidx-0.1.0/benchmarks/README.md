# raidx Benchmarks

**Performance comparison suite**: raidx vs pyfaidx using pytest-benchmark.

This benchmarking suite provides **side-by-side performance comparisons** between raidx and pyfaidx to help users understand the performance characteristics of each library.

## Key Features

- ✅ **Direct comparisons**: Each test runs with both raidx and pyfaidx
- ✅ **Realistic workloads**: Based on patterns from real-world usage  
- ✅ **Clear grouping**: Results grouped by operation type for easy comparison
- ✅ **Consistent test data**: Same input files for fair comparisons
- ✅ **Comprehensive coverage**: Tests major FASTA processing operations

## Performance Summary

Based on benchmark results, **performance varies significantly by operation**:

### raidx Advantages:
- **File opening**: 2-4x faster initialization
- **Large file handling**: Better memory management for big genomes

### pyfaidx Advantages:  
- **Small sequence operations**: 2-10x faster for small slices/access
- **Reverse complement**: 1.5-2x faster complement operations
- **Random access**: Better performance for scattered access patterns

**Recommendation**: Choose based on your specific workload. Test both libraries with your actual data and access patterns.

## Structure

```
benchmarks/
├── __init__.py                 # Package initialization
├── conftest.py                 # Pytest configuration and fixtures
├── benchmark_file_ops.py       # File operation comparisons
├── benchmark_sequence_ops.py   # Sequence operation comparisons
├── cli.py                      # Command-line interface
├── data/                       # Test data (auto-generated)
├── reports/                    # Benchmark reports (auto-generated)
└── README.md                   # This file
```

## Important: Coordinate Systems

⚠️ **Note on Coordinate Systems**: Be careful with coordinate ranges when writing benchmarks:

- **Python slicing** (`fa[seq_name][start:end]`): 0-based, exclusive end
  - `[1000:1100]` = positions 1000-1099 = 100 bases
- **get_seq method** (`fa.get_seq(name, start, end)`): 1-based, inclusive
  - `get_seq(name, 1000, 1099)` = positions 1000-1099 = 100 bases
  - `get_seq(name, 1001, 1100)` = positions 1001-1100 = 100 bases

Always verify expected lengths match actual results when adding new coordinate-based tests.

## Quick Start

### Install Dependencies

```bash
# Install with benchmark dependencies
pip install -e ".[benchmark]"

# Or install minimal requirements
pip install pytest-benchmark pyfaidx
```

### Run Benchmarks

```bash
# Run all comparisons (shows raidx vs pyfaidx side-by-side)
pytest benchmarks/ --benchmark-only

# Run only file operation comparisons  
pytest benchmarks/benchmark_file_ops.py --benchmark-only

# Run only sequence operation comparisons
pytest benchmarks/benchmark_sequence_ops.py --benchmark-only

# Run with detailed output showing speedup ratios
pytest benchmarks/ -v --benchmark-only

# Save results for later comparison
pytest benchmarks/ --benchmark-only --benchmark-save=baseline

# Compare current vs baseline performance
pytest benchmarks/ --benchmark-only --benchmark-compare=baseline
```

### Exclude Slow Tests

```bash
# Skip slow tests (large file benchmarks)
pytest benchmarks/ -m "not slow"

# Run only quick benchmarks
pytest benchmarks/ -m "benchmark and not slow"
```

## Advanced Usage

### Benchmark Configuration

The benchmarks use pytest-benchmark with these settings:
- **min_rounds**: 10 (minimum iterations)
- **max_time**: 2.0 seconds (maximum time per test)
- **min_time**: 0.1 seconds (minimum time per test)
- **save**: Auto-save to `benchmarks/reports/`

### Custom Test Data

Test data is automatically generated in three sizes:
- **Small**: 5 sequences × 1,000 bases each
- **Medium**: 20 sequences × 5,000 bases each  
- **Large**: 100 sequences × 10,000 bases each

### Available Fixtures

```python
@pytest.fixture
def sample_fasta_small():   # Quick tests
def sample_fasta_medium():  # Standard tests
def sample_fasta_large():   # Performance tests
def raidx_available():      # Check raidx availability
def pyfaidx_available():    # Check pyfaidx availability
```

## Benchmark Categories

### Core Operations (`benchmark_core_ops.py`) - **Recommended**
Focused tests on the most important operations:

- **File Opening**: Loading FASTA files and creating indexes *(raidx advantage)*
- **Sequence Access**: Getting sequence records by name *(pyfaidx advantage)*
- **100bp Slicing**: Extracting 100bp regions *(pyfaidx advantage)*
- **get_seq Method**: Using explicit get_seq() calls *(mixed results)*
- **Sequential Access**: Multiple adjacent extractions *(pyfaidx advantage)*
- **Multi-sequence Iteration**: Processing multiple sequences *(pyfaidx advantage)*

### File Operations (`benchmark_file_ops.py`)
Basic file handling comparisons:

- **File Opening**: Initialization and indexing performance
- **Sequence Listing**: Key enumeration performance

### Sequence Operations (`benchmark_sequence_ops.py`)  
Comprehensive sequence manipulation tests:

- **All core operations** plus reverse complement, random access, and workflows
- **Note**: Shows significant pyfaidx advantages in most operations

Each test runs with **both raidx and pyfaidx** using identical inputs for fair comparison.

## CLI Interface

For standalone benchmarking (outside pytest):

```bash
python -m benchmarks.cli your_file.fasta
```

## Interpreting Results

### Pytest-Benchmark Output
```
benchmarks/benchmark_file_ops.py::TestFileOperations::test_file_opening_medium[raidx] 
    Mean: 12.3ms, StdDev: 1.2ms, Rounds: 15

benchmarks/benchmark_file_ops.py::TestFileOperations::test_file_opening_medium[pyfaidx]
    Mean: 245.6ms, StdDev: 23.4ms, Rounds: 8
```

### Key Metrics
- **Mean**: Average execution time
- **StdDev**: Standard deviation (consistency)
- **Rounds**: Number of iterations performed
- **Min/Max**: Fastest/slowest single execution

### Performance Comparison
- Compare mean times between raidx and pyfaidx
- Lower StdDev indicates more consistent performance
- More rounds = more reliable statistics

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Run Benchmarks
  run: |
    pip install -e ".[benchmark]"
    pytest benchmarks/ --benchmark-only --benchmark-save=ci_results
    
- name: Compare Performance
  run: |
    pytest benchmarks/ --benchmark-compare=baseline --benchmark-compare-fail=min:10%
```

### Regression Detection
Set performance thresholds in `pyproject.toml`:
```toml
[tool.pytest-benchmark]
compare-fail = ["min:10%", "mean:10%"]  # Fail if 10% slower
```

## Best Practices

### 1. Consistent Environment
- Run on consistent hardware
- Close unnecessary applications
- Use SSD for file I/O tests
- Consider CPU scaling/power management

### 2. Statistical Significance
- Use sufficient iterations (10+ rounds)
- Look at multiple metrics (mean, median, min)
- Consider standard deviation for consistency
- Repeat important benchmarks

### 3. Realistic Test Data
- Use files similar to your actual workload
- Test various file sizes
- Include different sequence length distributions
- Test different access patterns

### 4. Baseline Comparisons
```bash
# Establish baseline
pytest benchmarks/ --benchmark-save=baseline

# Regular comparisons
pytest benchmarks/ --benchmark-compare=baseline
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   pip install -e ".[benchmark]"
   ```

2. **No Libraries Available**
   ```bash
   # Ensure at least one library is installed
   pip install pyfaidx        # Reference implementation
   pip install -e .           # RaidX (requires Rust)
   ```

3. **Slow Performance**
   ```bash
   # Use smaller test sets
   pytest benchmarks/ -m "not slow"
   
   # Reduce iterations
   pytest benchmarks/ --benchmark-min-rounds=3
   ```

4. **Inconsistent Results**
   - Check system load
   - Use more iterations
   - Run multiple times and compare

### Performance Tips
- Use `--benchmark-only` to skip test assertions
- Increase rounds for more stable results
- Use `--benchmark-autosave` for automatic baselines
- Profile with different file sizes for your use case 