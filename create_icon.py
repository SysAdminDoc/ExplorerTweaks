#!/usr/bin/env python3
"""
Icon Generator for ExplorerTweaks
=================================
Generates a simple icon file for the application.
Requires: pip install pillow

Run this script to create icon.ico before building.
"""

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow not installed. Installing...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'pillow'])
    from PIL import Image, ImageDraw, ImageFont

import os


def create_icon():
    """Create a modern folder icon with gear overlay."""
    
    # Icon sizes for ICO file
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []
    
    for size in sizes:
        # Create image with transparency
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Calculate proportions
        padding = size // 8
        folder_height = int(size * 0.65)
        folder_width = size - (padding * 2)
        tab_width = folder_width // 3
        tab_height = size // 6
        
        # Colors (Spotify green theme)
        folder_color = (29, 185, 84)  # #1DB954
        folder_dark = (22, 140, 64)   # Darker shade
        gear_color = (255, 255, 255)  # White
        
        # Draw folder back
        folder_top = padding + tab_height
        folder_bottom = size - padding
        
        # Folder body
        draw.rounded_rectangle(
            [padding, folder_top, size - padding, folder_bottom],
            radius=size // 16,
            fill=folder_color,
        )
        
        # Folder tab
        draw.rounded_rectangle(
            [padding, padding, padding + tab_width, folder_top + size // 16],
            radius=size // 20,
            fill=folder_color,
        )
        
        # Draw gear icon (simplified)
        gear_size = size // 3
        gear_x = size - padding - gear_size // 2 - size // 10
        gear_y = folder_bottom - gear_size // 2 - size // 10
        
        # Gear circle
        gear_radius = gear_size // 2
        draw.ellipse(
            [gear_x - gear_radius, gear_y - gear_radius,
             gear_x + gear_radius, gear_y + gear_radius],
            fill=gear_color,
        )
        
        # Inner circle (hole)
        inner_radius = gear_radius // 2
        draw.ellipse(
            [gear_x - inner_radius, gear_y - inner_radius,
             gear_x + inner_radius, gear_y + inner_radius],
            fill=folder_color,
        )
        
        # Gear teeth (simplified as small rectangles)
        if size >= 32:
            tooth_size = max(2, gear_radius // 3)
            for angle in range(0, 360, 45):
                import math
                rad = math.radians(angle)
                tx = gear_x + int(gear_radius * 0.9 * math.cos(rad))
                ty = gear_y + int(gear_radius * 0.9 * math.sin(rad))
                draw.ellipse(
                    [tx - tooth_size, ty - tooth_size,
                     tx + tooth_size, ty + tooth_size],
                    fill=gear_color,
                )
        
        images.append(img)
    
    # Save as ICO file
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
    images[0].save(
        icon_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[1:],
    )
    
    print(f"Icon created: {icon_path}")
    return icon_path


def create_simple_icon():
    """Create a very simple icon without complex drawing."""
    from PIL import Image, ImageDraw
    
    sizes = [16, 32, 48, 256]
    images = []
    
    for size in sizes:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Simple colored square with rounded corners
        padding = size // 8
        
        # Background
        draw.rounded_rectangle(
            [padding, padding, size - padding, size - padding],
            radius=size // 6,
            fill=(29, 185, 84),  # Spotify green
        )
        
        # Simple "E" letter
        if size >= 32:
            text_padding = size // 4
            line_width = max(2, size // 16)
            
            # Vertical line of E
            draw.rectangle(
                [text_padding, text_padding,
                 text_padding + line_width, size - text_padding],
                fill=(255, 255, 255),
            )
            
            # Horizontal lines of E
            for y_offset in [text_padding, size // 2 - line_width // 2, size - text_padding - line_width]:
                draw.rectangle(
                    [text_padding, y_offset,
                     size - text_padding, y_offset + line_width],
                    fill=(255, 255, 255),
                )
        
        images.append(img)
    
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
    images[-1].save(
        icon_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
    )
    
    print(f"Simple icon created: {icon_path}")
    return icon_path


if __name__ == "__main__":
    try:
        create_icon()
    except Exception as e:
        print(f"Complex icon failed ({e}), creating simple icon...")
        create_simple_icon()
    
    print("\nIcon generation complete!")
    print("You can now run build.bat to create the executable.")
