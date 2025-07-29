#!/usr/bin/env python3
"""
VeriDoc Server Main Module
Allows running the server with: python -m veridoc
"""

if __name__ == "__main__":
    import uvicorn
    import os
    from .server import app
    
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