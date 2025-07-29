# VeriDoc Core Functions Reference

This document provides detailed implementation reference for VeriDoc's core functions to enable rapid development without codebase scanning.

## Overview

VeriDoc's architecture is built around four core components that handle security, file operations, Git integration, and API serving. Understanding these components enables efficient feature development and debugging.

## SecurityManager (`veridoc/core/security.py`)

**Primary Function**: Multi-layer path validation and security enforcement with enterprise-grade protection

### Constructor
```python
SecurityManager(base_path: Union[str, Path])
```
- Validates and resolves base path
- Raises `ValueError` if base path doesn't exist or isn't a directory

### Core Methods

#### `validate_path(user_path: str) -> Path`
**Purpose**: Main validation method for all path-based operations
**Returns**: Resolved safe path within base directory
**Raises**: `ValueError` for invalid/unsafe paths

**Security Features**:
- **Multi-level URL Decoding**: Detects up to 3 levels (`%252e%252e%252f` → `../`)
- **Unicode Normalization**: NFD/NFC processing to catch decomposed characters
- **Unicode Lookalike Detection**: Converts fullwidth chars (`．．／`) to ASCII
- **Null Byte Protection**: Blocks `\x00` and `%00` injection attempts
- **Path Canonicalization**: Advanced normalization with traversal detection
- **Symlink Validation**: Ensures symlinks point within base directory

**Usage Pattern**:
```python
try:
    safe_path = security_manager.validate_path(user_input)
    # Use safe_path for all subsequent operations
except ValueError as e:
    if "outside base directory" in str(e):
        raise SecurityError(f"Path traversal attempt: {user_input}")
    raise PermissionError(f"Invalid path: {user_input}")
```

#### `_normalize_and_decode_path(user_path: str) -> str`
**Purpose**: Advanced evasion detection (internal method)
**Features**: 
- Recursive URL decoding (max 3 levels)
- Unicode normalization (NFD → NFC)
- Suspicious character detection

#### `is_safe_filename(filename: str) -> bool`
**Purpose**: Filename validation
**Checks**: Dangerous characters (`<>:"|?*\x00`), Windows reserved names (`CON`, `PRN`, etc.)

#### `validate_file_size(size_bytes: int) -> bool`
**Purpose**: File size validation (default limit: 50MB)

#### `validate_file_extension(filename: str) -> bool`
**Purpose**: Extension allowlist validation
**Allowed Extensions**: `.md`, `.txt`, `.py`, `.js`, `.json`, `.yaml`, code files, config files

## FileHandler (`veridoc/core/file_handler.py`)

**Primary Function**: Secure file operations with metadata, pagination, and categorization
**Constructor**: `FileHandler(security_manager: SecurityManager)`

### Core Async Methods

#### `list_directory(dir_path: Path, include_hidden=False, sort_by="name", sort_order="asc") -> List[FileItem]`
**Purpose**: Directory listing with metadata and sorting
**Returns**: List of `FileItem` objects

**Features**:
- Security validation via `SecurityManager`
- Hidden file filtering
- Sorting by name/size/modified
- Directory-first ordering
- Item count for directories

**Usage**:
```python
items = await file_handler.list_directory(
    Path("/docs"), 
    include_hidden=True, 
    sort_by="modified", 
    sort_order="desc"
)
```

#### `get_file_content(file_path: Path, page=1, lines_per_page=1000, encoding="utf-8") -> FileContentResponse`
**Purpose**: File content retrieval with pagination
**Returns**: `FileContentResponse` with content, metadata, and pagination info

**Features**:
- Async file reading with `aiofiles`
- Large file pagination (1000 lines/page default)
- Encoding support
- Line count and page calculation
- MIME type detection

**Usage**:
```python
content = await file_handler.get_file_content(
    Path("README.md"), 
    page=2, 
    lines_per_page=500
)
```

#### `get_file_metadata(file_path: Path) -> Dict[str, Any]`
**Purpose**: Comprehensive file metadata
**Returns**: Dictionary with size, modified, created, permissions, line count, MIME type

### File Categorization

#### `get_file_category(file_path: Path) -> str`
**Purpose**: File type classification for rendering
**Returns**: `"markdown"`, `"diagram"`, `"text"`, `"code"`, `"image"`, `"unknown"`

**Category Rules**:
- **Markdown**: `.md`, `.markdown`, `.mdown`, `.mkd`
- **Diagram**: `.mmd`, `.mermaid`
- **Text**: `.txt`, `.text`, `.log`, dotfiles without extension
- **Code**: 40+ programming language extensions
- **Image**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`

#### `_is_text_file(file_path: Path) -> bool`
**Purpose**: Text file detection (internal method)
**Logic**: Extension check + MIME type detection

## GitIntegration (`veridoc/core/git_integration.py`)

**Primary Function**: Git operations for documentation change tracking
**Constructor**: `GitIntegration(base_path)`

### Properties

#### `is_git_repository: bool`
**Usage**: Property access (not method call)
**Purpose**: Check if directory is Git repository
```python
if git_integration.is_git_repository:
    status = await git_integration.get_file_status(file_path)
