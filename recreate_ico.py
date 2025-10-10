#!/usr/bin/env python3
"""
Recreate high-quality ICO file from the updated PNG
"""

from PIL import Image
import os

def recreate_ico_from_png():
    """Recreate the ICO file from the high-quality PNG."""
    try:
        # Load the high-quality PNG image
        png_path = "icons/txttovoice.png"
        ico_path = "txttovoice.ico"
        
        print(f"Loading high-quality PNG: {png_path}")
        
        # Open the PNG image
        img = Image.open(png_path)
        print(f"Original PNG size: {img.width}x{img.height} pixels")
        print(f"Original PNG mode: {img.mode}")
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            print("Converted to RGBA mode")
        
        # Create multiple high-quality sizes for the ICO file
        # Using more sizes and higher quality
        sizes = [
            (16, 16),    # Small taskbar/title bar
            (20, 20),    # Windows 10 small
            (24, 24),    # Small toolbar
            (32, 32),    # Standard taskbar
            (40, 40),    # Windows 10 medium
            (48, 48),    # Large taskbar
            (64, 64),    # Extra large
            (96, 96),    # High DPI medium
            (128, 128),  # High DPI large
            (256, 256),  # Very high DPI
            (512, 512)   # Ultra high DPI
        ]
        
        print(f"Creating {len(sizes)} different icon sizes...")
        
        # Resize to all sizes with high-quality resampling
        images = []
        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            images.append(resized)
            print(f"  Created {size[0]}x{size[1]} version")
        
        # Remove old ICO file if it exists
        if os.path.exists(ico_path):
            os.remove(ico_path)
            print(f"Removed old ICO file: {ico_path}")
        
        # Save as ICO with multiple high-quality sizes
        print(f"Saving new high-quality ICO: {ico_path}")
        images[0].save(
            ico_path,
            format='ICO',
            sizes=[(img.width, img.height) for img in images],
            append_images=images[1:]
        )
        
        print(f"✅ Successfully created high-quality {ico_path}")
        print(f"   Sizes included: {', '.join([f'{s[0]}x{s[1]}' for s in sizes])}")
        
        # Also update the one in the icons folder
        icons_ico_path = "icons/txttovoice.ico"
        images[0].save(
            icons_ico_path,
            format='ICO',
            sizes=[(img.width, img.height) for img in images],
            append_images=images[1:]
        )
        
        print(f"✅ Also updated {icons_ico_path}")
        
        # Get file sizes
        ico_size = os.path.getsize(ico_path) / 1024
        print(f"📊 New ICO file size: {ico_size:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error recreating ICO: {e}")
        return False

if __name__ == "__main__":
    success = recreate_ico_from_png()
    if success:
        print("\n🎉 High-quality ICO file created successfully!")
        print("💡 The new ICO includes multiple sizes from 16x16 to 512x512")
        print("🔄 You may need to rebuild the app to use the new icon")
    else:
        print("\n💥 Failed to create ICO file")