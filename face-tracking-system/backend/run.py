#!/usr/bin/env python3
"""
Production startup script for Face Tracking System API.
"""
import os
import sys
import uvicorn
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Start the FastAPI application."""
    
    # Configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    workers = int(os.getenv("WORKERS", "1"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    # SSL configuration (optional)
    ssl_keyfile = os.getenv("SSL_KEYFILE")
    ssl_certfile = os.getenv("SSL_CERTFILE")
    
    print("🚀 Starting Face Tracking System API...")
    print(f"📡 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"👥 Workers: {workers}")
    print(f"📝 Log Level: {log_level}")
    print(f"🔄 Reload: {reload}")
    
    if ssl_keyfile and ssl_certfile:
        print(f"🔒 SSL Enabled")
    
    # Start the server
    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            workers=workers if not reload else 1,  # Workers > 1 doesn't work with reload
            log_level=log_level,
            reload=reload,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            access_log=True,
            server_header=False,  # Don't expose server details
            date_header=False,    # Don't expose date header
        )
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()