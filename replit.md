# PhotoVault - Photo Management Application

## Overview
PhotoVault is a Flask-based web application for professional photo storage and management, developed by Calmic Sdn Bhd. This is a multi-user platform that allows users to upload, organize, and edit photos with role-based access control.

## Recent Changes
- **September 10, 2025**: Successfully imported and configured for Replit environment
- Fixed main.py structure to separate CLI commands from routes
- Configured Flask app to run on 0.0.0.0:5000 for Replit compatibility
- Set up PostgreSQL-ready configuration (currently using SQLite)
- Configured deployment with Gunicorn for production
- **Photo upload functionality fully operational** with enhanced JavaScript UX
- Fixed all route references and template links for proper form submission
- Added drag & drop, file validation, and progress feedback to upload interface
- **Comprehensive photo markup capabilities implemented** with professional annotation tools
- Added pen, highlight, arrow, rectangle, circle, and text tools with customizable properties
- Implemented undo/redo functionality with keyboard shortcuts
- Enhanced editor with live preview, touch support, and non-destructive editing
- **Photo rename capability added** with inline editing across all views
- Users can rename photos from gallery, detail view, and dashboard with real-time updates
- Secure rename functionality preserves original files while updating display names
- **Photo delete functionality implemented** with single and bulk operations
- Individual photo deletion available from all views with confirmation dialogs
- Bulk selection interface with checkboxes for deleting multiple photos at once
- Comprehensive file cleanup ensures both original and edited versions are properly removed

## Project Architecture
- **Backend**: Flask with SQLAlchemy ORM
- **Database**: SQLite (development), PostgreSQL-ready
- **Authentication**: Flask-Login with user roles (User, Admin, Superuser)
- **File Handling**: Pillow for image processing
- **Frontend**: HTML templates with custom CSS and JavaScript
- **Migrations**: Flask-Migrate with Alembic

## Key Features
- User registration and authentication
- Photo upload and management
- Image editing capabilities
- Role-based access control (User/Admin/Superuser)
- Dashboard with statistics
- Photo organization and tagging

## Development Setup
- Python 3.11 with Flask 2.3.3
- Configured for Replit hosting on port 5000
- Development server: `python main.py`
- Production server: Gunicorn with autoscale deployment

## File Structure
- `main.py`: Application entry point and CLI commands
- `photovault/`: Main application package
  - `__init__.py`: App factory and configuration
  - `models/`: Database models (User, Photo)
  - `routes/`: Blueprint route handlers
  - `templates/`: Jinja2 HTML templates
  - `static/`: CSS, JS, and image assets
- `migrations/`: Database migration files

## Environment Configuration
- Host: 0.0.0.0 (required for Replit)
- Port: 5000 (fixed for Replit)
- Database: SQLite file-based (production-ready for PostgreSQL)
- Upload folder: photovault/static/uploads
- Max file size: 16MB