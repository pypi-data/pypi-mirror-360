<div align="center">
  <img src="logo-dark.png" alt="VeriDoc Logo" width="120" height="120">
  
  # VeriDoc
  
  **AI-Optimized Documentation Browser for Rapid Development**
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1+-green.svg)](https://fastapi.tiangolo.com/)
  
</div>

VeriDoc is a lightweight, open-source documentation browser designed for AI-assisted development workflows. It provides sub-second documentation access to maintain flow state during rapid development cycles.

## Features

- ⚡ **Ultra-fast startup** (< 500ms) and response times (< 200ms)
- 🪶 **Lightweight** (< 100MB memory) compared to heavy IDEs
- 📚 **Scalable performance** - works with projects of any size
- 🔍 **Full-text search** across all documentation
- 📱 **Three-pane layout** with file tree, content viewer, and terminal
- 🎨 **Rich rendering** - Markdown, Mermaid diagrams, syntax highlighting
- 🖥️ **Terminal integration** with security controls
- 🔐 **Secure** with comprehensive path validation and audit logging

## Screenshots

<div align="center">
  <img src="img/web-page.png" alt="VeriDoc Interface" width="800">
  <p><em>Three-pane interface: file tree, content viewer, and integrated terminal</em></p>
</div>

## Installation

> **Note**: VeriDoc has not yet been published to PyPI. For now, please install from source.

### Install from Source

```bash
# Clone the repository
git clone https://github.com/benny-bc-huang/veridoc.git
cd veridoc

# Install in development mode
pip install -e .

# Or install directly
pip install .
```

### Usage

```bash
# Launch in current directory
veridoc

# Launch with specific directory or file
veridoc docs/
veridoc README.md
veridoc README.md 42  # Jump to line 42
```

### Coming Soon: PyPI Installation

Once published to PyPI, you'll be able to install with:
```bash
pip install veridoc
```

## Quick Start

```bash
# Basic usage
veridoc                    # Current directory
veridoc --port 5001        # Custom port
veridoc --no-browser       # Start without opening browser
veridoc --help             # Show all options

# Development mode
python app.py              # Alternative startup method
```

## User Interface

### Navigation
- **File Tree Panel**: Browse your documentation structure
- **Content Viewer**: Rich rendering with syntax highlighting
- **Terminal Panel**: Integrated command line with security controls

### Keyboard Shortcuts
- `Ctrl+P` / `Ctrl+/` - Global search
- `Ctrl+F` - Find in current file
- `Ctrl+B` - Toggle file tree panel
- `Ctrl+K` - Copy current file path
- `Ctrl+`` ` - Toggle terminal panel

### File Support
- **Markdown**: Enhanced rendering with Mermaid diagrams
- **Code files**: Syntax highlighting for 30+ languages
- **Large files**: Smart pagination for files > 1MB
- **Binary files**: Safe detection and handling

## Use Cases

### AI-Assisted Development
- **Documentation verification** during AI-generated code review
- **Context gathering** for AI prompts and conversations
- **Project understanding** when working with unfamiliar codebases
- **Fast reference lookup** without breaking development flow

### Documentation Browsing
- **Technical documentation** for teams and projects
- **API reference** with fast search and navigation
- **Code documentation** with syntax highlighting
- **Cross-reference lookup** with table of contents

## Performance

VeriDoc is optimized for speed and efficiency:

- **Startup time**: < 500ms (vs 3-8s for heavy IDEs)
- **Memory usage**: < 100MB (vs 200-500MB for IDEs)
- **Search response**: < 200ms across 1000+ files
- **File loading**: < 500ms for typical documentation
- **Large file handling**: Smooth pagination for 10MB+ files

## Security

- **Path validation**: Prevents directory traversal attacks
- **Command filtering**: Terminal security with configurable policies
- **Audit logging**: Complete activity tracking
- **Read-only design**: Safe documentation access by default

## Configuration

VeriDoc works out of the box with sensible defaults. Configuration options:

```bash
# Environment variables
export BASE_PATH=/path/to/docs    # Default: current directory
export PORT=5000                  # Default: 5000

# Runtime options
veridoc --port 8080              # Custom port
veridoc --no-browser             # Headless mode
```

## API Access

VeriDoc provides a REST API for programmatic access:

```bash
# Health check
curl http://localhost:5000/api/health

# List files
curl http://localhost:5000/api/files

# Search
curl "http://localhost:5000/api/search?q=query&limit=10"

# Git status
curl http://localhost:5000/api/git/status
```

## Requirements

- **Python**: 3.8 or higher
- **Operating Systems**: Linux, macOS, Windows
- **Browser**: Any modern browser for the web interface
- **Memory**: Minimum 256MB available RAM

## Project Structure

```
veridoc/
├── veridoc/          # Main Python package
│   ├── cli.py        # Command-line interface
│   ├── server.py     # FastAPI web server
│   ├── core/         # Backend modules (security, file handling, search)
│   ├── models/       # API data models
│   └── frontend/     # Web application (HTML, CSS, JavaScript)
├── tests/            # Test suite (100% unit test coverage)
├── docs/             # Documentation and specifications
├── app.py            # Development server entry point
└── README.md         # This file
```

## Contributing

We welcome contributions! See our [contributing guidelines](CONTRIBUTING.md) for details on:

- Setting up the development environment
- Running tests and quality checks
- Submitting pull requests
- Reporting issues

## Support

- **Documentation**: Complete guides in the `/docs` directory
- **Issues**: Report bugs and feature requests on [GitHub Issues](https://github.com/benny-bc-huang/veridoc/issues)
- **Discussions**: Join conversations on GitHub Discussions

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Project Status

VeriDoc is production-ready with:
- ✅ Core functionality complete
- ✅ Comprehensive test suite (100% unit test coverage)
- ✅ Security audit and validation
- ✅ Performance optimization
- ✅ CI/CD pipeline and quality checks

---

**Made for developers who value speed, simplicity, and flow state in their AI-assisted workflows.**