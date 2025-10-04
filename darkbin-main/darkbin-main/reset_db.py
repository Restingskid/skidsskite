"""
Drop all tables and recreate them with correct schema
"""
from database import engine, init_db, db_session
from models import Base, User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def reset_database():
    """Drop all tables and recreate"""
    print("🗑️  Dropping all existing tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ All tables dropped!")
    
    print("\n🔨 Creating new tables with correct schema...")
    init_db()
    print("✅ Tables created successfully!")
    
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
    print("✅ Admin user created (username: admin, password: admin123)")
    
    print("\n✨ Database reset complete!")
    print("🔐 Default admin credentials: admin / admin123")


if __name__ == "__main__":
    print("⚠️  WARNING: This will delete ALL data in the database!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() == 'yes':
        reset_database()
    else:
        print("❌ Operation cancelled")