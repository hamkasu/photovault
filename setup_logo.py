#!/usr/bin/env python3
"""
PhotoVault Logo Setup Script
This script helps you set up your Calmic logo correctly.
"""

import os
import shutil
from pathlib import Path

def setup_logo():
    """Set up the Calmic logo for PhotoVault"""
    
    print("🏢 Calmic Logo Setup for PhotoVault")
    print("=" * 40)
    
    # Create the required directory
    logo_dir = Path('photovault/static/img')
    logo_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created directory: {logo_dir}")
    
    logo_path = logo_dir / 'calmic-logo.png'
    
    # Check if logo already exists
    if logo_path.exists():
        print(f"✅ Logo already exists: {logo_path}")
        file_size = logo_path.stat().st_size
        print(f"   📊 Current size: {file_size} bytes ({file_size/1024:.1f} KB)")
        
        replace = input(f"\n🔄 Replace existing logo? (y/n): ").lower().strip()
        if replace not in ['y', 'yes']:
            print(f"   Keeping existing logo.")
            return
    
    # Look for logo files in current directory
    print(f"\n🔍 Looking for logo files in current directory...")
    
    possible_logos = []
    for file_path in Path('.').glob('*'):
        if file_path.is_file() and file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
            if any(keyword in file_path.name.lower() for keyword in ['logo', 'calmic', 'brand']):
                possible_logos.append(file_path)
    
    if possible_logos:
        print(f"\n📁 Found potential logo files:")
        for i, logo_file in enumerate(possible_logos, 1):
            file_size = logo_file.stat().st_size
            print(f"   {i}. {logo_file.name} ({file_size/1024:.1f} KB)")
        
        print(f"   0. Browse for a different file")
        
        try:
            choice = int(input(f"\nSelect logo file (1-{len(possible_logos)}, 0 to browse): "))
            if 1 <= choice <= len(possible_logos):
                selected_logo = possible_logos[choice - 1]
                
                # Copy and rename the file
                shutil.copy2(selected_logo, logo_path)
                print(f"✅ Logo copied to: {logo_path}")
                
                # Verify the copy
                if logo_path.exists():
                    new_size = logo_path.stat().st_size
                    print(f"✅ Verification: Logo file exists ({new_size/1024:.1f} KB)")
                    
                    if new_size > 1024 * 1024:  # 1MB
                        print(f"⚠️  Warning: Logo is large ({new_size/1024/1024:.1f} MB)")
                        print(f"   Consider optimizing for web use")
                    
                    return True
                else:
                    print(f"❌ Error: Failed to copy logo file")
                    return False
            elif choice == 0:
                print(f"\n📂 Please manually copy your logo file to:")
                print(f"   {logo_path}")
                print(f"   Ensure the filename is exactly 'calmic-logo.png'")
                return False
        except ValueError:
            print(f"❌ Invalid selection")
            return False
    else:
        print(f"❌ No logo files found in current directory")
        print(f"\n📝 Instructions:")
        print(f"1. Copy your Calmic logo file to this directory")
        print(f"2. Run this script again")
        print(f"3. Or manually copy your logo to: {logo_path}")
        return False

def verify_setup():
    """Verify the logo setup is correct"""
    
    print(f"\n🔍 Verifying logo setup...")
    
    # Check file exists
    logo_path = Path('photovault/static/img/calmic-logo.png')
    if not logo_path.exists():
        print(f"❌ Logo file not found: {logo_path}")
        return False
    
    print(f"✅ Logo file exists: {logo_path}")
    
    # Check file size
    file_size = logo_path.stat().st_size
    print(f"✅ File size: {file_size} bytes ({file_size/1024:.1f} KB)")
    
    if file_size < 100:
        print(f"⚠️  Warning: File is very small, might be corrupted")
    elif file_size > 2 * 1024 * 1024:
        print(f"⚠️  Warning: File is large, consider optimizing")
    
    # Check if it's likely a valid image
    try:
        with open(logo_path, 'rb') as f:
            header = f.read(8)
            if header.startswith(b'\x89PNG\r\n\x1a\n'):
                print(f"✅ Valid PNG file detected")
            else:
                print(f"⚠️  Warning: File might not be a valid PNG")
    except:
        print(f"⚠️  Warning: Could not verify file format")
    
    # Check template file
    template_path = Path('photovault/templates/base.html')
    if template_path.exists():
        print(f"✅ Template file found")
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'calmic-logo.png' in content:
                print(f"✅ Template references logo correctly")
            else:
                print(f"❌ Template doesn't reference calmic-logo.png")
    else:
        print(f"❌ Template file not found: {template_path}")
    
    print(f"\n🚀 Next steps:")
    print(f"1. Restart your Flask application")
    print(f"2. Hard refresh your browser (Ctrl+F5)")
    print(f"3. Check if logo appears in navbar")
    
    return True

if __name__ == "__main__":
    try:
        if setup_logo():
            verify_setup()
        
        print(f"\n💡 Troubleshooting tips:")
        print(f"- Logo should be PNG format")
        print(f"- Recommended size: 100x100 to 400x400 pixels")
        print(f"- Keep file size under 500KB")
        print(f"- Use transparent background for best results")
        
        input(f"\nPress Enter to exit...")
        
    except KeyboardInterrupt:
        print(f"\n\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"Please try manual setup")