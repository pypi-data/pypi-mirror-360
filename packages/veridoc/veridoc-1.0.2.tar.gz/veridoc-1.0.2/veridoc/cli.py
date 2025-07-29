#!/usr/bin/env python3
"""
VeriDoc CLI Helper Script
Usage: veridoc [file_path] [line_number]
       veridoc [directory]
       veridoc --help

Launches VeriDoc documentation browser with specified file or directory.
"""

import sys
import os
import subprocess
import time
import signal
import argparse
import webbrowser
import socket
from pathlib import Path

def find_free_port(start_port=5000, end_port=5099):
    """Find a free port in the specified range."""
    for port in range(start_port, end_port + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            return port
        except OSError:
            continue
    return None

def is_server_running(port):
    """Check if VeriDoc server is already running on the specified port."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def start_server(base_path, port=5000):
    """Start VeriDoc server in the background."""
    # Use python -m veridoc to run the server
    pass  # No need to check for files, we'll use module execution
    
    # Check if server is already running
    if is_server_running(port):
        print(f"VeriDoc server already running on port {port}")
        return None
    
    # Find free port if default is taken
    if port == 5000:
        free_port = find_free_port()
        if free_port and free_port != 5000:
            port = free_port
            print(f"Using port {port} (5000 was taken)")
    
    # Start server
    env = os.environ.copy()
    env['BASE_PATH'] = str(base_path)
    env['PORT'] = str(port)
    
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "veridoc"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )
        
        # Wait for server to start
        for _ in range(30):  # 3 second timeout
            if is_server_running(port):
                print(f"VeriDoc server started on http://localhost:{port}")
                return port
            time.sleep(0.1)
        
        print("Error: Server failed to start within timeout")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"Error starting server: {e}")
        return None

def construct_url(port, file_path=None, line_number=None):
    """Construct URL for VeriDoc web interface."""
    base_url = f"http://localhost:{port}"
    
    if file_path:
        # Convert to relative path from current directory
        try:
            rel_path = os.path.relpath(file_path)
            url = f"{base_url}/?path={rel_path}"
            if line_number:
                url += f"&line={line_number}"
            return url
        except:
            pass
    
    return base_url

def main():
    parser = argparse.ArgumentParser(
        description="VeriDoc CLI - AI-optimized documentation browser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  veridoc                          # Launch in current directory
  veridoc README.md                # Open specific file
  veridoc README.md 42             # Open file at line 42
  veridoc docs/                    # Open specific directory
  veridoc --port 5001              # Use custom port
  veridoc --no-browser             # Start server without opening browser
        """
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='File or directory path to open (default: current directory)'
    )
    
    parser.add_argument(
        'line',
        nargs='?',
        type=int,
        help='Line number to jump to (for files only)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to run server on (default: 5000)'
    )
    
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Start server without opening browser'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='VeriDoc CLI 1.0.1'
    )
    
    args = parser.parse_args()
    
    # Resolve path
    target_path = Path(args.path).resolve()
    
    if not target_path.exists():
        print(f"Error: Path does not exist: {target_path}")
        sys.exit(1)
    
    # Determine base path and file path
    if target_path.is_file():
        base_path = target_path.parent
        file_path = target_path
    else:
        base_path = target_path
        file_path = None
    
    # Start server
    print(f"Starting VeriDoc for: {base_path}")
    port = start_server(base_path, args.port)
    
    if port is None:
        sys.exit(1)
    
    # Construct URL
    url = construct_url(port, file_path, args.line)
    
    # Open browser
    if not args.no_browser:
        print(f"Opening: {url}")
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Warning: Could not open browser: {e}")
            print(f"Please open manually: {url}")
    else:
        print(f"Server running at: {url}")
    
    # Keep running until interrupted
    try:
        print("Press Ctrl+C to stop server")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == "__main__":
    main()