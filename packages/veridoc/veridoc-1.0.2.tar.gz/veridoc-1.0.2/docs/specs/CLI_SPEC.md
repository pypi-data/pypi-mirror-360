# VeriDoc CLI Specification

## Overview

The VeriDoc CLI provides seamless integration with AI-assisted development workflows by enabling instant documentation access from the terminal. The CLI helper script ensures sub-second documentation access while maintaining developer flow state.

## Core Philosophy

### Zero-Context-Switch Design
- **Instant Access**: Documentation available in < 1 second
- **Terminal-Native**: Direct integration with command-line workflows
- **Flow State Preservation**: No disruption to AI development momentum
- **Command-Line First**: Optimized for terminal-based development

## CLI Command Structure

### Basic Syntax
```bash
veridoc [OPTIONS] [PATH] [LINE_NUMBER]
```

### Command Examples
```bash
# Open documentation browser at current directory
veridoc

# Open specific file
veridoc docs/api.md

# Open file at specific line
veridoc docs/api.md 42

# Open directory
veridoc docs/

# Open file with options
veridoc --port 8080 docs/guide.md

# Search for documentation
veridoc --search "authentication"

# Start server only (no browser)
veridoc --server-only --port 5000
```

## Command-Line Options

### Global Options
```bash
Options:
  -h, --help              Show help message and exit
  -v, --version           Show version information
  -p, --port PORT         Server port (default: 5000)
  -H, --host HOST         Server host (default: localhost)
  -b, --browser BROWSER   Browser to use (default: system default)
  -s, --server-only       Start server without opening browser
  -q, --quiet             Suppress output messages
  -d, --debug             Enable debug mode
  --no-terminal           Disable integrated terminal
  --config FILE           Configuration file path
```

### Search Options
```bash
Search Options:
  --search QUERY          Search for files/content
  --search-type TYPE      Search type: filename, content, both
  --search-limit N        Maximum search results (default: 50)
  --search-extensions EXT Comma-separated extensions to search
```

### Server Options
```bash
Server Options:
  --base-path PATH        Base directory for file access
  --max-file-size SIZE    Maximum file size to display (default: 50MB)
  --cache-size SIZE       Cache size in MB (default: 100MB)
  --log-level LEVEL       Log level: debug, info, warning, error
  --log-file FILE         Log file path
```

## Usage Patterns

### AI Development Integration
```bash
# Quick verification during AI development
veridoc docs/api-spec.md 42

# Project documentation overview
veridoc docs/

# Integration with AI workflow patterns
alias verify="veridoc"
alias docs="veridoc docs/"
alias api="veridoc docs/api/"

# Combine with other tools
veridoc $(find docs -name "*.md" | fzf)
```

### Development Workflow Examples
```bash
# After AI implements feature, verify against docs
claude code "implement user authentication"
veridoc docs/security-guidelines.md

# Quick context gathering for AI
veridoc docs/architecture.md
claude code "add new API endpoint following our patterns"

# Rapid documentation cross-reference
veridoc docs/api.md &
veridoc docs/database.md &
# Both open in tabs, instant access
```

## Command Implementation

