# VeriDoc v1.0.1 Release Notes

## 🎉 First Official Release

We're excited to announce the first official release of VeriDoc - an AI-optimized documentation browser designed for rapid development workflows.

## 📦 Installation

```bash
pip install veridoc
```

## ✨ Key Features

### Core Functionality
- **⚡ Ultra-fast Performance**: Sub-500ms startup, <200ms response times
- **📱 Three-Pane Interface**: File tree, content viewer, and integrated terminal
- **🔍 Full-Text Search**: Global search across all documentation files
- **🎨 Rich Rendering**: Markdown, Mermaid diagrams, syntax highlighting for 30+ languages
- **📄 Large File Support**: Pagination for files over 1MB
- **🔐 Enterprise Security**: Multi-layer path validation and audit logging

### Recent Enhancements
- **👁️ Dot Files Support**: Toggle hidden files visibility in file tree
- **📋 Log File Rendering**: Proper display of `.log` files as plain text
- **🎨 Professional Branding**: VeriDoc logo integration across the application
- **📸 Interface Screenshots**: Visual documentation in README

## 🛡️ Security Features

- Advanced path traversal protection against:
  - Double/triple URL encoding attacks
  - Unicode normalization bypass attempts
  - Null byte injection
  - Symbolic link escapes
- Comprehensive audit logging for all terminal operations
- Command filtering with whitelist/blacklist policies

## 🚀 Performance Metrics

- **Startup Time**: < 500ms
- **File Loading**: < 500ms for typical files
- **Search Response**: < 200ms across 1000+ files
- **Memory Usage**: < 100MB total
- **Large Files**: Smooth handling of 10MB+ files with pagination

## 📋 Development Status

- **Test Coverage**: 100% unit test pass rate (124/124 tests passing)
- **Python Support**: 3.8, 3.9, 3.10, 3.11
- **Platform Support**: Windows, macOS, Linux
- **License**: MIT

## 🔧 Technical Stack

- **Backend**: FastAPI with async support
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Terminal**: xterm.js with WebSocket integration
- **Search**: Custom indexing with caching
- **Security**: Multi-layer validation system

## 📚 Documentation

- [GitHub Repository](https://github.com/benny-bc-huang/veridoc)
- [README](https://github.com/benny-bc-huang/veridoc#readme)
- [Bug Reports](https://github.com/benny-bc-huang/veridoc/issues)

## 🙏 Acknowledgments

VeriDoc includes the following open-source dependencies:
- FastAPI, Pydantic (MIT License)
- uvicorn, psutil (BSD 3-Clause)
- aiofiles, python-multipart (Apache 2.0)
- python-json-logger (BSD 2-Clause)
- watchfiles (Multi-licensed)

---

**Full Changelog**: https://github.com/benny-bc-huang/veridoc/commits/v1.0.1