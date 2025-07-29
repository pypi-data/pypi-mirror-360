#!/usr/bin/env python3
"""
VeriDoc Backend Server - Development Entry Point
For development use only. In production, use: veridoc
"""

# Import the main server from the package
from veridoc.server import app

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get configuration from environment
    port = int(os.getenv("PORT", 5000))
    base_path = os.getenv("BASE_PATH", ".")
    
    print(f"🚀 VeriDoc server starting on http://localhost:{port}")
    print(f"📁 Base path: {base_path}")
    
    uvicorn.run(
        app,
        host="localhost",
        port=port,
        access_log=False,
        log_level="info"
    )