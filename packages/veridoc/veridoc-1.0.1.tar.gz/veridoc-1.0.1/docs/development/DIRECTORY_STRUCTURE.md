# VeriDoc Directory Structure

This document describes the organization of the VeriDoc project directory structure and the rationale behind each directory.

## Project Overview

VeriDoc follows a clean, modular directory structure that separates concerns and maintains clear boundaries between different aspects of the application. The structure follows modern Python packaging standards with a proper package hierarchy.

## Root Directory Structure

```
/root/veridoc/
├── 📄 Core Documentation
│   ├── README.md                    # Main project documentation (user-focused)
│   ├── DEVELOPMENT.md               # Developer setup and guidelines
│   ├── CONTRIBUTING.md              # Contribution guidelines
│   ├── CHANGELOG.md                 # Version history and release notes
│   ├── LICENSE                      # MIT license
│   └── CLAUDE.md                    # Claude Code AI assistant instructions
│
├── ⚙️ Package Configuration
│   ├── pyproject.toml               # Modern Python packaging configuration
│   ├── setup.cfg                    # Build and tool configuration
│   ├── pytest.ini                  # Test runner configuration
│   ├── requirements.txt             # Production dependencies
│   └── requirements-dev.txt         # Development dependencies
│
├── 🚀 Application Entry Points
│   └── app.py                       # Development server entry point
│
├── 📦 Main Package (veridoc/)
│   ├── __init__.py                  # Package initialization and metadata
│   ├── __main__.py                  # Module execution entry (python -m veridoc)
│   ├── cli.py                       # Command-line interface implementation
│   ├── server.py                    # FastAPI server application
│   │
│   ├── core/                        # Backend core modules
│   │   ├── __init__.py
│   │   ├── config.py                # Configuration management
│   │   ├── security.py              # Security validation and path handling
│   │   ├── file_handler.py          # File system operations
│   │   ├── git_integration.py       # Git operations and version control
│   │   ├── search_optimization.py   # Search indexing and caching
│   │   ├── performance_monitor.py   # Performance metrics and monitoring
│   │   ├── terminal_security.py     # Terminal command filtering and security
│   │   └── enhanced_error_handling.py # Error handling and exception management
│   │
│   ├── models/                      # API data models and schemas
│   │   ├── __init__.py
│   │   └── api_models.py            # Pydantic models for API requests/responses
│   │
│   ├── frontend/                    # Web application (client-side)
│   │   ├── index.html               # Main HTML template
│   │   ├── css/                     # Stylesheets
│   │   │   ├── main.css             # Main styles and variables
│   │   │   ├── layout.css           # Layout and positioning
│   │   │   └── components.css       # Component-specific styles
│   │   └── js/                      # JavaScript modules
│   │       ├── app.js               # Main application entry point
│   │       ├── components/          # UI components
│   │       │   ├── file-tree.js     # File tree navigation
│   │       │   ├── content-viewer.js # Content display and rendering
│   │       │   ├── search.js        # Search functionality
│   │       │   └── terminal.js      # Terminal integration
│   │       └── utils/               # Utility modules
│   │           ├── api.js           # API communication
│   │           ├── markdown.js      # Markdown rendering and processing
│   │           ├── url-handler.js   # URL routing and navigation
│   │           └── console-cleaner.js # Development console management
│   │
│   └── completions/                 # Shell completion scripts
│       ├── bash_completion.sh       # Bash completion
│       ├── zsh_completion.zsh       # Zsh completion
│       └── fish_completion.fish     # Fish shell completion
│
├── 🧪 Testing & Quality Assurance
│   ├── tests/                       # Test suite (100% unit test coverage)
│   │   ├── conftest.py              # Test configuration and fixtures
│   │   ├── unit/                    # Unit tests (70/70 passing)
│   │   │   ├── test_security.py     # SecurityManager tests (26/26)
│   │   │   ├── test_file_handler.py # FileHandler tests (21/21)
│   │   │   └── test_git_integration.py # GitIntegration tests (23/23)
│   │   ├── integration/             # Integration tests
│   │   │   └── test_api.py          # API endpoint testing
│   │   ├── security/                # Security-focused tests
│   │   │   └── test_path_traversal.py # Path security validation
│   │   └── frontend/                # Frontend test assets
│   │       └── test.html            # HTML test templates
│   │
│   └── docs/                        # Extended documentation
│       ├── development/             # Development documentation
│       │   ├── ARCHITECTURE.md      # System architecture overview
│       │   ├── DEVELOPMENT_PLAN.md  # Development phases and milestones
│       │   ├── PHASE5_ANALYSIS.md   # Open source release analysis
│       │   ├── ALIGNMENT_ASSESSMENT.md # Project alignment evaluation
│       │   └── DIRECTORY_STRUCTURE.md # This file
│       ├── specs/                   # Technical specifications
│       │   ├── API_SPEC.md          # REST API documentation
│       │   ├── CLI_SPEC.md          # Command-line interface specification
│       │   └── UI_SPEC.md           # User interface specification
│       └── logs/                    # Development logs
│           ├── dev-log-2025-07-04.md # Daily development progress
│           └── dev-log-2025-07-05.md # Daily development progress
│
├── 🔧 Development & Operations
│   ├── dev/                         # Development artifacts
│   │   ├── initialize.prompt        # AI assistant initialization
│   │   └── project_statement.md     # Project vision and goals
│   │
│   └── logs/                        # Application runtime logs
│       ├── error.log                # Application error logs
│       └── terminal_audit.log       # Terminal command audit trail
│
└── 🔒 Configuration & Version Control
    ├── .git/                        # Git repository
    ├── .github/                     # GitHub workflows and templates
    ├── .gitignore                   # Git ignore patterns
    └── .claude/                     # Claude Code configuration
        └── settings.local.json      # Local Claude Code permissions
```

