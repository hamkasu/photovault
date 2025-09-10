#!/usr/bin/env python3
"""
Script to create an initial superuser for PhotoVault
Run this after setting up the database
"""

from photovault import create_app, db
from photovault.models import User

def create_superuser():
    app = create_app()
    
    with app.app_context():
        # Check if any superuser already exists
        existing_superuser = User.query.filter_by(is_superuser=True).first()
        if existing_superuser:
            print(f"Superuser already exists: {existing_superuser.username}")
            return
        
        print("Creating initial superuser...")
        username = input("Enter username: ").strip()
        email = input("Enter email: ").strip()
        password = input("Enter password: ").strip()
        
        # Validate input
        if not username or not email or not password:
            print("All fields are required!")
            return
        
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            print("Username or email already exists!")
            return
        
        # Create superuser
        user = User(
            username=username,
            email=email,
            is_superuser=True,
            is_admin=True  # Superusers are also admins
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        print(f"Superuser '{username}' created successfully!")

if __name__ == '__main__':
    create_superuser()