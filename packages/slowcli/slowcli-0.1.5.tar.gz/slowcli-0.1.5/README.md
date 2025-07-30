# SlowCLI

A deliberately slow CLI application with complex argument structures, heavy imports, and nested arguments. This project demonstrates various advanced argparse and argcomplete features while simulating real-world slow startup scenarios.

## Features

- **Complex Argument Structures**: Nested subcommands with multiple levels
- **Dynamic Arguments**: Arguments that change based on context and previous inputs
- **Heavy Imports**: Simulates slow startup with heavy library imports
- **Auto-completion**: Full argcomplete integration for enhanced UX
- **Nested Arguments**: Deep argument hierarchies with conditional logic
- **Multiple Output Formats**: JSON, YAML, CSV, and human-readable output
- **Async Operations**: Simulated async operations for realistic performance

## Installation

### From PyPI (when published)
```bash
pip install slowcli
```

### From Source
```bash
git clone https://github.com/yourusername/slowcli.git
cd slowcli
pip install -e .
```

## Usage

### Basic Commands

```bash
# Main help
slowcli --help

# Data processing with complex options
slowcli data process --input large_file.csv --format json --compress gzip --validate

# Network operations with nested arguments
slowcli network scan --targets 192.168.1.0/24 --ports 80,443,8080 --timeout 30 --retries 3

# Analysis with dynamic arguments
slowcli analyze --algorithm ml --model-type random-forest --features auto --cross-validate
```

### Advanced Features

#### Auto-completion
```bash
# Enable auto-completion for bash
eval "$(register-python-argcomplete slowcli)"

# For zsh
eval "$(register-python-argcomplete slowcli)"
```

#### Complex Nested Commands
```bash
# Deep nested command structure
slowcli data process --input file.csv \
    --transform normalize \
    --filter "column > 100" \
    --output processed.json \
    --format json \
    --compress gzip \
    --validate \
    --log-level debug
```

## Command Structure

```
slowcli
├── data
│   ├── process
│   ├── analyze
│   ├── transform
│   └── export
├── network
│   ├── scan
│   ├── monitor
│   └── test
├── analyze
│   ├── ml
│   ├── stats
│   └── visualize
└── system
    ├── info
    ├── monitor
    └── optimize
```

## Configuration

The application supports configuration through:
- Environment variables
- Configuration files (YAML, TOML, JSON)
- Command-line arguments (highest priority)

## Performance Characteristics

This CLI is intentionally slow to simulate real-world scenarios:
- **Startup Time**: 2-5 seconds (heavy imports)
- **Command Processing**: 1-3 seconds per command
- **Complex Operations**: 5-15 seconds for data processing

## Development

### Setup Development Environment
```bash
git clone https://github.com/yourusername/slowcli.git
cd slowcli
pip install -e ".[dev]"
```

### Running Tests
```bash
pytest tests/
```

### Building for Distribution
```bash
python setup.py sdist bdist_wheel
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Why "Slow"?

This CLI is designed to demonstrate:
- Real-world startup delays from heavy imports
- Complex argument parsing scenarios
- Performance optimization techniques
- User experience considerations for slow applications

Perfect for testing and benchmarking CLI performance tools!
