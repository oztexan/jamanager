#!/usr/bin/env python3
"""
Create sample background images for development jams
"""

import os
from PIL import Image, ImageDraw, ImageFont
import io
import base64

def create_gradient_background(width, height, color1, color2, text, filename):
    """Create a gradient background image with text"""
    # Create image
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    # Create gradient effect
    for y in range(height):
        ratio = y / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Add text overlay
    try:
        # Try to use a system font
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        except:
            font = ImageFont.load_default()
    
    # Get text size and position
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Add text shadow
    draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, 128))
    # Add main text
    draw.text((x, y), text, font=font, fill=(255, 255, 255))
    
    # Save image
    img.save(f"static/uploads/{filename}")
    print(f"✅ Created {filename}")

def main():
    """Create sample background images"""
    # Ensure uploads directory exists
    os.makedirs("static/uploads", exist_ok=True)
    
    # Create different themed backgrounds
    backgrounds = [
        {
            "filename": "acoustic-bg.jpg",
            "color1": (139, 69, 19),  # Saddle brown
            "color2": (160, 82, 45),  # Saddle brown lighter
            "text": "ACOUSTIC"
        },
        {
            "filename": "rock-bg.jpg", 
            "color1": (105, 105, 105),  # Dim gray
            "color2": (47, 79, 79),     # Dark slate gray
            "text": "ROCK"
        },
        {
            "filename": "jazz-bg.jpg",
            "color1": (25, 25, 112),    # Midnight blue
            "color2": (72, 61, 139),    # Dark slate blue
            "text": "JAZZ"
        },
        {
            "filename": "pop-bg.jpg",
            "color1": (255, 20, 147),   # Deep pink
            "color2": (255, 105, 180),  # Hot pink
            "text": "POP"
        },
        {
            "filename": "country-bg.jpg",
            "color1": (34, 139, 34),    # Forest green
            "color2": (107, 142, 35),   # Olive drab
            "text": "COUNTRY"
        }
    ]
    
    for bg in backgrounds:
        create_gradient_background(
            width=1200,
            height=800,
            color1=bg["color1"],
            color2=bg["color2"],
            text=bg["text"],
            filename=bg["filename"]
        )
    
    print(f"\n🎨 Created {len(backgrounds)} sample background images")
    print("   These will be used for jam sessions in development")

if __name__ == "__main__":
    main()
