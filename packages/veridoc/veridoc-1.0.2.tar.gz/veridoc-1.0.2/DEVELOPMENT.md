# VeriDoc Development Guide

This guide covers development setup, testing, and contribution workflows for VeriDoc.

## Development Setup

### Prerequisites
- Python 3.8 or higher
- Git for version control
- Modern browser for testing

### Environment Setup
```bash
# Clone repository
git clone https://github.com/benny-bc-huang/veridoc.git
cd veridoc

# Install dependencies
pip install -r requirements-dev.txt

# Install package in development mode
pip install -e .

# Run development server
python app.py
# OR
veridoc
```

## Architecture Overview

VeriDoc follows a clean architecture with separate concerns:

```
/root/veridoc/
├── veridoc/                 # Main package
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # Module execution entry
│   ├── cli.py              # Command-line interface
│   ├── server.py           # FastAPI server
│   ├── core/               # Backend modules
│   │   ├── security.py     # Security manager
│   │   ├── file_handler.py # File operations
│   │   ├── config.py       # Configuration
│   │   └── ...             # Other core modules
│   ├── models/             # API models
│   ├── frontend/           # Web application
│   └── completions/        # Shell completions
├── tests/                  # Test suite
├── docs/                   # Documentation
├── app.py                  # Development entry point
├── pyproject.toml          # Package configuration
└── requirements*.txt       # Dependencies
```

### Technology Stack
- **Backend**: Python FastAPI with async support
- **Frontend**: Vanilla HTML/CSS/JavaScript (no frameworks)
- **Terminal Integration**: xterm.js with WebSocket proxy
- **Content Rendering**: Markdown with Mermaid diagram support
- **Search Engine**: Custom indexing with caching optimization
- **Security**: Multi-layer validation and audit logging

## Development Commands

### Server Management
```bash
# Development server (recommended)
python app.py                # Start at localhost:5000

# CLI integration
./veridoc                    # Launch VeriDoc
./veridoc docs/              # Open specific directory
./veridoc README.md          # Open specific file

# Module execution
python -m veridoc            # Alternative server start
```

### Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/unit/ -v          # Unit tests
python -m pytest tests/integration/ -v   # Integration tests
python -m pytest tests/security/ -v      # Security tests

# Coverage report
python -m pytest --cov=veridoc tests/
```

### Quality Assurance
```bash
# Code formatting
black veridoc/ tests/
isort veridoc/ tests/

# Linting
flake8 veridoc/ tests/

# Type checking
mypy veridoc/
```

### API Testing
```bash
# Health check
curl http://localhost:5000/api/health

# File operations
curl http://localhost:5000/api/files
curl http://localhost:5000/api/files?path=docs

# Search functionality
curl "http://localhost:5000/api/search?q=VeriDoc&type=both&limit=5"

