"""
VeriDoc File Handler
File system operations with security validation
"""

import os
import mimetypes
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import aiofiles
import asyncio

from .security import SecurityManager
from ..models.api_models import FileItem, FileContentResponse, FileMetadata, PaginationInfo

class FileHandler:
    """Handles file system operations with security validation"""
    
    def __init__(self, security_manager: SecurityManager):
        self.security = security_manager
        
        # File type categories for rendering priority
        self.markdown_extensions = {".md", ".markdown", ".mdown", ".mkd"}
        self.diagram_extensions = {".mmd", ".mermaid"}
        self.text_extensions = {".txt", ".text", ".log"}
        self.code_extensions = {
            # Top 10 languages (Phase 3 priority)
            ".py", ".js", ".java", ".ts", ".c", ".cpp", ".cs", ".php", ".rb", ".go",
            # Additional common languages
            ".jsx", ".tsx", ".h", ".hpp", ".cc", ".cxx", ".kt", ".swift", ".rs", ".dart",
            # Web technologies
            ".html", ".css", ".scss", ".sass", ".vue", ".svelte",
            # Data/config files
            ".json", ".yaml", ".yml", ".xml", ".toml", ".ini", ".cfg", ".conf",
            # Shell and scripting
            ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd",
            # Other
            ".sql", ".r", ".lua", ".perl", ".vim", ".dockerfile"
        }
        self.image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
    
    async def list_directory(
        self, 
        dir_path: Path, 
        include_hidden: bool = False,
        sort_by: str = "name",
        sort_order: str = "asc"
    ) -> List[FileItem]:
        """
        List directory contents with metadata
        
        Args:
            dir_path: Directory path to list
            include_hidden: Include hidden files/directories
            sort_by: Field to sort by (name, size, modified)
            sort_order: Sort order (asc, desc)
            
        Returns:
            List of FileItem objects
        """
        # Validate path security first
        validated_path = self.security.validate_path(dir_path)
        
        if not validated_path.is_dir():
            raise ValueError("Path is not a directory")
        
        items = []
        
        try:
            for item_path in validated_path.iterdir():
                # Skip hidden files unless requested
                if not include_hidden and item_path.name.startswith('.'):
                    continue
                
                # Get item statistics
                try:
                    stat = item_path.stat()
                    
                    # Determine item type
                    if item_path.is_dir():
                        item_type = "directory"
                        size = 0
                        extension = None
                        # Count items in directory
                        item_count = len([x for x in item_path.iterdir() if not x.name.startswith('.')])
                    else:
                        item_type = "file"
                        size = stat.st_size
                        extension = item_path.suffix.lower() if item_path.suffix else None
                        item_count = None
                    
                    # Create FileItem
                    item = FileItem(
                        name=item_path.name,
                        type=item_type,
                        size=size,
                        modified=datetime.fromtimestamp(stat.st_mtime),
                        extension=extension,
                        is_readable=os.access(item_path, os.R_OK),
                        item_count=item_count
                    )
                    
                    items.append(item)
                
                except (OSError, PermissionError):
                    # Skip items we can't access
                    continue
        
        except PermissionError:
            raise PermissionError("Access denied to directory")
        
        # Sort items
        reverse = sort_order.lower() == "desc"
        
        if sort_by == "name":
            items.sort(key=lambda x: x.name.lower(), reverse=reverse)
        elif sort_by == "size":
            items.sort(key=lambda x: x.size or 0, reverse=reverse)
        elif sort_by == "modified":
            items.sort(key=lambda x: x.modified, reverse=reverse)
        
        # Sort directories first, then files
        items.sort(key=lambda x: x.type != "directory")
        
        return items
    
    async def get_file_content(
        self,
        file_path: Path,
        page: int = 1,
        lines_per_page: int = 1000,
        encoding: str = "utf-8"
    ) -> FileContentResponse:
        """
        Get file content with pagination
        
        Args:
            file_path: Path to file
            page: Page number (1-based)
            lines_per_page: Lines per page
            encoding: Text encoding
            
        Returns:
            FileContentResponse with content and metadata
        """
        # Validate path security first
        validated_path = self.security.validate_path(file_path)
        
        if not validated_path.exists():
            raise FileNotFoundError("File not found")
        
        if not validated_path.is_file():
            raise ValueError("Path is not a file")
        
        # Get file metadata
        stat = validated_path.stat()
        
        # Read file content
        async with aiofiles.open(validated_path, 'r', encoding=encoding) as f:
            lines = await f.readlines()
        
        total_lines = len(lines)
        total_pages = (total_lines + lines_per_page - 1) // lines_per_page
        
        # Calculate pagination
        start_line = (page - 1) * lines_per_page
        end_line = min(start_line + lines_per_page, total_lines)
        
        # Get page content
        page_lines = lines[start_line:end_line]
        content = ''.join(page_lines)
        
        # Create metadata
        metadata = FileMetadata(
            size=stat.st_size,
            modified=datetime.fromtimestamp(stat.st_mtime),
            extension=validated_path.suffix.lower() if validated_path.suffix else None,
            mime_type=mimetypes.guess_type(str(validated_path))[0] or "text/plain",
            encoding=encoding,
            line_count=total_lines
        )
        
        # Create pagination info
        pagination = PaginationInfo(
            page=page,
            lines_per_page=lines_per_page,
            total_pages=total_pages,
            total_lines=total_lines,
            has_next=page < total_pages,
            has_previous=page > 1
        )
        
        return FileContentResponse(
            path=str(validated_path.relative_to(self.security.base_path)),
            content=content,
            metadata=metadata,
            pagination=pagination
        )
    
    async def get_file_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Get detailed file metadata
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file metadata
        """
        # Validate path security first
        validated_path = self.security.validate_path(file_path)
        
        if not validated_path.exists():
            raise FileNotFoundError("File not found")
        
        stat = validated_path.stat()
        
        metadata = {
            "path": str(validated_path.relative_to(self.security.base_path)),
            "name": validated_path.name,
            "type": "file" if validated_path.is_file() else "directory",
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "extension": validated_path.suffix.lower() if validated_path.suffix else None,
            "mime_type": mimetypes.guess_type(str(validated_path))[0] if validated_path.is_file() else None,
            "is_readable": os.access(validated_path, os.R_OK),
            "is_writable": os.access(validated_path, os.W_OK),
            "permissions": oct(stat.st_mode)[-3:]
        }
        
        # Add line count for text files
        if validated_path.is_file() and self._is_text_file(validated_path):
            try:
                async with aiofiles.open(validated_path, 'r', encoding='utf-8') as f:
                    lines = await f.readlines()
                    metadata["line_count"] = len(lines)
            except (UnicodeDecodeError, PermissionError):
                metadata["line_count"] = None
        
        return metadata
    
    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is a text file"""
        extension = file_path.suffix.lower()
        filename = file_path.name
        
        # Treat dot files (configuration files) as text files
        if filename.startswith('.') and extension == '':
            return True
        
        # Treat .log files as text files
        if extension == '.log':
            return True
        
        # Check known text extensions
        text_extensions = (
            self.markdown_extensions | 
            self.diagram_extensions | 
            self.text_extensions | 
            self.code_extensions
        )
        
        if extension in text_extensions:
            return True
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type and mime_type.startswith('text/'):
            return True
        
        return False
    
    def get_file_category(self, file_path: Path) -> str:
        """Get file category for rendering priority"""
        extension = file_path.suffix.lower()
        filename = file_path.name
        
        # Treat dot files (configuration files) as text files
        if filename.startswith('.') and extension == '':
            return "text"
        
        # Treat .log files as text files
        if extension == '.log':
            return "text"
        
        if extension in self.markdown_extensions:
            return "markdown"
        elif extension in self.diagram_extensions:
            return "diagram"
        elif extension in self.text_extensions:
            return "text"
        elif extension in self.code_extensions:
            return "code"
        elif extension in self.image_extensions:
            return "image"
        else:
            return "unknown"