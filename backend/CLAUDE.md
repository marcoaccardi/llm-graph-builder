# Backend Development Guide

This guide provides comprehensive instructions for working with the Python backend of the Hygent Knowledge Graph Platform.

**IMPORTANT: All responses and code comments MUST be in English only. Do not use Chinese or any other language.**

**For general project information, Docker setup, and architecture overview, see the main `CLAUDE.md` in the project root.**

ALWAYS USE Context7 MCP to use updated syntax for a specific library
---
## Backend documentation and report 
always put reports and backend related md files in `backend/docs`

Always organize test files in the `backend/tests` directory
## 📋 Quick Reference

- **Language**: Python 3.11+
- **Package Manager**: UV
- **Virtual Environment**: `.venv` (located in `backend/`)
- **Testing Framework**: pytest
- **Code Formatter**: black
- **Import Sorter**: isort
- **Type Checker**: mypy
- **Validation**: pydantic v2



# Activate environment
source .venv/bin/activate 



# Run commands in the environment
uv run python script.py
uv run python -m pytest


**Use Local UV development when:**
- You need maximum debugging control and performance
- Working in resource-constrained environments
- Doing rapid prototyping without container overhead
- You have specific local tooling requirements

### Testing & Quality Commands


#### Local UV Development (PRIMARY)

```bash
# From backend/ directory with activated venv

# Run all tests
uv run python -m pytest

# Run specific test categories
uv run python -m pytest tests/unit/          # Unit tests
uv run python -m pytest tests/integration/   # Integration tests

# Run tests with verbose output
uv run python -m pytest -v

# Run tests with extra verbose output for debugging
uv run python -m pytest -vvs

# Run tests and stop on first failure
uv run python -m pytest -x

# Run tests with coverage
uv run python -m pytest --cov=app

# Generate HTML coverage report
uv run python -m pytest --cov=app --cov-report=html

# Format code
uv run black .

# Sort imports
uv run isort .

# Type checking
uv run mypy app/

# Run all quality checks
uv run black . && uv run isort . && uv run mypy app/ && uv run python -m pytest
```


## 🧱 Code Structure & Modularity

### File and Function Limits

- **Never create a file longer than 500 lines of code**. If approaching this limit, refactor by splitting into modules.
- **Functions should be under 50 lines** with a single, clear responsibility.
- **Classes should be under 100 lines** and represent a single concept or entity.
- **Organize code into clearly separated modules**, grouped by feature or responsibility.
- **Line length should be max 100 characters** (configured in development tools)

### Import Conventions

- **Prefer relative imports within packages** (e.g., `from .seed import SessionSeed`)
- This is the established pattern in the codebase - maintain consistency
- Use absolute imports only when importing from external packages

## 📋 Python Style & Conventions

### Python Style Guide

- **Follow PEP8** with these specific choices:
  - Line length: 100 characters
  - Use double quotes for strings
  - Use trailing commas in multi-line structures
- **Always use type hints** for function signatures and class attributes
- **Format with `black`** for consistent code style
- **Sort imports with `isort`**
- **Type check with `mypy`**
- **Use `pydantic` v2** for data validation when applicable

### Naming Conventions

- **Variables and functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private attributes/methods**: `_leading_underscore`
- **Type aliases**: `PascalCase`
- **Enum values**: `UPPER_SNAKE_CASE`
## 🧪 Testing Strategy

### Test-Driven Development (TDD)

1. **Write the test first** - Define expected behavior before implementation
2. **Watch it fail** - Ensure the test actually tests something
3. **Write minimal code** - Just enough to make the test pass
4. **Refactor** - Improve code while keeping tests green
5. **Repeat** - One test at a time

### Testing Best Practices
## 🛡️ Security Best Practices

### Security Guidelines

- Never commit secrets - use environment variables
- Validate all user input with Pydantic
- Use parameterized queries for database operations (if applicable)
- Implement rate limiting for APIs
- Keep dependencies updated with `uv pip install --upgrade`
- Use HTTPS for all external communications
- Implement proper authentication and authorization for WebSocket connections



### Time Profiling

```bash
# Detailed time profiling
uv run python -m cProfile -o profile.stats script.py
uv run python -m pstats profile.stats

# Line-by-line timing
uv run python -m line_profiler script.py
```

### GPU Debugging

```bash
# GPU status and memory usage
uv run python scripts/debug_gpu.py
uv run python scripts/debug_gpu.py --detailed
uv run python scripts/debug_gpu.py --processes
uv run python scripts/debug_gpu.py --json
```




### Enhanced Debugging Commands

```bash
# Debug with enhanced tracebacks
uv run python -X dev script.py  # Enable development mode

# Check process memory usage
ps aux | grep python
htop

# Monitor file changes during development
uv run python -m watchdog script.py

# Debug with pdb (built-in)
python -m pdb script.py
```

---
### Essential Tools

- UV Documentation: https://github.com/astral-sh/uv
- Black: https://github.com/psf/black
- isort: https://pycqa.github.io/isort/
- MyPy: https://mypy.readthedocs.io/
- Pytest: https://docs.pytest.org/
- Pydantic: https://docs.pydantic.dev/
- FastAPI: https://fastapi.tiangolo.com/
- NumPy: https://numpy.org/doc/

### Python Best Practices

- PEP 8: https://pep8.org/
- PEP 484 (Type Hints): https://www.python.org/dev/peps/pep-0484/
- The Hitchhiker's Guide to Python: https://docs.python-guide.org/

## ✅ Backend Development Checklist

Before committing backend code, ensure:

- [ ] Code is formatted with `black`
- [ ] Imports are sorted with `isort`
- [ ] Type hints are present on all functions
- [ ] All tests pass (`uv run python -m pytest`)
- [ ] Type checking passes (`uv run mypy app/`)
- [ ] Test coverage is maintained or improved
- [ ] Docstrings are present for public functions
- [ ] No secrets are committed
