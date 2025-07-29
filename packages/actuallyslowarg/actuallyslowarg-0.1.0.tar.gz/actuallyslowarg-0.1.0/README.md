# ActuallySlowArg

A really slow CLI tool for testing tab completion with only argcomplete (no fastargsnap).

This project is designed to compare the performance of tab completion between:
- **actuallyslowarg**: Uses only argcomplete (this project)
- **slowarg**: Uses fastargsnap + argcomplete

## Installation

```bash
pip install actuallyslowarg
```

## Usage

```bash
actuallyslowarg <command> [options]
```

### Commands

- `foo` - Run foo command
  - `--bar` - Bar value (integer)
  - `--baz` - Baz option (choices: a, b, c)

- `data` - Run data command
  - `--file` - Input file (string)
  - `--mode` - Mode (choices: fast, slow)

## Performance Testing

This tool is designed to test whether argcomplete alone would provide the same fast completion performance as fastargsnap.

The tool includes:
- Heavy imports (matplotlib, numpy, pandas, sklearn, requests, click)
- 5-second sleep to simulate slow startup
- Early completion detection to avoid heavy imports during completion
- Only argcomplete (no fastargsnap)

## Performance Results

### Completion Speed (Tab Completion)

| Tool | Method | Time | Performance |
|------|--------|------|-------------|
| **slowarg** | fastargsnap + argcomplete | **0.081s** | ⚡ **4x faster** |
| **actuallyslowarg** | argcomplete only | **0.325s** | 🐌 **Baseline** |

### Command Execution Speed

| Tool | Method | Time | Performance |
|------|--------|------|-------------|
| **slowarg** | fastargsnap + argcomplete | **9.9s** | Same |
| **actuallyslowarg** | argcomplete only | **16.4s** | Same |

## Key Findings

- **fastargsnap provides 4x faster completions** than argcomplete alone
- **Parser creation has real overhead** - even for simple parsers
- **JSON parsing is much faster** than Python object creation
- **fastargsnap is worth the complexity** for performance-critical CLI tools

## Development

```bash
# Install in development mode
pip install -e .

# Run tests
pytest

# Format code
black .

# Lint code
flake8
```

## License

MIT License