```

### Async Methods (Main Operations)

#### `get_file_status(file_path: Path) -> Dict[str, Any]`
**Purpose**: Git status for specific file
**Returns**: 
```python
{
    "tracked": bool,
    "status": str,  # "clean", "modified", "added", "deleted", "untracked"
    "modified": bool,
    "staged": bool,
    "index_status": str,
    "working_status": str
}
```

#### `get_file_history(file_path: Path, limit=10) -> List[Dict[str, Any]]`
**Purpose**: Commit history for file
**Returns**: List of commit dictionaries with hash, author, date, message

#### `get_file_diff(file_path: Path, commit_hash=None) -> str`
**Purpose**: Git diff for file
**Returns**: Diff string (against HEAD if no commit specified)

#### `get_repository_info() -> Dict[str, Any]`
**Purpose**: Repository metadata
**Returns**: current_branch, remote_url, commit_count, last_commit, modified_files

### Sync Methods (Testing Support)

#### `get_git_status() -> Optional[Dict[str, Any]]`
**Purpose**: Repository status (synchronous for tests)
**Returns**: `{"modified": [], "untracked": [], "added": [], "deleted": [], "branch": str, "clean": bool}`

#### `get_git_log(limit=10, file_path=None) -> Optional[List[Dict]]`
**Purpose**: Commit log (synchronous for tests)

#### `get_git_diff(file_path=None, commit_hash=None) -> Optional[str]`
**Purpose**: Git diff (synchronous for tests)

#### `get_current_branch() -> Optional[str]`
**Purpose**: Current branch name (synchronous for tests)

## API Server (`veridoc/server.py`)

**Framework**: FastAPI with async support, error handling, and WebSocket integration

### Key API Endpoints

#### `GET /api/files`
**Purpose**: Directory listing
**Parameters**: `path`, `include_hidden`, `sort_by`, `sort_order`
**Handler Chain**: `get_files()` → `SecurityManager.validate_path()` → `FileHandler.list_directory()`
**Returns**: `FileListResponse`

#### `GET /api/file_content`
**Purpose**: File content with pagination
**Parameters**: `path`, `page`, `lines_per_page`, `encoding`
**Handler Chain**: `get_file_content()` → `SecurityManager.validate_path()` → `FileHandler.get_file_content()`
**Returns**: `FileContentResponse` or `FileResponse` for binary files

#### `GET /api/search`
**Purpose**: File and content search
**Parameters**: `q`, `type`, `path`, `extensions`, `limit`
**Features**: Filename/content search, relevance scoring, extension filtering
**Algorithm**: Exact match (1.0) → Starts with (0.9) → Contains (0.7) → Content match (0.4-0.6)

#### `WebSocket /ws/terminal/{terminal_id}`
**Purpose**: Terminal integration
**Features**: PTY management, command filtering, session security
**Handler**: `TerminalManager` with `TerminalSecurityManager`

### Data Models (`veridoc/models/api_models.py`)

#### `FileItem`
```python
name: str
type: str  # "file" | "directory"
size: int
modified: datetime
extension: Optional[str]
is_readable: bool
item_count: Optional[int]  # for directories
```

#### `FileContentResponse`
```python
path: str
content: str
metadata: FileMetadata
pagination: PaginationInfo
```

#### `FileListResponse`
```python
path: str
parent: str
items: List[FileItem]
total_items: int
```

## Common Development Patterns

### 1. Secure Path Handling Pattern
```python
# ALWAYS validate paths first
try:
    safe_path = security_manager.validate_path(user_input)
except ValueError as e:
    if "outside base directory" in str(e):
        raise SecurityError(f"Path traversal attempt: {user_input}")
    raise PermissionError(f"Invalid path: {user_input}")

# Then use safe_path for all operations
content = await file_handler.get_file_content(safe_path)
```

### 2. Git Repository Check Pattern
```python
# Use property access, NOT method call
if git_integration.is_git_repository:  # ✅ Correct
    status = await git_integration.get_file_status(file_path)

# NOT: git_integration.is_git_repository()  # ❌ Wrong
```

### 3. Async File Operations Pattern
```python
# Use async methods for I/O
async with aiofiles.open(validated_path, 'r', encoding='utf-8') as f:
    lines = await f.readlines()

# For directory operations
items = await file_handler.list_directory(safe_path)
```

### 4. Error Handling Pattern
```python
# API endpoint pattern
@handle_async_api_error
async def api_endpoint():
    try:
        safe_path = security_manager.validate_path(path)
        result = await file_handler.some_operation(safe_path)
        return result
    except ValueError as e:
        if "outside base directory" in str(e):
            raise SecurityError(f"Path traversal: {path}")
        raise ValidationError(f"Invalid path: {path}")
```

### 5. File Category-Based Processing
```python
category = file_handler.get_file_category(file_path)
if category == "markdown":
    # Apply markdown rendering
elif category == "code":
    # Apply syntax highlighting
elif category == "text":
    # Apply plain text rendering
```

## Testing Patterns

### Security Testing
```python
# Test path traversal protection
with pytest.raises(ValueError, match="Path traversal"):
    security_manager.validate_path("../../../etc/passwd")
```

### Async Testing
```python
@pytest.mark.asyncio
async def test_file_operations():
    content = await file_handler.get_file_content(Path("test.md"))
    assert content.metadata.line_count > 0
```

### Git Integration Testing
```python
def test_git_status():
    # Use sync methods for testing
    status = git_integration.get_git_status()
    assert status is not None
    assert "branch" in status
```

## Performance Considerations

1. **Path Validation**: SecurityManager validation is CPU-intensive due to multiple encoding/normalization steps
2. **File Content**: Large files are paginated to avoid memory issues
3. **Directory Listing**: Directory traversal uses async iteration
4. **Git Operations**: Both async (main) and sync (testing) versions available
5. **Search**: Simple string matching algorithm optimized for sub-200ms response

## Extension Points

1. **New File Types**: Add extensions to `FileHandler` category dictionaries
2. **Search Enhancement**: Replace simple search in `/api/search` with `OptimizedSearchEngine`
3. **Security Rules**: Extend `SecurityManager` validation rules
4. **Git Features**: Add new methods to `GitIntegration` for additional Git operations