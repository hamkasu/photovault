#!/usr/bin/env python3
"""
PhotoVault Route Verification Script
Run this to check if all routes are properly registered
"""

import sys
import os

# Add the PhotoVault directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_routes():
    """Verify all PhotoVault routes are registered correctly"""
    
    print("🔍 PhotoVault Route Verification")
    print("=" * 40)
    
    try:
        from photovault import create_app
        
        # Create app instance
        app = create_app()
        
        with app.app_context():
            print("✅ Flask app created successfully")
            
            # Get all registered routes
            routes = []
            for rule in app.url_map.iter_rules():
                if rule.endpoint != 'static':
                    routes.append({
                        'endpoint': rule.endpoint,
                        'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                        'path': rule.rule
                    })
            
            # Sort routes by blueprint and endpoint
            routes.sort(key=lambda x: (x['endpoint'].split('.')[0], x['endpoint']))
            
            print(f"\n📋 Registered Routes ({len(routes)} total):")
            print("-" * 50)
            
            current_blueprint = None
            for route in routes:
                blueprint = route['endpoint'].split('.')[0]
                
                if blueprint != current_blueprint:
                    current_blueprint = blueprint
                    print(f"\n🔹 {blueprint.upper()} Blueprint:")
                
                methods_str = ', '.join(route['methods'])
                print(f"   {route['endpoint']:<20} {route['path']:<30} [{methods_str}]")
            
            # Check specific required routes
            print(f"\n🎯 Critical Route Check:")
            required_routes = [
                'main.index',
                'main.about', 
                'main.dashboard',
                'auth.login',
                'auth.logout',
                'auth.register'
            ]
            
            registered_endpoints = [route['endpoint'] for route in routes]
            
            for required in required_routes:
                if required in registered_endpoints:
                    print(f"   ✅ {required}")
                else:
                    print(f"   ❌ {required} - MISSING!")
            
            # Test URL building
            print(f"\n🔗 URL Building Test:")
            test_urls = [
                ('main.index', 'Home page'),
                ('main.about', 'About page'),
                ('auth.login', 'Login page'),
                ('auth.register', 'Register page')
            ]
            
            with app.test_request_context():
                from flask import url_for
                
                for endpoint, description in test_urls:
                    try:
                        url = url_for(endpoint)
                        print(f"   ✅ {endpoint:<15} -> {url:<20} ({description})")
                    except Exception as e:
                        print(f"   ❌ {endpoint:<15} -> ERROR: {str(e)}")
            
            print(f"\n🚀 Route verification complete!")
            
            # Check template files
            print(f"\n📄 Template Files Check:")
            template_files = [
                'base.html',
                'index.html', 
                'about.html',
                'dashboard.html',
                'login.html',
                'register.html'
            ]
            
            template_dir = os.path.join(os.path.dirname(__file__), 'photovault', 'templates')
            
            for template in template_files:
                template_path = os.path.join(template_dir, template)
                if os.path.exists(template_path):
                    print(f"   ✅ {template}")
                else:
                    print(f"   ❌ {template} - MISSING!")
            
            return True
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Make sure you're running this from the PhotoVault directory")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_blueprint_registration():
    """Check if blueprints are properly registered"""
    
    print(f"\n🔧 Blueprint Registration Check:")
    
    try:
        # Check if __init__.py has blueprint registration
        init_file = os.path.join('photovault', '__init__.py')
        
        if os.path.exists(init_file):
            with open(init_file, 'r') as f:
                content = f.read()
                
            blueprints = ['auth_bp', 'main_bp', 'photo_bp', 'admin_bp', 'superuser_bp']
            
            for bp in blueprints:
                if f'app.register_blueprint({bp})' in content:
                    print(f"   ✅ {bp} registered")
                else:
                    print(f"   ❌ {bp} not registered")
        else:
            print("   ❌ photovault/__init__.py not found")
            
    except Exception as e:
        print(f"   ❌ Error checking blueprints: {e}")

if __name__ == "__main__":
    try:
        success = verify_routes()
        check_blueprint_registration()
        
        if success:
            print(f"\n✅ All checks completed. PhotoVault routes should be working!")
        else:
            print(f"\n❌ Issues found. Please check the errors above.")
            
    except KeyboardInterrupt:
        print(f"\n\n👋 Verification cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print(f"Please check your PhotoVault installation")