# Git integration
curl http://localhost:5000/api/git/status
```

## Development Phases

VeriDoc was developed in 5 phases:

1. **Phase 1**: ✅ Core documentation MVP with backend APIs and frontend layout
2. **Phase 2**: ✅ Enhanced documentation features (pagination, navigation, search)
3. **Phase 3**: ✅ CLI integration, terminal features, and enhanced code support
4. **Phase 4**: ✅ Open source preparation, comprehensive testing, and production polish
5. **Phase 5**: ✅ Open source release preparation: easy installation & clean documentation

## Performance Targets

All targets have been met and are maintained:

- **Application startup**: < 2 seconds ✅
- **File loading**: < 500ms for typical files ✅
- **Search response**: < 200ms across 1000+ files ✅
- **Large file pagination**: Smooth 10MB+ handling ✅
- **Memory usage**: < 100MB total ✅
- **Browser response time**: < 100ms for navigation ✅

## Security Model

- **File Access**: All operations restricted to BASE_PATH with comprehensive validation
- **Path Security**: Path traversal prevention with symbolic link detection
- **Input Validation**: Sanitization and length limits for all API parameters
- **Terminal Security**: Command filtering with whitelist/blacklist policies
- **Audit Logging**: Complete activity logs in `./logs/terminal_audit.log` and `./logs/error.log`
- **Session Management**: Terminal session isolation with automatic cleanup

## Git Workflow

**IMPORTANT**: Always use git for code changes. Follow this workflow:

### Before Making Changes
```bash
git status              # Check current state
git diff               # Review uncommitted changes
git log --oneline -5   # Check recent commits
```

### After Making Changes
```bash
git add .                              # Stage all changes
git commit -m "type(scope): message"   # Commit with descriptive message
git push origin main                   # Push to GitHub
```

### Commit Message Format
- **feat**: new feature
- **fix**: bug fix
- **docs**: documentation changes
- **style**: code style changes
- **refactor**: code refactoring
- **test**: test additions/changes
- **chore**: maintenance tasks

### Examples
```bash
git commit -m "feat(search): add fuzzy search algorithm"
git commit -m "fix(security): resolve path traversal vulnerability"
git commit -m "docs(readme): update installation instructions"
```

## Test Suite Status

**Target: 100% Test Pass Rate** ✅ **ACHIEVED**:

- **SecurityManager Tests**: ✅ 100% passing (26/26)
- **FileHandler Tests**: ✅ 100% passing (21/21)
- **GitIntegration Tests**: ✅ 100% passing (23/23)
- **Overall Unit Tests**: ✅ **100% passing (70/70)**

### Running Specific Tests
```bash
# Focus on specific components
python -m pytest tests/unit/test_security.py -v
python -m pytest tests/unit/test_file_handler.py -v
python -m pytest tests/unit/test_git_integration.py -v

# Test markers
python -m pytest -m unit        # Unit tests only
python -m pytest -m integration # Integration tests
python -m pytest -m security    # Security tests
python -m pytest -m git         # Git-related tests
```

## Troubleshooting

### Server Won't Start
```bash
# Check for port conflicts
lsof -i :5000

# Verify dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.8+
```

### Tests Failing
```bash
# Update test dependencies
pip install -r requirements-dev.txt

# Clear Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -delete

# Ensure pytest-asyncio is available
pip install pytest-asyncio
```

### Package Installation Issues
```bash
# Reinstall in development mode
pip uninstall veridoc
pip install -e .

# Check package structure
python -c "import veridoc; print(veridoc.__file__)"
```

## Contributing Guidelines

1. **Fork the repository** on GitHub
2. **Create a feature branch** from main
3. **Make your changes** following code style guidelines
4. **Add tests** for new functionality
5. **Run the test suite** to ensure nothing breaks
6. **Update documentation** if needed
7. **Submit a pull request** with a clear description

### Code Style
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Write docstrings for public functions
- Keep functions focused and small
- Use meaningful variable names

### Testing Guidelines
- Write tests for all new features
- Ensure test coverage remains high
- Use descriptive test names
- Mock external dependencies
- Test both success and error cases

## IDE Integration

### VS Code Settings
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black"
}
```

### PyCharm Configuration
- Set project interpreter to your virtual environment
- Configure pytest as test runner
- Enable black as code formatter
- Set up flake8 for linting

## Performance Monitoring

VeriDoc includes built-in performance monitoring:

```python
# Access performance metrics
from veridoc.core.performance_monitor import performance_monitor

# Get current metrics
metrics = performance_monitor.get_metrics()
print(f"Memory usage: {metrics['memory_mb']}MB")
print(f"Active requests: {metrics['active_requests']}")
```

## Deployment

### Production Setup
```bash
# Install production dependencies only
pip install veridoc

# Set environment variables
export BASE_PATH=/path/to/docs
export PORT=8080

# Run with production server
veridoc --port 8080 --no-browser
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "-m", "veridoc"]
```

## Support and Contact

- **Issues**: [GitHub Issues](https://github.com/benny-bc-huang/veridoc/issues)
- **Discussions**: GitHub Discussions
- **Documentation**: `/docs` directory
- **Email**: dev@veridoc.dev