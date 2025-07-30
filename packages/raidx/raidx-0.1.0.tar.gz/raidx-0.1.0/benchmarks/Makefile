# RaidX Benchmarks Makefile
# Common commands for running benchmarks

.PHONY: help install bench bench-fast bench-full bench-save bench-compare clean

help:  ## Show this help message
	@echo "RaidX Benchmarks"
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install benchmark dependencies
	@echo "Installing benchmark dependencies..."
	pip install -e ".[benchmark]"

bench:  ## Run standard benchmarks (excludes slow tests)
	@echo "Running standard benchmarks..."
	pytest benchmarks/ -m "not slow" --benchmark-only -v

bench-fast:  ## Run quick benchmarks only
	@echo "Running quick benchmarks..."
	pytest benchmarks/ -m "not slow" --benchmark-only --benchmark-min-rounds=3 --benchmark-max-time=1.0

bench-full:  ## Run all benchmarks including slow tests
	@echo "Running full benchmark suite..."
	pytest benchmarks/ --benchmark-only -v

bench-save:  ## Run benchmarks and save results as baseline
	@echo "Running benchmarks and saving as baseline..."
	pytest benchmarks/ -m "not slow" --benchmark-only --benchmark-save=baseline

bench-compare:  ## Run benchmarks and compare to baseline
	@echo "Running benchmarks and comparing to baseline..."
	pytest benchmarks/ -m "not slow" --benchmark-only --benchmark-compare=baseline

bench-ci:  ## Run benchmarks suitable for CI (fast, with comparison)
	@echo "Running CI benchmarks..."
	pytest benchmarks/ -m "not slow" --benchmark-only --benchmark-compare-fail=min:15%,mean:10%

file-ops:  ## Run only file operation benchmarks
	@echo "Running file operation benchmarks..."
	pytest benchmarks/benchmark_file_ops.py --benchmark-only -v

sequence-ops:  ## Run only sequence operation benchmarks
	@echo "Running sequence operation benchmarks..."
	pytest benchmarks/benchmark_sequence_ops.py --benchmark-only -v

clean:  ## Clean generated test data and reports
	@echo "Cleaning benchmark data..."
	rm -rf benchmarks/data/*.fasta
	rm -rf benchmarks/data/*.fai
	rm -rf benchmarks/reports/*.json

clean-reports:  ## Clean only benchmark reports
	@echo "Cleaning benchmark reports..."
	rm -rf benchmarks/reports/*.json

list-reports:  ## List available benchmark reports
	@echo "Available benchmark reports:"
	@ls -la benchmarks/reports/ || echo "No reports found"

# CLI benchmarks (original tool)
cli-demo:  ## Run the original demo benchmark
	@echo "Running original benchmark demo..."
	python demo_benchmark.py

cli-bench:  ## Run CLI benchmark (requires FASTA file)
	@echo "Usage: make cli-bench FILE=your_file.fasta"
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify a FASTA file with FILE=path/to/file.fasta"; \
		exit 1; \
	fi
	python benchmark_raidx.py $(FILE)

# Development targets
dev-install:  ## Install development dependencies
	@echo "Installing development dependencies..."
	pip install -e ".[dev]"

test:  ## Run unit tests (not benchmarks)
	@echo "Running unit tests..."
	pytest tests/ -v

test-all:  ## Run both unit tests and benchmarks
	@echo "Running all tests..."
	pytest tests/ benchmarks/ -v

# Example targets for specific use cases
example-small:  ## Example: benchmark small files
	@echo "Benchmarking small files..."
	pytest benchmarks/ -k "small" --benchmark-only -v

example-comparison:  ## Example: direct library comparison
	@echo "Comparing raidx vs pyfaidx..."
	pytest benchmarks/ --benchmark-only --benchmark-group-by=func -v

example-histogram:  ## Example: generate performance histograms
	@echo "Generating histograms..."
	pytest benchmarks/ --benchmark-only --benchmark-histogram=benchmarks/reports/histogram

# Documentation
docs:  ## Show benchmark documentation
	@echo "Benchmark documentation:"
	@echo "  Structure: benchmarks/README.md"
	@echo "  Original:  BENCHMARK_README.md"
	@echo ""
	@echo "Quick start:"
	@echo "  make install    # Install dependencies"
	@echo "  make bench      # Run standard benchmarks"
	@echo "  make bench-save # Save baseline"
	@echo ""
	@echo "For more options, see: make help" 