# Contributing to VeriDoc

Thank you for your interest in contributing to VeriDoc! This guide will help you get started.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/benny-bc-huang/veridoc.git
   cd veridoc
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For linting and testing
   ```

3. **Run tests**
   ```bash
   python -m pytest tests/unit/ -v  # Core functionality tests
   ```

## Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow existing code style and patterns
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run unit tests (required)
   python -m pytest tests/unit/ -v
   
   # Test the application locally
   python app.py
   # Visit http://localhost:5000
   ```

4. **Format your code** (optional but recommended)
   ```bash
   black .
   isort .
   flake8 .
   ```

## Pull Request Process

1. **Ensure tests pass**: All unit tests must pass
2. **Write clear commit messages**: Use conventional commit format
3. **Update documentation**: If you change functionality
4. **Small, focused PRs**: Easier to review and merge

## Testing Notes

- **Unit tests**: Always required and must pass
- **Integration tests**: Currently disabled due to dependency conflicts (httpx/FastAPI versions)
- **Local testing**: Please test the application manually in your browser

## Code Style

- Follow existing patterns in the codebase
- Use type hints where possible
- Keep functions focused and well-documented
- Follow Python PEP 8 style guidelines

## Need Help?

- Check the [README.md](README.md) for project overview
- Look at existing code for examples
- Open an issue for questions or bug reports

Thank you for contributing! 🚀