### Helper Script Structure
```python
#!/usr/bin/env python3
"""
VeriDoc CLI Helper Script
Provides instant documentation access for AI-assisted development
"""

import sys
import os
import time
import subprocess
import webbrowser
import argparse
from pathlib import Path
from urllib.parse import quote
import requests

class VeriDocCLI:
    def __init__(self):
        self.default_port = 5000
        self.default_host = "localhost"
        self.base_url = f"http://{self.default_host}:{self.default_port}"
        self.server_process = None
        
    def main(self):
        """Main CLI entry point"""
        parser = self.create_parser()
        args = parser.parse_args()
        
        try:
            if args.command == 'search':
                self.handle_search(args)
            elif args.command == 'server':
                self.handle_server(args)
            else:
                self.handle_open(args)
        except KeyboardInterrupt:
            self.cleanup()
            sys.exit(0)
        except Exception as e:
            self.error(f"Error: {e}")
            sys.exit(1)
    
    def create_parser(self):
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            description='VeriDoc - AI-Optimized Documentation Browser',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  veridoc                     # Open current directory
  veridoc docs/api.md         # Open specific file
  veridoc docs/api.md 42      # Open file at line 42
  veridoc --search "auth"     # Search for documentation
  veridoc --server-only       # Start server only
            """
        )
        
        # Global options
        parser.add_argument('-v', '--version', action='version', version='VeriDoc 1.0.0')
        parser.add_argument('-p', '--port', type=int, default=5000, help='Server port')
        parser.add_argument('-H', '--host', default='localhost', help='Server host')
        parser.add_argument('-b', '--browser', help='Browser to use')
        parser.add_argument('-s', '--server-only', action='store_true', help='Start server only')
        parser.add_argument('-q', '--quiet', action='store_true', help='Suppress output')
        parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
        parser.add_argument('--no-terminal', action='store_true', help='Disable terminal')
        parser.add_argument('--config', help='Configuration file')
        
        # Search options
        parser.add_argument('--search', help='Search query')
        parser.add_argument('--search-type', choices=['filename', 'content', 'both'], 
                           default='both', help='Search type')
        parser.add_argument('--search-limit', type=int, default=50, help='Max results')
        parser.add_argument('--search-extensions', help='File extensions to search')
        
        # Server options
        parser.add_argument('--base-path', help='Base directory path')
        parser.add_argument('--max-file-size', help='Maximum file size')
        parser.add_argument('--cache-size', type=int, default=100, help='Cache size in MB')
        parser.add_argument('--log-level', choices=['debug', 'info', 'warning', 'error'],
                           default='info', help='Log level')
        parser.add_argument('--log-file', help='Log file path')
        
        # Positional arguments
        parser.add_argument('path', nargs='?', default='.', help='File or directory path')
        parser.add_argument('line', nargs='?', type=int, help='Line number')
        
        return parser
    
    def handle_open(self, args):
        """Handle file/directory opening"""
        if not self.ensure_server_running(args):
            self.error("Failed to start server")
            return
        
        url = self.construct_url(args.path, args.line)
        
        if not args.server_only:
            self.open_browser(url, args.browser)
        
        if not args.quiet:
            self.info(f"VeriDoc available at: {url}")
    
    def handle_search(self, args):
        """Handle search functionality"""
        if not self.ensure_server_running(args):
            self.error("Failed to start server")
            return
        
        search_url = self.construct_search_url(args.search, args)
        
        if not args.server_only:
            self.open_browser(search_url, args.browser)
        
        if not args.quiet:
            self.info(f"Search results: {search_url}")
    
    def handle_server(self, args):
        """Handle server-only mode"""
        if not self.ensure_server_running(args):
            self.error("Failed to start server")
            return
        
        if not args.quiet:
            self.info(f"VeriDoc server running at: {self.base_url}")
        
        try:
            # Keep server running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.cleanup()
```

### Server Detection and Management
```python
def ensure_server_running(self, args):
    """Ensure VeriDoc server is running"""
    if self.is_server_running():
        if not args.quiet:
            self.info("Server already running")
        return True
    
    return self.start_server(args)

def is_server_running(self):
    """Check if server is already running"""
    try:
        response = requests.get(f"{self.base_url}/api/health", timeout=1)
        return response.status_code == 200
    except:
        return False

def start_server(self, args):
    """Start VeriDoc server"""
    server_cmd = self.build_server_command(args)
    
    try:
        self.server_process = subprocess.Popen(
            server_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=args.base_path or os.getcwd()
        )
        
        # Wait for server to start
        if self.wait_for_server(timeout=10):
            if not args.quiet:
                self.info("Server started successfully")
            return True
        else:
            self.error("Server failed to start within timeout")
            return False
            
    except Exception as e:
        self.error(f"Failed to start server: {e}")
        return False

def wait_for_server(self, timeout=10):
    """Wait for server to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if self.is_server_running():
            return True
        time.sleep(0.1)
    return False
```

