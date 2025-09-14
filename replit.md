# Overview

PhotoVault is a professional photo management platform developed by Calmic Sdn Bhd. It provides secure photo storage, advanced editing capabilities, user management, and administrative features. The system is built using Flask with a focus on enterprise-grade security, role-based access control, and comprehensive photo organization tools.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Framework
- **Flask**: Core web framework providing routing, templating, and request handling
- **Flask-SQLAlchemy**: Database ORM for model definitions and database operations
- **Flask-Login**: User session management and authentication
- **Flask-Migrate**: Database schema migrations using Alembic
- **Flask-WTF**: CSRF protection and form handling

## Database Design
- **PostgreSQL**: Primary database (with psycopg2-binary adapter)
- **SQLAlchemy Models**: User, Photo, Album, Person, and PhotoPerson entities
- **Migration System**: Alembic-based versioned schema management
- **Relationships**: Foreign key constraints between users, photos, albums, and people

## Authentication & Authorization
- **Role-Based Access Control**: Three-tier system (User, Admin, Superuser)
- **Password Security**: Werkzeug password hashing with salt
- **Session Management**: Flask-Login for secure user sessions
- **CSRF Protection**: Flask-WTF token-based protection on all forms

## File Management
- **Image Processing**: Pillow (PIL) for image manipulation and validation
- **Secure Upload**: Werkzeug secure filename handling with UUID generation
- **File Validation**: MIME type checking and size limits (16MB max)
- **Storage Structure**: Organized file system with original and edited versions

## Frontend Architecture
- **Template Engine**: Jinja2 templating with Bootstrap 5 responsive design
- **Client-Side Processing**: Canvas-based photo editing with JavaScript
- **Camera Integration**: WebRTC getUserMedia API for device camera access
- **Progressive Enhancement**: Mobile-responsive design with touch support

## Security Features
- **Input Validation**: Server-side validation for all user inputs
- **File Security**: Image validation to prevent malicious uploads
- **Access Control**: Decorator-based route protection
- **Error Handling**: Graceful error handling with user-friendly messages

## Photo Management
- **Dual Storage**: Original and edited versions maintained separately
- **Metadata Tracking**: File size, upload timestamps, and editing history
- **Album Organization**: Time-based and event-based photo grouping
- **Person Tagging**: Face detection metadata and relationship tracking

# External Dependencies

## Core Framework Dependencies
- **Flask 3.0.3**: Web application framework
- **Flask-SQLAlchemy 3.1.1**: Database ORM
- **Flask-Login 0.6.3**: User authentication
- **Flask-Migrate 4.1.0**: Database migrations
- **Flask-WTF 1.2.1**: Form handling and CSRF protection

## Database & Storage
- **PostgreSQL**: Primary database system
- **psycopg2-binary**: PostgreSQL adapter for Python
- **SQLAlchemy**: Database abstraction layer

## Image Processing
- **Pillow 11.0.0+**: Image manipulation and validation
- **Canvas API**: Client-side image editing capabilities

## Frontend Libraries
- **Bootstrap 5.1.3**: CSS framework for responsive design
- **Bootstrap Icons 1.11.3**: Icon library for UI elements
- **WebRTC getUserMedia**: Camera access for photo capture

## Production & Development
- **Gunicorn**: WSGI HTTP server for production deployment
- **python-dotenv**: Environment variable management
- **Werkzeug 3.0.3**: WSGI utilities and security functions

## Optional Integrations
- **OpenCV.js**: Advanced computer vision features (edge detection, perspective correction)
- **Face Detection APIs**: For automated person tagging capabilities