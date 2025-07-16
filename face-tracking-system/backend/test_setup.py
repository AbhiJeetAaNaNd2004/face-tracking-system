#!/usr/bin/env python3
"""
Simple test script to verify Face Tracking System backend setup.
Run this to check if all components are properly configured.
"""
import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test if all critical modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        # Test FastAPI and core dependencies
        import fastapi
        import uvicorn
        import sqlalchemy
        import psycopg2
        import jwt
        import bcrypt
        import cv2
        import numpy
        print("✅ Core dependencies imported successfully")
        
        # Test our modules
        from app.main import app
        print("✅ Main FastAPI app imported successfully")
        
        from db.db_config import engine, SessionLocal
        print("✅ Database configuration imported successfully")
        
        from utils.security import hash_password, verify_password
        print("✅ Security utilities imported successfully")
        
        from utils.video_stream import camera_manager
        print("✅ Video streaming utilities imported successfully")
        
        from tasks.camera_tasks import camera_monitor
        print("✅ Background tasks imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_environment():
    """Test environment configuration."""
    print("\n🔧 Testing environment configuration...")
    
    # Check for .env file
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found (will use defaults)")
    
    # Check critical environment variables
    secret_key = os.getenv("SECRET_KEY")
    if secret_key and len(secret_key) >= 32:
        print("✅ SECRET_KEY is properly configured")
    else:
        print("⚠️  SECRET_KEY is not set or too short")
    
    # Check database configuration
    db_host = os.getenv("DB_HOST", "localhost")
    db_name = os.getenv("DB_NAME", "face_tracking")
    print(f"✅ Database configured: {db_host}/{db_name}")
    
    return True

def test_security():
    """Test security functions."""
    print("\n🔒 Testing security functions...")
    
    try:
        from utils.security import hash_password, verify_password, create_access_token
        
        # Test password hashing
        test_password = "test123"
        hashed = hash_password(test_password)
        
        if verify_password(test_password, hashed):
            print("✅ Password hashing and verification working")
        else:
            print("❌ Password verification failed")
            return False
        
        # Test JWT token creation
        token = create_access_token({"sub": "test_user", "role": "admin", "status": "active"})
        if token:
            print("✅ JWT token creation working")
        else:
            print("❌ JWT token creation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Security test failed: {e}")
        return False

def test_database():
    """Test database connection."""
    print("\n🗄️  Testing database connection...")
    
    try:
        from db.db_config import engine
        
        # Try to connect to database
        connection = engine.connect()
        connection.close()
        print("✅ Database connection successful")
        return True
        
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("   This is expected if PostgreSQL is not running")
        return False

def main():
    """Run all tests."""
    print("🚀 Face Tracking System Backend - Setup Verification")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Environment Tests", test_environment),
        ("Security Tests", test_security),
        ("Database Tests", test_database),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 All tests passed! The backend is ready to run.")
        print("\nTo start the server:")
        print("  Development: ./start.sh")
        print("  Production:  python run.py")
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.")
        print("\nCommon fixes:")
        print("  - Install missing dependencies: pip install -r requirements.txt")
        print("  - Create .env file: cp .env.example .env")
        print("  - Start PostgreSQL service")
        print("  - Update .env with correct database credentials")

if __name__ == "__main__":
    main()