### URL Construction
```python
def construct_url(self, path, line=None):
    """Construct URL for file/directory access"""
    # Normalize path
    path = Path(path).resolve()
    
    # Convert to relative path from base
    try:
        rel_path = path.relative_to(Path.cwd())
    except ValueError:
        rel_path = path
    
    # Build URL
    url = f"{self.base_url}/?path={quote(str(rel_path))}"
    
    if line:
        url += f"&line={line}"
    
    return url

def construct_search_url(self, query, args):
    """Construct URL for search"""
    url = f"{self.base_url}/?search={quote(query)}"
    
    if args.search_type != 'both':
        url += f"&type={args.search_type}"
    
    if args.search_limit != 50:
        url += f"&limit={args.search_limit}"
    
    if args.search_extensions:
        url += f"&extensions={quote(args.search_extensions)}"
    
    return url
```

## Configuration System

### Configuration File Format
```yaml
# ~/.veridoc/config.yaml
server:
  port: 5000
  host: localhost
  base_path: null
  max_file_size: 50MB
  cache_size: 100MB
  log_level: info
  log_file: ~/.veridoc/logs/server.log

browser:
  default: system
  options:
    - chrome
    - firefox
    - safari

search:
  default_type: both
  default_limit: 50
  default_extensions: [md, txt, py, js, html, css, json, yaml]

ui:
  theme: dark
  font_size: 14
  show_hidden: false
  auto_expand: true
  terminal_enabled: true

shortcuts:
  quick_docs: "docs/"
  quick_api: "docs/api/"
  quick_guide: "docs/guide/"
```

### Configuration Loading
```python
def load_config(self, config_path=None):
    """Load configuration from file"""
    if config_path is None:
        config_path = Path.home() / ".veridoc" / "config.yaml"
    
    if not config_path.exists():
        return self.default_config()
    
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        self.warning(f"Failed to load config: {e}")
        return self.default_config()
```

## Error Handling

### Error Types and Messages
```python
class VeriDocError(Exception):
    """Base exception for VeriDoc CLI"""
    pass

class ServerError(VeriDocError):
    """Server-related errors"""
    pass

class FileError(VeriDocError):
    """File access errors"""
    pass

class ConfigError(VeriDocError):
    """Configuration errors"""
    pass

def handle_error(self, error):
    """Handle different error types"""
    if isinstance(error, ServerError):
        self.error(f"Server error: {error}")
        self.info("Try: veridoc --debug for more information")
    elif isinstance(error, FileError):
        self.error(f"File error: {error}")
        self.info("Check file path and permissions")
    elif isinstance(error, ConfigError):
        self.error(f"Configuration error: {error}")
        self.info("Check configuration file syntax")
    else:
        self.error(f"Unexpected error: {error}")
```

### User-Friendly Messages
```python
def error(self, message):
    """Print error message"""
    print(f"❌ {message}", file=sys.stderr)

def warning(self, message):
    """Print warning message"""
    print(f"⚠️  {message}", file=sys.stderr)

def info(self, message):
    """Print info message"""
    print(f"ℹ️  {message}")

def success(self, message):
    """Print success message"""
    print(f"✅ {message}")
```

## Platform Support

### Cross-Platform Compatibility
```python
def get_platform_browser(self):
    """Get default browser for platform"""
    platform = sys.platform
    
    if platform == "darwin":  # macOS
        return "open"
    elif platform == "win32":  # Windows
        return "start"
    else:  # Linux and others
        return "xdg-open"

def open_browser(self, url, browser=None):
    """Open URL in browser"""
    if browser:
        webbrowser.get(browser).open(url)
    else:
        webbrowser.open(url)
```

