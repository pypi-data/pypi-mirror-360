"""
VeriDoc Configuration Management
"""

import os
from pathlib import Path
from typing import Optional

class Config:
    """Application configuration"""
    
    def __init__(self):
        self.base_path = Path(os.getcwd()).resolve()
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.cache_size_mb = 100
        self.log_level = "info"
        self.port = 5000
        self.host = "localhost"
        
        # Load from environment variables
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        if base_path := os.getenv("VERIDOC_BASE_PATH"):
            self.base_path = Path(base_path).resolve()
        
        if max_size := os.getenv("VERIDOC_MAX_FILE_SIZE"):
            self.max_file_size = int(max_size)
        
        if cache_size := os.getenv("VERIDOC_CACHE_SIZE_MB"):
            self.cache_size_mb = int(cache_size)
        
        if log_level := os.getenv("VERIDOC_LOG_LEVEL"):
            self.log_level = log_level
        
        if port := os.getenv("VERIDOC_PORT"):
            self.port = int(port)
        
        if host := os.getenv("VERIDOC_HOST"):
            self.host = host