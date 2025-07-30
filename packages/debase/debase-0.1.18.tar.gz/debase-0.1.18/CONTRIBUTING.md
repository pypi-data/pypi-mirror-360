# Contributing to DEBase

Thank you for your interest in contributing to DEBase!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/debase.git
cd debase
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/
```

## Code Style

We use Black for code formatting:
```bash
black src/ tests/
```

And isort for import sorting:
```bash
isort src/ tests/
```

## Project Structure

```
debase/
├── src/debase/           # Main package source code
├── tests/               # Test suite
├── docs/               # Documentation
├── examples/           # Example outputs and usage
├── data/              # Research data (PDFs)
└── scripts/           # Utility scripts
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run the test suite
6. Submit a pull request