#!/usr/bin/env python3
"""
Create a placeholder image for PhotoVault
Run this once to create a placeholder image for broken photo links
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image():
    """Create a simple placeholder image"""
    
    # Create directories
    os.makedirs('photovault/static/img', exist_ok=True)
    
    # Create a 400x300 placeholder image
    width, height = 400, 300
    image = Image.new('RGB', (width, height), color='#f8f9fa')
    
    # Draw on the image
    draw = ImageDraw.Draw(image)
    
    # Try to use a font, fall back to default
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            font = ImageFont.load_default()
    
    # Draw text
    text = "Photo\nPlaceholder"
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw the text
    draw.text((x, y), text, fill='#6c757d', font=font, align='center')
    
    # Draw a border
    draw.rectangle([0, 0, width-1, height-1], outline='#dee2e6', width=2)
    
    # Save the image
    placeholder_path = 'photovault/static/img/placeholder.png'
    image.save(placeholder_path)
    print(f"✅ Created placeholder image: {placeholder_path}")

if __name__ == "__main__":
    create_placeholder_image()
    print("🎯 Placeholder image created successfully!")
    print("   This image will show when uploaded photos fail to load.")