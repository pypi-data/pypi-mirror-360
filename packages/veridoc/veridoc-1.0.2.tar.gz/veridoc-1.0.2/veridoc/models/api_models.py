"""
VeriDoc API Models
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class FileItem(BaseModel):
    """File or directory item in listing"""
    name: str
    type: str  # "file" or "directory"
    size: int
    modified: datetime
    extension: Optional[str] = None
    is_readable: bool
    item_count: Optional[int] = None  # For directories

class FileListResponse(BaseModel):
    """Response for directory listing"""
    path: str
    parent: str
    items: List[FileItem]
    total_items: int

class FileMetadata(BaseModel):
    """File metadata information"""
    size: int
    modified: datetime
    extension: Optional[str] = None
    mime_type: str
    encoding: str
    line_count: int

class PaginationInfo(BaseModel):
    """Pagination information"""
    page: int
    lines_per_page: int
    total_pages: int
    total_lines: int
    has_next: bool
    has_previous: bool

class FileContentResponse(BaseModel):
    """Response for file content"""
    path: str
    content: str
    metadata: FileMetadata
    pagination: PaginationInfo

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    uptime_seconds: int
    base_path: str
    memory_usage_mb: int
    active_connections: int

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: bool = True
    message: str
    code: str
    details: Optional[str] = None