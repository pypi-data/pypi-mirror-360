# VeriDoc Architecture Specification

<div align="center">
  <img src="../../logo-dark.png" alt="VeriDoc Logo" width="80" height="80">
</div>

## System Overview

VeriDoc is a lightweight, web-based documentation browser designed for AI-assisted development workflows. The architecture prioritizes performance, security, and simplicity.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Helper    │    │   Web Browser   │    │   Terminal      │
│   (veridoc)     │    │   (Frontend)    │    │   (xterm.js)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   HTTP Server   │
                    │   (Backend)     │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   File System   │
                    │   (BASE_PATH)   │
                    └─────────────────┘
```

## Core Principles

### 1. **Verification-First Design**
- Read-only architecture optimized for document viewing
- No editing capabilities to maintain simplicity
- Fast content rendering prioritized over feature richness

### 2. **Performance Independence**
- Response times constant regardless of documentation volume
- Memory usage bounded regardless of project size
- Sub-500ms target for all user interactions

### 3. **Security by Design**
- All file access restricted to BASE_PATH
- Path traversal prevention at multiple layers
- Input validation and sanitization throughout

### 4. **Minimal Dependencies**
- Vanilla JavaScript frontend (no frameworks)
- Lightweight backend with minimal external dependencies
- Self-contained deployment model

## Architecture Components

### Backend Server

#### Technology Stack
**Production Implementation**: FastAPI (Python) with async support
- Type hints for automatic API documentation
- Excellent performance for I/O bound operations
- Built-in validation and serialization
- WebSocket support for terminal integration
- Async/await support for concurrent operations

**Alternative**: Express.js (Node.js)
- Single-language stack
- NPM ecosystem for utilities
- Native JSON handling

#### Core Modules

```python
veridoc/
├── app.py              # FastAPI application entry point
├── api/
│   ├── __init__.py
│   ├── files.py        # File system API endpoints
│   ├── search.py       # Search functionality
│   ├── terminal.py     # WebSocket terminal proxy
│   └── health.py       # Health check and metrics
├── core/
│   ├── __init__.py
│   ├── security.py              # Path validation and sanitization
│   ├── terminal_security.py     # Terminal command filtering
│   ├── file_handler.py          # File system operations
│   ├── search_optimization.py   # Search indexing engine
│   ├── performance_monitor.py   # Real-time metrics
│   ├── enhanced_error_handling.py # Exception management
│   ├── git_integration.py       # Git operations
│   └── config.py               # Configuration management
├── models/
│   ├── __init__.py
│   ├── api_models.py   # Pydantic models for API
│   └── file_models.py  # File metadata models
├── tests/
│   ├── __init__.py
│   ├── conftest.py     # Test fixtures
│   ├── test_unit/      # Unit tests
│   ├── test_integration/ # Integration tests
│   └── test_security/  # Security tests
└── utils/
    ├── __init__.py
    ├── logging.py      # Structured logging
    └── performance.py  # Performance monitoring
```

#### Security Layer (Production Implementation)
```python
class SecurityManager:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path).resolve()
    
    def validate_path(self, user_path: str) -> Path:
        """Validate path is within BASE_PATH"""
        # Normalize and resolve path
        # Check for path traversal
        # Validate against BASE_PATH
        # Reject symbolic links
        
    def sanitize_input(self, user_input: str) -> str:
        """Sanitize user input for security"""
        # Remove null bytes
        # Escape special characters
        # Validate length limits

class TerminalSecurityManager:
    def __init__(self):
        self.whitelist_patterns = [...]  # Allowed commands
        self.blacklist_patterns = [...]  # Dangerous patterns
        
    def validate_command(self, command: str) -> bool:
        """Validate terminal commands for safety"""
        # Check against whitelist/blacklist
        # Log security events
        # Return validation result
