"""
Quick start script for skids.rest
This script will:
1. Check if database is initialized
2. Create tables if needed
3. Create admin user if needed
4. Start the application
"""
import os
import sys

def check_dependencies():
    """Check if all required packages are installed"""
    print("📦 Checking dependencies...")
    try:
        import flask
        import sqlalchemy
        import flask_login
        import flask_bcrypt
        import flask_socketio
        import psycopg2
        print("✅ All dependencies installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n💡 Run: pip install -r requirements.txt")
        return False


def check_env():
    """Check if .env file exists"""
    print("\n🔍 Checking environment configuration...")
    if not os.path.exists('.env'):
        print("⚠️  .env file not found!")
        print("💡 Creating .env from .env.example...")
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("✅ .env file created! Please edit it with your configuration.")
        else:
            print("❌ .env.example not found!")
        return False
    print("✅ Environment configuration found!")
    return True


def initialize_database():
    """Initialize database and create admin user"""
    print("\n🗄️  Initializing database...")
    try:
        from database import init_db, db_session
        from models import User
        from flask_bcrypt import Bcrypt
        
        bcrypt = Bcrypt()
        
        # Create tables
        init_db()
        print("✅ Database tables created!")
        
        # Check if admin exists
        admin = db_session.query(User).filter_by(username='admin').first()
        
        if not admin:
            print("\n👤 Creating admin user...")
            hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(
                username='admin',
                password=hashed_password,
                email='admin@skids.rest',
                role='admin',
                bio='Site Administrator',
                username_color='#ff0000'
            )
            db_session.add(admin)
            db_session.commit()
            print("✅ Admin user created!")
            print("   Username: admin")
            print("   Password: admin123")
            print("   ⚠️  CHANGE THIS PASSWORD AFTER FIRST LOGIN!")
        else:
            print("ℹ️  Admin user already exists")
        
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("\n💡 Make sure your DATABASE_URL in .env is correct")
        return False


def start_application():
    """Start the Flask application"""
    print("\n🚀 Starting skids.rest...")
    print("=" * 60)
    print("🌐 Application will be available at: http://localhost:5000")
    print("📝 Login with: admin / admin123")
    print("=" * 60)
    print()
    
    try:
        from app_new import app, socketio
        socketio.run(app, host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)


def main():
    """Main startup sequence"""
    print("=" * 60)
    print("🎯 skids.rest - Quick Start")
    print("=" * 60)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Step 2: Check environment
    if not check_env():
        print("\n⚠️  Please configure your .env file and run this script again.")
        sys.exit(1)
    
    # Step 3: Initialize database
    if not initialize_database():
        sys.exit(1)
    
    # Step 4: Start application
    start_application()


if __name__ == "__main__":
    main()