### Environment Detection
```python
def detect_environment(self):
    """Detect development environment"""
    # Check for common development environments
    if os.getenv('CODESPACES'):
        return 'codespaces'
    elif os.getenv('GITPOD_WORKSPACE_ID'):
        return 'gitpod'
    elif os.getenv('REPLIT_DB_URL'):
        return 'replit'
    else:
        return 'local'
```

## Integration Examples

### Shell Integration
```bash
# .bashrc / .zshrc
alias docs="veridoc docs/"
alias api="veridoc docs/api/"
alias guide="veridoc docs/guide/"

# Function for quick documentation access
vd() {
    if [ -z "$1" ]; then
        veridoc .
    else
        veridoc "$1" "$2"
    fi
}

# Function for documentation search
vds() {
    veridoc --search "$1"
}
```

### Git Integration
```bash
# Git hooks integration
# .git/hooks/post-commit
#!/bin/bash
# Show documentation after commits that modify docs
if git diff --name-only HEAD~1 | grep -q "docs/"; then
    veridoc docs/
fi
```

### IDE Integration
```json
// VS Code tasks.json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Open VeriDoc",
            "type": "shell",
            "command": "veridoc",
            "args": ["${workspaceFolder}/docs"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "silent",
                "focus": false,
                "panel": "shared"
            }
        }
    ]
}
```

## Performance Considerations

### Startup Time Optimization
- **Binary packaging**: Single executable for instant startup
- **Dependency caching**: Pre-cache frequently used modules
- **Lazy loading**: Load components only when needed
- **Connection pooling**: Reuse server connections

### Memory Usage
- **Process monitoring**: Track memory usage
- **Garbage collection**: Periodic cleanup
- **Cache management**: Bounded cache sizes
- **Resource limits**: Prevent memory leaks

## Testing Strategy

### Unit Tests
```python
import unittest
from unittest.mock import patch, MagicMock

class TestVeriDocCLI(unittest.TestCase):
    def setUp(self):
        self.cli = VeriDocCLI()
    
    def test_url_construction(self):
        """Test URL construction for various inputs"""
        url = self.cli.construct_url("docs/api.md", 42)
        self.assertIn("path=docs/api.md", url)
        self.assertIn("line=42", url)
    
    def test_server_detection(self):
        """Test server running detection"""
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            self.assertTrue(self.cli.is_server_running())
    
    def test_config_loading(self):
        """Test configuration loading"""
        config = self.cli.load_config()
        self.assertIn('server', config)
        self.assertIn('browser', config)
```

### Integration Tests
```python
class TestCLIIntegration(unittest.TestCase):
    def test_file_opening(self):
        """Test opening files through CLI"""
        # Test with real file
        # Verify server starts
        # Verify browser opens
        # Verify correct URL construction
    
    def test_search_functionality(self):
        """Test search through CLI"""
        # Test search command
        # Verify search results
        # Verify URL construction
```

## Documentation

### Help System
```bash
# Built-in help
veridoc --help

# Command-specific help
veridoc search --help
veridoc server --help

# Examples
veridoc --examples
```

### Man Page
```bash
# System manual page
man veridoc

# Section overview
veridoc(1) - AI-Optimized Documentation Browser
```

## Installation and Distribution

### Installation Methods
```bash
# Via package manager
pip install veridoc
npm install -g veridoc
brew install veridoc

# Direct download
curl -sSL https://github.com/veridoc/veridoc/releases/latest/download/veridoc-linux-amd64 -o veridoc
chmod +x veridoc
mv veridoc /usr/local/bin/

# From source
git clone https://github.com/veridoc/veridoc.git
cd veridoc
make install
```

### Binary Distribution
```bash
# Create platform-specific binaries
make build-linux
make build-macos
make build-windows

# Package for distribution
make package
```

This CLI specification ensures VeriDoc integrates seamlessly with AI-assisted development workflows while maintaining the core principle of zero-context-switch documentation access.