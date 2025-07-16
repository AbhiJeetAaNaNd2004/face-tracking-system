#!/usr/bin/env python3
"""
Database initialization script for Face Tracking System.
This script creates the database schema and populates it with initial data.
"""
import sys
import os
import logging
from pathlib import Path

# Add the parent directory to the path to import from backend modules
sys.path.append(str(Path(__file__).parent.parent))

from db.db_config import create_tables, engine
from db.db_models import Role, User, CameraConfig
from db.db_manager import DatabaseManager
from utils.security import hash_password
import bcrypt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_default_roles(db_manager: DatabaseManager):
    """Create default roles."""
    roles = [
        {
            "role_name": "admin",
            "permissions": {
                "cameras": ["read", "write", "delete"],
                "employees": ["read", "write", "delete"],
                "attendance": ["read", "write", "delete"],
                "embeddings": ["read", "write", "delete"],
                "users": ["read", "write", "delete"],
                "system": ["read", "write"]
            }
        },
        {
            "role_name": "operator",
            "permissions": {
                "cameras": ["read"],
                "employees": ["read", "write"],
                "attendance": ["read", "write"],
                "embeddings": ["read", "write"],
                "users": ["read"],
                "system": ["read"]
            }
        },
        {
            "role_name": "viewer",
            "permissions": {
                "cameras": ["read"],
                "employees": ["read"],
                "attendance": ["read"],
                "embeddings": ["read"],
                "users": [],
                "system": ["read"]
            }
        }
    ]
    
    for role_data in roles:
        existing_role = db_manager.get_role_by_name(role_data["role_name"])
        if not existing_role:
            role = Role(
                role_name=role_data["role_name"],
                permissions=role_data["permissions"]
            )
            success = db_manager.create_role(role)
            if success:
                logger.info(f"Created role: {role_data['role_name']}")
            else:
                logger.error(f"Failed to create role: {role_data['role_name']}")
        else:
            logger.info(f"Role {role_data['role_name']} already exists")

def create_default_admin_user(db_manager: DatabaseManager):
    """Create default admin user."""
    admin_username = "admin"
    admin_password = "admin123!"  # Change this in production!
    
    existing_user = db_manager.get_user_by_username(admin_username)
    if not existing_user:
        # Get admin role
        admin_role = db_manager.get_role_by_name("admin")
        if admin_role:
            success = db_manager.create_user(
                username=admin_username,
                password=admin_password,
                role_id=admin_role.id
            )
            if success:
                logger.info(f"Created default admin user: {admin_username}")
                logger.warning("⚠️  IMPORTANT: Change the default admin password in production!")
            else:
                logger.error("Failed to create default admin user")
        else:
            logger.error("Admin role not found, cannot create admin user")
    else:
        logger.info("Admin user already exists")

def create_default_cameras(db_manager: DatabaseManager):
    """Create default camera configurations."""
    cameras = [
        {
            "camera_id": 0,
            "camera_name": "Main Entrance",
            "camera_type": "entry",
            "resolution_width": 1920,
            "resolution_height": 1080,
            "fps": 30,
            "gpu_id": 0,
            "tripwire_config": {
                "enabled": True,
                "zones": [
                    {
                        "name": "entrance_zone",
                        "points": [[100, 100], [1820, 100], [1820, 980], [100, 980]],
                        "type": "entry"
                    }
                ]
            }
        },
        {
            "camera_id": 1,
            "camera_name": "Exit Door",
            "camera_type": "exit",
            "resolution_width": 1920,
            "resolution_height": 1080,
            "fps": 30,
            "gpu_id": 0,
            "tripwire_config": {
                "enabled": True,
                "zones": [
                    {
                        "name": "exit_zone",
                        "points": [[100, 100], [1820, 100], [1820, 980], [100, 980]],
                        "type": "exit"
                    }
                ]
            }
        }
    ]
    
    for camera_data in cameras:
        existing_camera = db_manager.get_camera_config(camera_data["camera_id"])
        if not existing_camera:
            camera_config = CameraConfig(**camera_data)
            success = db_manager.create_camera_config(camera_config)
            if success:
                logger.info(f"Created camera config: {camera_data['camera_name']}")
            else:
                logger.error(f"Failed to create camera config: {camera_data['camera_name']}")
        else:
            logger.info(f"Camera {camera_data['camera_id']} already exists")

def create_sample_employees(db_manager: DatabaseManager):
    """Create sample employees for testing."""
    employees = [
        {
            "employee_id": "EMP001",
            "employee_name": "John Doe",
            "department": "Engineering",
            "designation": "Software Engineer",
            "email": "john.doe@company.com",
            "phone": "+1234567890"
        },
        {
            "employee_id": "EMP002",
            "employee_name": "Jane Smith",
            "department": "HR",
            "designation": "HR Manager",
            "email": "jane.smith@company.com",
            "phone": "+1234567891"
        }
    ]
    
    for emp_data in employees:
        existing_employee = db_manager.get_employee(emp_data["employee_id"])
        if not existing_employee:
            success = db_manager.create_employee(**emp_data)
            if success:
                logger.info(f"Created sample employee: {emp_data['employee_name']}")
            else:
                logger.error(f"Failed to create sample employee: {emp_data['employee_name']}")
        else:
            logger.info(f"Employee {emp_data['employee_id']} already exists")

def main():
    """Main initialization function."""
    logger.info("🚀 Starting database initialization...")
    
    try:
        # Create database tables
        logger.info("Creating database tables...")
        create_tables()
        logger.info("✅ Database tables created successfully")
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Create default data
        logger.info("Creating default roles...")
        create_default_roles(db_manager)
        
        logger.info("Creating default admin user...")
        create_default_admin_user(db_manager)
        
        logger.info("Creating default camera configurations...")
        create_default_cameras(db_manager)
        
        logger.info("Creating sample employees...")
        create_sample_employees(db_manager)
        
        logger.info("✅ Database initialization completed successfully!")
        
        print("\n" + "="*60)
        print("🎉 Face Tracking System Database Initialized!")
        print("="*60)
        print("Default credentials:")
        print("  Username: admin")
        print("  Password: admin123!")
        print("\n⚠️  IMPORTANT: Change the default password in production!")
        print("="*60)
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()