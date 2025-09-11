"""
PhotoVault - Professional Photo Management Platform
Copyright (c) 2025 Calmic Sdn Bhd. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution,
modification, or use of this software is strictly prohibited.

Website: https://www.calmic.com.my
Email: support@calmic.com.my

CALMIC SDN BHD - "Committed to Excellence"
"""

# photovault/models/__init__.py
from photovault import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # --- Add is_admin field ---
    is_admin = db.Column(db.Boolean, default=False, nullable=False, server_default='0')
    # --- Add is_superuser field ---
    is_superuser = db.Column(db.Boolean, default=False, nullable=False, server_default='0')
    # --- End Add admin/superuser fields ---
    photos = db.relationship('Photo', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False) # This will now point to the original
    original_filename = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    tags = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    # --- Add field to track edited version ---
    edited_filename = db.Column(db.String(255), nullable=True) # Stores the filename of the edited image
    # --- End Add field ---
