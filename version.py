# photovault/version.py
"""Version information for PhotoVault"""

__version__ = "1.0.0"
__build__ = "2025.09.10"
__author__ = "PhotoVault Team"
__description__ = "Personal Photo Storage and Editing Platform"

# Version history
VERSION_HISTORY = {
    "1.0.0": {
        "date": "2025-09-10",
        "changes": [
            "Initial release",
            "Photo upload and storage",
            "Basic photo editing tools",
            "User authentication system",
            "Admin panel with user management",
            "Statistics dashboard",
            "Role-based access control"
        ]
    }
}

def get_version():
    """Get the current version string"""
    return __version__

def get_version_info():
    """Get detailed version information"""
    return {
        "version": __version__,
        "build": __build__,
        "author": __author__,
        "description": __description__
    }

def get_full_version():
    """Get full version string with build info"""
    return f"PhotoVault v{__version__} (Build {__build__})"