```

### Frontend Application

#### Technology Stack
- **Vanilla JavaScript** (ES6+)
- **CSS Grid/Flexbox** for layout
- **Web Components** for reusable UI elements
- **Marked.js** for Markdown rendering
- **Mermaid.js** for diagram rendering
- **xterm.js** for terminal integration

#### Component Architecture

```
frontend/
├── index.html          # Main application shell
├── css/
│   ├── main.css        # Global styles
│   ├── layout.css      # Layout-specific styles
│   └── components.css  # Component styles
├── js/
│   ├── app.js          # Main application logic
│   ├── components/
│   │   ├── file-tree.js    # File tree component
│   │   ├── content-viewer.js # Content display
│   │   ├── terminal.js     # Terminal integration
│   │   └── search.js       # Search functionality
│   ├── services/
│   │   ├── api.js          # API client
│   │   ├── file-service.js # File operations
│   │   └── cache.js        # Client-side caching
│   └── utils/
│       ├── markdown.js     # Markdown processing
│       ├── url-handler.js  # URL routing
│       └── performance.js  # Performance monitoring
└── assets/
    ├── icons/          # UI icons
    └── fonts/          # Web fonts
```

#### Core Components

**FileTree Component**
```javascript
class FileTree {
    constructor(container, apiService) {
        this.container = container;
        this.api = apiService;
        this.cache = new Map();
    }
    
    async loadDirectory(path) {
        // Load directory contents
        // Update tree structure
        // Handle caching
    }
    
    render() {
        // Render expandable tree
        // Handle click events
        // Update selection state
    }
}
```

**ContentViewer Component**
```javascript
class ContentViewer {
    constructor(container, apiService) {
        this.container = container;
        this.api = apiService;
        this.renderers = {
            'md': new MarkdownRenderer(),
            'mmd': new MermaidRenderer(),
            'txt': new TextRenderer()
        };
    }
    
    async displayFile(path, lineNumber = null) {
        // Load file content
        // Determine renderer
        // Display content
        // Handle line navigation
    }
}
```

### CLI Integration

#### Helper Script Architecture
```bash
#!/usr/bin/env python3
# veridoc CLI helper script

import sys
import webbrowser
import subprocess
from pathlib import Path

class VeriDocCLI:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.server_port = 5000
        
    def ensure_server_running(self):
        # Check if server is running
        # Start server if needed
        # Wait for server to be ready
        
    def open_file(self, file_path, line_number=None):
        # Construct URL
        # Open in browser
        # Handle fallbacks
        
    def open_directory(self, dir_path):
        # Construct directory URL
        # Open in browser
```

## Data Flow

### File Loading Flow
```
1. User clicks file in tree
2. Frontend sends GET /api/file_content
3. Backend validates path
4. Backend reads file with pagination
5. Backend returns content + metadata
6. Frontend determines renderer
7. Frontend displays content
8. Frontend updates URL history
```

### Search Flow
```
1. User enters search query
2. Frontend sends GET /api/search
3. Backend performs file/content search
4. Backend returns ranked results
5. Frontend displays results
6. User clicks result
7. Frontend loads selected file
```

### Terminal Integration Flow
```
1. User opens terminal panel
2. Frontend establishes WebSocket connection
3. User enters command
4. Frontend sends command via WebSocket
5. Backend executes command in shell
6. Backend streams output via WebSocket
7. Frontend displays output in terminal
```

## Performance Architecture

### Caching Strategy

**Client-Side Caching**
- File content cached in memory (LRU eviction)
- Directory listings cached for 60 seconds
- Search results cached for 30 seconds

**Server-Side Caching**
- File metadata cached in memory
- Directory scans cached for 10 seconds
- Search index updated incrementally

### Memory Management
```python
class MemoryManager:
    def __init__(self, max_memory_mb=100):
        self.max_memory = max_memory_mb * 1024 * 1024
        self.cache = {}
        self.access_times = {}
    
    def get_memory_usage(self):
        # Monitor current memory usage
        # Return usage statistics
        
    def evict_if_needed(self):
        # Check memory usage
        # Evict least recently used items
        # Free up memory
