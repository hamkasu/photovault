#!/usr/bin/env python3
"""
PhotoVault Logo Diagnostic Script
This script helps diagnose why your Calmic logo isn't showing up.
"""

import os
from pathlib import Path

def diagnose_logo_issues():
    """Diagnose common logo display issues"""
    
    print("🔍 PhotoVault Logo Diagnostic Tool")
    print("=" * 50)
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    
    # Expected logo paths
    possible_paths = [
        'photovault/static/img/calmic-logo.png',
        'static/img/calmic-logo.png',
        'photovault/static/images/calmic-logo.png',
        'static/images/calmic-logo.png',
        'app/static/img/calmic-logo.png'
    ]
    
    print("\n📂 Checking logo file locations:")
    logo_found = False
    correct_path = None
    
    for path in possible_paths:
        full_path = Path(path)
        if full_path.exists():
            print(f"✅ FOUND: {path}")
            logo_found = True
            correct_path = path
            
            # Check file size
            file_size = full_path.stat().st_size
            print(f"   📊 File size: {file_size} bytes ({file_size/1024:.1f} KB)")
            
            # Check if it's a valid image file
            if file_size < 100:
                print(f"   ⚠️  WARNING: File is very small ({file_size} bytes) - might be corrupted")
            elif file_size > 2 * 1024 * 1024:  # 2MB
                print(f"   ⚠️  WARNING: File is large ({file_size/1024/1024:.1f} MB) - consider optimizing")
            else:
                print(f"   ✅ File size looks good")
        else:
            print(f"❌ Missing: {path}")
    
    if not logo_found:
        print(f"\n❌ No logo file found in any expected location!")
        print(f"Expected filename: calmic-logo.png")
        
        # Check for other image files that might be the logo
        print(f"\n🔍 Looking for other image files...")
        for search_dir in ['photovault/static', 'static']:
            if Path(search_dir).exists():
                print(f"\nFiles in {search_dir}:")
                for file_path in Path(search_dir).rglob('*'):
                    if file_path.is_file() and file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
                        print(f"   📁 {file_path}")
    
    # Check Flask static folder configuration
    print(f"\n⚙️  Flask Configuration Check:")
    
    # Check if PhotoVault directory structure exists
    pv_dirs = ['photovault', 'photovault/static', 'photovault/templates']
    for dir_path in pv_dirs:
        if Path(dir_path).exists():
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"❌ Missing directory: {dir_path}")
    
    # Check template files
    template_files = ['photovault/templates/base.html', 'templates/base.html']
    template_found = False
    for template_path in template_files:
        if Path(template_path).exists():
            print(f"✅ Template found: {template_path}")
            template_found = True
            
            # Check if template references the logo
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'calmic-logo.png' in content:
                    print(f"   ✅ Template references calmic-logo.png")
                else:
                    print(f"   ❌ Template doesn't reference calmic-logo.png")
                
                if "url_for('static', filename='img/calmic-logo.png')" in content:
                    print(f"   ✅ Template uses correct Flask url_for syntax")
                else:
                    print(f"   ⚠️  Template might not use correct Flask url_for syntax")
            break
    
    if not template_found:
        print(f"❌ No base.html template found")
    
    print(f"\n💡 Solutions:")
    
    if not logo_found:
        print(f"1. Add your logo file as 'calmic-logo.png' to: photovault/static/img/")
        print(f"2. Ensure the filename is exactly 'calmic-logo.png' (case-sensitive)")
        print(f"3. Make sure the file is a valid PNG image")
    
    print(f"4. Restart your Flask application after adding the logo")
    print(f"5. Clear your browser cache (Ctrl+F5 or Cmd+Shift+R)")
    print(f"6. Check browser developer tools (F12) for 404 errors on the logo")
    
    # Generate the correct directory structure
    print(f"\n🏗️  Creating missing directories...")
    Path('photovault/static/img').mkdir(parents=True, exist_ok=True)
    print(f"✅ Created: photovault/static/img/")
    
    if correct_path:
        print(f"\n✅ Logo file found at: {correct_path}")
        print(f"If logo still not showing, check:")
        print(f"   - Browser cache (hard refresh)")
        print(f"   - Flask static file serving")
        print(f"   - File permissions")
    else:
        print(f"\n📥 Next step: Add your logo file")
        print(f"   Copy your company logo to: photovault/static/img/calmic-logo.png")

def create_test_logo():
    """Create a simple test logo if none exists"""
    import base64
    
    # Simple PNG data for a test logo (1x1 transparent pixel)
    simple_png = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
    )
    
    logo_path = Path('photovault/static/img/calmic-logo.png')
    logo_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not logo_path.exists():
        with open(logo_path, 'wb') as f:
            f.write(simple_png)
        print(f"✅ Created test logo at: {logo_path}")
        print(f"   Replace this with your actual Calmic logo")
        return True
    return False

if __name__ == "__main__":
    diagnose_logo_issues()
    
    print(f"\n🧪 Create test logo? (y/n): ", end="")
    try:
        response = input().lower().strip()
        if response in ['y', 'yes']:
            if create_test_logo():
                print(f"Test logo created. Replace with your actual logo.")
    except:
        pass
    
    print(f"\n🔧 Run this diagnostic again after adding your logo file!")