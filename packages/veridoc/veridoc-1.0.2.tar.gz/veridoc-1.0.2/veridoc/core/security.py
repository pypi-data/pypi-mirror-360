"""
VeriDoc Security Layer
Path validation and access control
"""

import os
import urllib.parse
import unicodedata
from pathlib import Path
from typing import Union

class SecurityManager:
    """Manages file system security and path validation"""

    def __init__(self, base_path: Union[str, Path]):
        self.base_path = Path(base_path).resolve()

        # Ensure base path exists
        if not self.base_path.exists():
            raise ValueError(f"Base path does not exist: {self.base_path}")

        if not self.base_path.is_dir():
            raise ValueError(f"Base path is not a directory: {self.base_path}")
    
    def _normalize_and_decode_path(self, user_path: str) -> str:
        """
        Normalize and decode path to catch advanced evasion techniques.
        
        Args:
            user_path: Raw user input path
            
        Returns:
            Normalized path string
            
        Raises:
            ValueError: If malicious content detected
        """
        original_path = user_path
        
        # Check for null bytes before any processing
        if "\x00" in user_path or "%00" in user_path:
            raise ValueError("Null bytes not allowed in path")
        
        # Perform multiple rounds of URL decoding to catch double/triple encoding
        for i in range(3):  # Maximum 3 levels of encoding
            decoded = urllib.parse.unquote(user_path)
            if decoded == user_path:
                break  # No more decoding possible
            user_path = decoded
            
            # Check for null bytes after each decoding round
            if "\x00" in user_path:
                raise ValueError("Null bytes not allowed in path")
        
        # Unicode normalization to catch fullwidth and other Unicode evasions
        # Convert to NFD (decomposed) form, then back to NFC (composed)
        user_path = unicodedata.normalize('NFD', user_path)
        user_path = unicodedata.normalize('NFC', user_path)
        
        # Replace common Unicode lookalikes with ASCII equivalents
        unicode_replacements = {
            '\uff0e': '.',  # Fullwidth full stop
            '\uff0f': '/',  # Fullwidth solidus
            '\uff3c': '\\', # Fullwidth reverse solidus
            '\u002e': '.',  # Regular full stop (should be unchanged)
            '\u002f': '/',  # Regular solidus (should be unchanged)
            '\u005c': '\\', # Regular reverse solidus (should be unchanged)
        }
        
        for unicode_char, ascii_char in unicode_replacements.items():
            user_path = user_path.replace(unicode_char, ascii_char)
        
        # Additional check for any remaining suspicious Unicode characters
        # Look for characters that could be path separators or dots
        suspicious_chars = []
        for char in user_path:
            if unicodedata.category(char).startswith('P') and char not in './\\-_':
                # Punctuation that's not common in paths
                suspicious_chars.append(char)
        
        if suspicious_chars:
            # Only raise if the suspicious chars could form path traversal
            cleaned = ''.join(c for c in user_path if c not in suspicious_chars)
            if '..' in cleaned or cleaned != user_path:
                raise ValueError(f"Suspicious Unicode characters in path: {suspicious_chars}")
        
        return user_path
    
    def validate_path(self, user_path: str) -> Path:
        """
        Validate that user path is safe and within base path.

        Args:
            user_path: User-provided path (relative to base)

        Returns:
            Resolved safe path

        Raises:
            ValueError: If path is invalid or outside base path
            SecurityError: If path traversal attempt detected
        """
        if user_path is None:
            raise ValueError("Path cannot be None")
        
        # Convert Path objects to strings
        if hasattr(user_path, '__fspath__'):  # Path-like object
            user_path = str(user_path)
        
        # Handle empty string as base path
        if user_path == "":
            return self.base_path
        
        # Apply advanced normalization and decoding to catch evasion attempts
        user_path = self._normalize_and_decode_path(user_path)
        
        # Check for URL schemes
        if "://" in user_path:
            raise ValueError("URLs not allowed in path")
        
        # Check for Windows absolute paths
        if len(user_path) >= 2 and user_path[1] == ':':
            raise ValueError("Windows absolute paths not allowed")
        
        # Check for Unix absolute paths
        if user_path.startswith('/'):
            # Special case: "/" means root of our base path
            if user_path == "/":
                return self.base_path
            
            # Allow absolute paths if they're within our base path
            try:
                abs_path = Path(user_path).resolve()
                # Try to get relative path to base_path
                rel_path = abs_path.relative_to(self.base_path.resolve())
                user_path = str(rel_path)
            except ValueError:
                # Path is not within base path
                raise ValueError("Absolute paths outside base directory not allowed")
        
        # Check for UNC paths (Windows network paths)
        if user_path.startswith('\\\\') or user_path.startswith('//'):
            raise ValueError("UNC paths not allowed")
            
        # Check for null bytes (redundant but kept for clarity)
        if "\x00" in user_path:
            raise ValueError("Null bytes not allowed in path")

        # Check for dangerous parent directory traversal
        normalized = os.path.normpath(user_path)
        if normalized.startswith('..') or '/../' in normalized or normalized == '..':
            raise ValueError("Path traversal not allowed")

        # Remove leading slashes and normalize (after security checks)
        user_path = user_path.strip("/")

        # Construct full path
        try:
            if user_path == "" or user_path == ".":
                full_path = self.base_path
            else:
                full_path = (self.base_path / user_path).resolve()
        except (OSError, ValueError) as e:
            raise ValueError(f"Invalid path: {e}")

        # Check if resolved path is within base path
        try:
            full_path.relative_to(self.base_path)
        except ValueError:
            raise ValueError("Path outside base directory")

        # Check for symbolic links (security risk)
        if full_path.is_symlink():
            # Check if symlink target is within base path
            try:
                target = full_path.readlink()
                if target.is_absolute():
                    raise ValueError("Absolute symbolic links not allowed")

                resolved_target = (full_path.parent / target).resolve()
                resolved_target.relative_to(self.base_path)
            except (ValueError, OSError):
                raise ValueError("Symbolic link points outside base directory")

        return full_path
    
    def sanitize_input(self, user_input: str) -> str:
        """
        Sanitize user input for safe processing.

        Args:
            user_input: Raw user input

        Returns:
            Sanitized input
        """
        if not isinstance(user_input, str):
            raise ValueError("Input must be a string")

        # Remove null bytes
        sanitized = user_input.replace("\x00", "")

        # Limit length
        if len(sanitized) > 1000:
            raise ValueError("Input too long")

        return sanitized
    
    def is_safe_filename(self, filename: str) -> bool:
        """
        Check if filename is safe.

        Args:
            filename: Filename to check

        Returns:
            True if filename is safe
        """
        # Check for dangerous characters
        dangerous_chars = ["<", ">", ":", '"', "|", "?", "*", "\x00"]

        for char in dangerous_chars:
            if char in filename:
                return False

        # Check for reserved names (Windows)
        reserved_names = [
            "CON", "PRN", "AUX", "NUL",
            "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
            "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
        ]

        if filename.upper() in reserved_names:
            return False

        return True

    def validate_file_size(self, size_bytes: int) -> bool:
        """
        Validate file size is within limits.

        Args:
            size_bytes: File size in bytes

        Returns:
            True if size is acceptable
        """
        if size_bytes < 0:
            return False
        
        # Default limit: 50MB
        max_size = 50 * 1024 * 1024
        return size_bytes <= max_size

    def validate_file_extension(self, filename: str) -> bool:
        """
        Validate file extension is allowed.

        Args:
            filename: Filename to check

        Returns:
            True if extension is allowed
        """
        if not filename:
            return False
        
        if filename is None:
            return False
            
        # Extract extension
        if '.' not in filename:
            # Files without extension (README, Makefile, etc.)
            return True
            
        ext = Path(filename).suffix.lower()
        
        # Allowed extensions
        allowed_extensions = {
            '.md', '.txt', '.py', '.js', '.json', '.yaml', '.yml', 
            '.html', '.css', '.xml', '.rst', '.csv', '.toml',
            '.ini', '.cfg', '.conf', '.sh', '.bat', '.ts', '.tsx',
            '.jsx', '.vue', '.svelte', '.go', '.rs', '.cpp', '.c',
            '.h', '.hpp', '.java', '.kt', '.swift', '.rb', '.php',
            '.pl', '.r', '.scala', '.clj', '.hs', '.elm', '.dart',
            '.lua', '.vim', '.sql', '.dockerfile', '.gitignore',
            '.gitattributes', '.editorconfig'
        }
        
        return ext in allowed_extensions