```

### Performance Monitoring
```javascript
class PerformanceMonitor {
    constructor() {
        this.metrics = {
            pageLoadTime: 0,
            apiResponseTimes: [],
            memoryUsage: 0,
            renderTimes: []
        };
    }
    
    measureApiCall(endpoint, duration) {
        // Record API response time
        // Calculate moving averages
        // Detect performance regressions
    }
    
    reportMetrics() {
        // Send metrics to backend
        // Log performance data
        // Trigger alerts if needed
    }
}
```

## Security Architecture

### Multi-Layer Security

**Layer 1: Input Validation**
- All user input validated at entry points
- Path parameters sanitized and normalized
- Query parameters type-checked and bounded

**Layer 2: Path Security**
- BASE_PATH enforcement at filesystem level
- Symbolic link detection and rejection
- Real path resolution and validation

**Layer 3: Access Control**
- Read-only file system access
- No write operations permitted
- System file permissions respected

### Security Implementation
```python
class PathValidator:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path).resolve()
    
    def is_safe_path(self, user_path: str) -> bool:
        try:
            # Normalize path
            normalized = Path(user_path).resolve()
            
            # Check if within base path
            normalized.relative_to(self.base_path)
            
            # Check for symbolic links
            if normalized.is_symlink():
                return False
                
            return True
        except (ValueError, OSError):
            return False
```

## Error Handling Architecture

### Error Categories

**User Errors (4xx)**
- Invalid paths
- Malformed requests
- Rate limit exceeded

**System Errors (5xx)**
- File system errors
- Memory exhaustion
- Network issues

### Error Handling Strategy
```python
class ErrorHandler:
    def handle_user_error(self, error: UserError):
        # Log error details
        # Return user-friendly message
        # Suggest corrective action
        
    def handle_system_error(self, error: SystemError):
        # Log full error details
        # Return generic error message
        # Trigger monitoring alerts
```

## Deployment Architecture

### Local Development
```
┌─────────────────┐
│   Developer     │
│   Machine       │
│                 │
│ ┌─────────────┐ │
│ │   VeriDoc   │ │
│ │   Server    │ │
│ │ localhost:  │ │
│ │   5000      │ │
│ └─────────────┘ │
└─────────────────┘
```

### Production Deployment
```
┌─────────────────┐
│   User Machine  │
│                 │
│ ┌─────────────┐ │
│ │   VeriDoc   │ │
│ │   Binary    │ │
│ │   (Packaged │ │
│ │   with docs)│ │
│ └─────────────┘ │
└─────────────────┘
```

## Scalability Considerations

### File System Scalability
- Directory listing pagination for large directories
- Lazy loading of file tree branches
- Incremental search indexing
- Background file metadata caching

### Memory Scalability
- Bounded memory usage regardless of project size
- LRU cache eviction for file content
- Streaming for large file rendering
- Garbage collection optimization

### Network Scalability
- Content compression for large files
- Efficient pagination for API responses
- WebSocket connection management
- Request batching for directory operations

## Monitoring and Observability

### Metrics Collection
```python
class MetricsCollector:
    def __init__(self):
        self.metrics = {
            'request_count': 0,
            'response_times': [],
            'memory_usage': 0,
            'error_count': 0,
            'cache_hit_rate': 0.0
        }
    
    def record_request(self, endpoint, duration, status):
        # Record request metrics
        # Update moving averages
        # Detect anomalies
```

### Health Monitoring
- API endpoint health checks
- Memory usage monitoring
- File system access validation
- Performance regression detection

### Logging Strategy
```python
import logging
import structlog

# Structured logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = structlog.get_logger()

# Usage
logger.info("File accessed", path="/docs/api.md", duration_ms=150)
logger.error("Path validation failed", path="../../etc/passwd", user_ip="127.0.0.1")
```

## Future Architecture Considerations

### Plugin Architecture
- Renderer plugin system for custom file types
- Theme plugin support
- Custom search provider integration

### Microservices Evolution
- Search service separation
- Content rendering service
- Terminal service isolation

### Performance Optimization
- Content delivery network integration
- Advanced caching strategies
- Database backend for large projects