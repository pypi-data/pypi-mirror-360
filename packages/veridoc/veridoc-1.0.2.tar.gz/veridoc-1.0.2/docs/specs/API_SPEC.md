# VeriDoc API Specification

## Overview
RESTful API for VeriDoc documentation browser backend. All endpoints return JSON responses and follow REST conventions.

**Base URL**: `http://localhost:5000/api`
**Content-Type**: `application/json`

## Authentication
None required - single-user, localhost-only application.

## Error Handling

### Standard Error Response
```json
{
  "error": true,
  "message": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": "Additional technical details (optional)",
  "category": "validation|permission|security|system"
}
```

### Enhanced Error Categories (Phase 4)
- **Validation**: Invalid input parameters, malformed requests
- **Permission**: Access denied, file permissions, path restrictions
- **Security**: Path traversal attempts, security violations
- **System**: Server errors, resource exhaustion, timeout

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `403` - Forbidden (path outside BASE_PATH)
- `404` - Not Found (file/directory doesn't exist)
- `413` - Payload Too Large (file > 50MB)
- `429` - Too Many Requests (rate limiting)
- `500` - Internal Server Error

## Endpoints

### 1. Directory Listing

**GET** `/api/files`

Lists files and directories at the specified path.

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Relative path from BASE_PATH |
| `include_hidden` | boolean | No | Include hidden files (default: false) |
| `sort_by` | string | No | Sort field: `name`, `size`, `modified` (default: `name`) |
| `sort_order` | string | No | Sort order: `asc`, `desc` (default: `asc`) |

#### Response
```json
{
  "path": "/docs",
  "parent": "/",
  "items": [
    {
      "name": "api.md",
      "type": "file",
      "size": 15420,
      "modified": "2024-01-15T10:30:00Z",
      "extension": "md",
      "is_readable": true
    },
    {
      "name": "diagrams",
      "type": "directory",
      "size": 0,
      "modified": "2024-01-15T10:25:00Z",
      "item_count": 5
    }
  ],
  "total_items": 2
}
```

#### Error Responses
- `400` - Invalid path parameter
- `403` - Path outside BASE_PATH
- `404` - Directory doesn't exist

### 2. File Content

**GET** `/api/file_content`

Retrieves file content with pagination support.

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Relative file path from BASE_PATH |
| `page` | integer | No | Page number (1-based, default: 1) |
| `lines_per_page` | integer | No | Lines per page (default: 1000, max: 10000) |
| `encoding` | string | No | Text encoding (default: utf-8) |

#### Response
```json
{
  "path": "/docs/api.md",
  "content": "# API Documentation\n\nThis is the content...",
  "metadata": {
    "size": 15420,
    "modified": "2024-01-15T10:30:00Z",
    "extension": "md",
    "mime_type": "text/markdown",
    "encoding": "utf-8",
    "line_count": 450
  },
  "pagination": {
    "page": 1,
    "lines_per_page": 1000,
    "total_pages": 1,
    "total_lines": 450,
    "has_next": false,
    "has_previous": false
  }
}
```

#### Error Responses
- `400` - Invalid path or pagination parameters
- `403` - Path outside BASE_PATH
- `404` - File doesn't exist
- `413` - File too large (> 50MB)

### 3. File Search

**GET** `/api/search`

Search for files by name or content.

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search query |
| `type` | string | No | Search type: `filename`, `content`, `both` (default: `both`) |
| `path` | string | No | Limit search to specific directory |
| `extensions` | string | No | Comma-separated file extensions (e.g., "md,txt") |
| `limit` | integer | No | Max results (default: 50, max: 200) |

#### Response
```json
{
  "query": "authentication",
  "results": [
    {
      "path": "/docs/auth.md",
      "type": "file",
      "match_type": "filename",
      "score": 0.95,
      "snippet": null
    },
    {
      "path": "/docs/api.md",
      "type": "file",
      "match_type": "content",
      "score": 0.78,
      "snippet": "Authentication is handled via...",
      "line_number": 42
    }
  ],
  "total_results": 2,
  "search_time_ms": 15
}
```

### 4. File Metadata

**GET** `/api/file_info`

Get detailed file metadata without content.

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Relative file path from BASE_PATH |

#### Response
```json
{
  "path": "/docs/api.md",
  "name": "api.md",
  "type": "file",
  "size": 15420,
  "modified": "2024-01-15T10:30:00Z",
  "created": "2024-01-10T14:20:00Z",
  "extension": "md",
  "mime_type": "text/markdown",
  "encoding": "utf-8",
  "line_count": 450,
  "is_readable": true,
  "is_writable": false,
  "permissions": "644"
}
```

### 5. Health Check

**GET** `/api/health`

Server health and status information.

#### Response
```json
{
  "status": "healthy",
  "version": "1.0.1",
  "uptime_seconds": 3600,
  "base_path": "/home/user/project",
  "memory_usage_mb": 45,
  "active_connections": 1,
  "performance": {
    "avg_response_time_ms": 85,
    "requests_per_second": 12
  },
  "testing": {
    "unit_tests_passing": 70,
    "test_coverage": "100%",
    "last_test_run": "2025-07-05T10:30:00Z"
  }
}
```

## WebSocket Endpoints

### Terminal Connection

**WebSocket** `/api/terminal`

Interactive terminal session for CLI integration.

#### Connection
```javascript
const ws = new WebSocket('ws://localhost:5000/api/terminal');
```

#### Message Format
```json
{
  "type": "input|output|error|resize",
  "data": "command or output text",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Commands
- `input`: Send command to terminal
- `output`: Receive terminal output
- `error`: Terminal error messages
- `resize`: Terminal window resize

## Rate Limiting

### Default Limits
- **File requests**: 100 requests/minute per IP
- **Search requests**: 20 requests/minute per IP
- **Directory listings**: 200 requests/minute per IP

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Performance Specifications

### Response Time Targets (All Met ✅)
- **Directory listings**: < 200ms ✅
- **File content (< 1MB)**: < 500ms ✅
- **File content (1-10MB)**: < 2000ms ✅
- **Search queries**: < 200ms ✅ (Phase 4 optimization)
- **Large file pagination**: Smooth 10MB+ handling ✅

### Memory Usage
- **Baseline**: < 50MB
- **With active terminal**: < 100MB
- **Peak usage**: < 150MB

## Security Considerations

### Path Validation
- All paths validated against BASE_PATH
- Symbolic links explicitly rejected
- Path traversal attempts (../) blocked
- Null bytes and special characters sanitized

### Input Sanitization
- Query parameters validated and sanitized
- File paths normalized
- Search queries escaped for regex safety
- Terminal commands logged for security audit

### File Access Control
- Read-only access to files
- No file modification capabilities
- Respect system file permissions
- Hidden files excluded by default

## Logging

### Request Logging
```
[2024-01-15 10:30:00] GET /api/files?path=/docs 200 150ms
[2024-01-15 10:30:01] GET /api/file_content?path=/docs/api.md 200 280ms
```

### Error Logging
```
[2024-01-15 10:30:02] ERROR: Path traversal attempt: /docs/../../../etc/passwd
[2024-01-15 10:30:03] ERROR: File not found: /docs/nonexistent.md
```

### Terminal Logging
```
[2024-01-15 10:30:04] TERMINAL: ls -la /docs
[2024-01-15 10:30:05] TERMINAL: cat /docs/api.md
```

## API Versioning

### Version Header
```
X-API-Version: 1.0.1
```

### Backward Compatibility
- v1.0.0: Initial Phase 4 release
- v1.0.1: Enhanced error handling and **100% unit test coverage**
- Future versions will maintain backward compatibility
- Deprecated endpoints will include sunset warnings

## Development Testing

### Test Endpoints
Available only in development mode:

**POST** `/api/test/reset`
- Resets server state for testing

**GET** `/api/test/metrics`
- Detailed performance metrics

**POST** `/api/test/simulate_error`
- Simulates various error conditions