"""
Initialize database and create tables
"""
from database import init_db, db_session
from models import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def create_admin_user():
    """Create default admin user"""
    # Check if admin exists
    admin = db_session.query(User).filter_by(username='admin').first()
    
    if not admin:
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
        print("✅ Admin user created (username: admin, password: admin123)")
    else:
        print("ℹ️  Admin user already exists")


if __name__ == "__main__":
    print("🚀 Initializing database...")
    init_db()
    print("✅ Database tables created!")
    
    print("\n👤 Creating admin user...")
    create_admin_user()
    
    print("\n✨ Database initialization complete!")
    print("\n📝 You can now run the application with: python app_new.py")
    print("🔐 Default admin credentials: admin / admin123")