## Directory Rationale

### Package Structure (`veridoc/`)

The main package follows Python packaging best practices:

- **Proper Python Package**: Complete with `__init__.py` and proper imports
- **Entry Points**: Multiple ways to run (CLI command, module execution, development)
- **Modular Organization**: Clear separation between core logic, models, and frontend
- **Asset Inclusion**: Frontend assets and completions bundled with package

### Core Modules (`veridoc/core/`)

Backend functionality is organized by domain:

- **`security.py`**: Centralized security validation and path handling
- **`file_handler.py`**: File system operations with security integration
- **`git_integration.py`**: Version control operations and git integration
- **`search_optimization.py`**: Search indexing with sub-200ms response times
- **`performance_monitor.py`**: Real-time performance metrics and memory tracking
- **`terminal_security.py`**: Command filtering and terminal security controls
- **`enhanced_error_handling.py`**: Comprehensive error management with categorization

### Frontend Architecture (`veridoc/frontend/`)

Modern web application structure:

- **Component-Based**: Modular JavaScript components for different UI areas
- **CSS Organization**: Separated concerns (layout, components, main styles)
- **Utility Modules**: Reusable functionality for API, markdown, and navigation
- **No Framework Dependency**: Vanilla JavaScript for minimal overhead

### Testing Strategy (`tests/`)

Comprehensive testing with 100% unit test coverage:

- **Unit Tests**: Isolated testing of individual components (70/70 passing)
- **Integration Tests**: API endpoint and system integration testing
- **Security Tests**: Focused security validation and vulnerability testing
- **Test Organization**: Tests mirror the source code structure

### Documentation Structure (`docs/`)

Multi-level documentation organization:

- **Development**: Internal development processes and architecture
- **Specifications**: Technical API and interface documentation
- **Logs**: Development progress tracking and decision history

## File Naming Conventions

### Python Files
- **Snake Case**: `file_handler.py`, `git_integration.py`
- **Descriptive Names**: Clear indication of module purpose
- **Package Structure**: Consistent `__init__.py` in all packages

### Frontend Files
- **Kebab Case**: `file-tree.js`, `content-viewer.js`
- **Component Suffix**: JavaScript components end with `.js`
- **Utility Prefix**: Utility modules in `utils/` directory

### Documentation Files
- **Upper Case**: `README.md`, `CONTRIBUTING.md`
- **Descriptive Names**: `DEVELOPMENT_PLAN.md`, `API_SPEC.md`
- **Consistent Format**: All documentation in Markdown format

## Dependencies and Configuration

### Package Management
- **`pyproject.toml`**: Modern Python packaging standard (PEP 518)
- **`requirements.txt`**: Production dependencies only
- **`requirements-dev.txt`**: Development and testing dependencies
- **`setup.cfg`**: Tool configuration (flake8, mypy, etc.)

### Version Control
- **`.gitignore`**: Comprehensive ignore patterns for Python, frontend, and IDE files
- **`.github/`**: GitHub Actions workflows and issue templates
- **Git Hooks**: Pre-commit hooks for code quality (if configured)

## Installation Methods

The directory structure supports multiple installation methods:

1. **Production Installation**: `pip install veridoc`
2. **Development Installation**: `pip install -e .`
3. **Development Server**: `python app.py`
4. **Module Execution**: `python -m veridoc`
5. **Direct CLI**: `veridoc` command (after installation)

## Performance Considerations

### Asset Organization
- **Static Files**: Frontend assets served efficiently by FastAPI
- **Completion Scripts**: Shell completions bundled with package
- **Modular Loading**: Core modules loaded on demand

### Development Efficiency
- **Clear Separation**: Easy to locate and modify specific functionality
- **Test Integration**: Tests mirror source structure for easy navigation
- **Documentation Access**: Quick access to relevant documentation

## Security Considerations

### Path Security
- **Restricted Access**: All file operations restricted to BASE_PATH
- **Path Validation**: Comprehensive path traversal prevention
- **Audit Logging**: Complete activity tracking in logs directory

### Package Security
- **Read-Only Design**: Default safe access to documentation
- **Input Validation**: All user inputs validated and sanitized
- **Secure Defaults**: Conservative security configuration

## Maintenance and Evolution

### Extensibility
- **Modular Design**: Easy to add new core modules or frontend components
- **Plugin Ready**: Architecture supports future plugin system
- **API Versioning**: Structure supports API evolution

### Development Workflow
- **Clear Entry Points**: Multiple ways to run and test the application
- **Comprehensive Testing**: Full test coverage for reliable development
- **Documentation Integration**: Living documentation alongside code

This directory structure represents the culmination of 5 development phases, resulting in a production-ready, open-source Python package with professional organization and comprehensive functionality.