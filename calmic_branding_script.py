#!/usr/bin/env python3
"""
PhotoVault - Calmic Sdn Bhd Branding Setup Script
This script sets up the required directory structure and checks for the logo file.
"""

import os
from pathlib import Path

def setup_calmic_branding():
    """Setup directory structure and verify branding files"""
    
    print("🏢 Setting up Calmic Sdn Bhd branding for PhotoVault...")
    print("=" * 60)
    
    # Create required directories
    directories = [
        'photovault/static/img',
        'photovault/static/css',
        'photovault/templates'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Check for logo file
    logo_path = Path('photovault/static/img/calmic-logo.png')
    if logo_path.exists():
        print(f"✅ Logo found: {logo_path}")
        
        # Check logo file size
        file_size = logo_path.stat().st_size
        if file_size > 1024 * 1024:  # 1MB
            print(f"⚠️  Warning: Logo file is large ({file_size // 1024}KB). Consider optimizing for web.")
        else:
            print(f"✅ Logo file size OK: {file_size // 1024}KB")
    else:
        print(f"❌ Logo not found: {logo_path}")
        print("   Please add your company logo as 'calmic-logo.png' in the static/img folder")
    
    # Check for updated template files
    template_path = Path('photovault/templates/base.html')
    css_path = Path('photovault/static/css/style.css')
    
    print("\n📄 File Status:")
    print(f"{'✅' if template_path.exists() else '❌'} Base template: {template_path}")
    print(f"{'✅' if css_path.exists() else '❌'} CSS file: {css_path}")
    
    # Verify template has Calmic branding
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'Calmic Sdn Bhd' in content:
                print("✅ Template contains Calmic branding")
            else:
                print("❌ Template needs to be updated with Calmic branding")
    
    # Verify CSS has branding styles
    if css_path.exists():
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'brand-text' in content and 'company-name' in content:
                print("✅ CSS contains branding styles")
            else:
                print("❌ CSS needs to be updated with branding styles")
    
    print("\n🎨 Branding Implementation Checklist:")
    print("1. ✅ Directory structure created")
    print(f"2. {'✅' if logo_path.exists() else '❌'} Company logo added")
    print(f"3. {'✅' if template_path.exists() else '❌'} Base template exists")
    print(f"4. {'✅' if css_path.exists() else '❌'} CSS file exists")
    
    print("\n📋 Next Steps:")
    if not logo_path.exists():
        print("1. Add your Calmic logo as 'photovault/static/img/calmic-logo.png'")
    print("2. Update base.html template with the provided Calmic-branded version")
    print("3. Update style.css with the provided branding styles")
    print("4. Restart your Flask application")
    print("5. Verify branding appears correctly in browser")
    
    print("\n💡 Logo Requirements:")
    print("- Format: PNG with transparent background")
    print("- Size: 200x200px or higher (minimum 100x100px)")
    print("- Aspect ratio: Square or rectangular (width ≤ 2x height)")
    print("- File size: Under 1MB (preferably under 500KB)")
    
    print("\n🚀 Ready to deploy with Calmic Sdn Bhd branding!")

def check_flask_app():
    """Check if this is a Flask application directory"""
    required_files = [
        'app.py',
        'run.py',
        'photovault/__init__.py'
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            return True
    return False

if __name__ == "__main__":
    if check_flask_app():
        setup_calmic_branding()
    else:
        print("❌ This doesn't appear to be a PhotoVault Flask application directory.")
        print("Please run this script from your PhotoVault project root directory.")
        print("\nExpected files: app.py, run.py, or photovault/__init__.py")