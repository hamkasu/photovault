# create_superuser.py
"""
Script to create a superuser account for PhotoVault administration.
"""
import os
import sys
from getpass import getpass

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from photovault import create_app, db
from photovault.models import User

def create_superuser():
    """Create a superuser account."""
    app = create_app()
    
    with app.app_context():
        print("Creating Superuser Account")
        print("-" * 30)
        
        # Get superuser details
        username = input("Enter superuser username: ").strip()
        if not username:
            print("Username cannot be empty.")
            return
            
        email = input("Enter superuser email: ").strip()
        if not email:
            print("Email cannot be empty.")
            return
            
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            print(f"Error: A user with username '{username}' or email '{email}' already exists.")
            return
            
        # Get password securely
        password = getpass("Enter superuser password: ")
        if not password:
            print("Password cannot be empty.")
            return
            
        confirm_password = getpass("Confirm superuser password: ")
        if password != confirm_password:
            print("Passwords do not match.")
            return
            
        # Create superuser
        try:
            superuser = User(
                username=username,
                email=email,
                is_admin=True,      # Also make them an admin
                is_superuser=True   # Mark as superuser
            )
            superuser.set_password(password)
            
            db.session.add(superuser)
            db.session.commit()
            
            print(f"\nSuperuser '{username}' created successfully!")
            print("You can now log in with these credentials.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating superuser: {e}")

if __name__ == "__main__":
    create_superuser()
