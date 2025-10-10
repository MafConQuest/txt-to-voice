#!/usr/bin/env python3
"""
txttovoice Release Builder
=========================

Creates a distributable release package for txttovoice.
Visit: https://txttovoice.com
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_release():
    """Create a release package."""
    print("🚀 Building txttovoice release package...")
    
    # Create release directory
    release_dir = Path("release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # Files to include in release
    files_to_include = [
        "txttovoice.py",
        "install.bat", 
        "requirements.txt",
        "README.md",
        "LICENSE"
    ]
    
    # Copy files
    for file in files_to_include:
        if Path(file).exists():
            shutil.copy2(file, release_dir)
            print(f"✅ Copied {file}")
        else:
            print(f"⚠️ Missing {file}")
    
    # Copy icons directory
    if Path("icons").exists():
        shutil.copytree("icons", release_dir / "icons")
        print("✅ Copied icons directory")
    
    # Create version info
    version_info = f"""txttovoice Release
==================

Version: 1.0.0
Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Website: https://txttovoice.com

Installation:
1. Run install.bat
2. Get OpenAI API key from https://platform.openai.com/api-keys
3. Launch txttovoice and enter your API key in Settings
4. Start converting text to speech!

Support: https://txttovoice.com/support
"""
    
    with open(release_dir / "VERSION.txt", 'w') as f:
        f.write(version_info)
    
    # Create ZIP file
    zip_name = f"txttovoice-v1.0.0-{datetime.now().strftime('%Y%m%d')}.zip"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in release_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(release_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Created release package: {zip_name}")
    print(f"📦 Package size: {Path(zip_name).stat().st_size / 1024:.1f} KB")
    
    # Create GitHub release info
    release_notes = f"""# txttovoice v1.0.0

🎤 **Professional Text-to-Speech Application**

## ✨ Features
- Global hotkey (Ctrl+Shift+J) to convert selected text
- 6 professional OpenAI voices
- System tray integration
- Speed control (0.5x - 2.0x)
- Windows native application

## 🚀 Installation
1. Download `{zip_name}`
2. Extract all files
3. Run `install.bat`
4. Get your OpenAI API key from https://platform.openai.com/api-keys
5. Launch txttovoice and enter your API key

## 🔗 Links
- Website: https://txttovoice.com
- Support: https://txttovoice.com/support
- API Keys: https://platform.openai.com/api-keys

**Full Changelog**: https://github.com/yourusername/txttovoice/compare/v0.9.0...v1.0.0
"""
    
    with open("RELEASE_NOTES.md", 'w') as f:
        f.write(release_notes)
    
    print("✅ Created RELEASE_NOTES.md for GitHub")
    print()
    print("🎉 Release package ready!")
    print(f"📁 Files: {len(list(release_dir.rglob('*')))} files")
    print(f"📦 Package: {zip_name}")
    print()
    print("Next steps:")
    print("1. Upload to GitHub Releases")
    print("2. Upload to txttovoice.com")
    print("3. Test installation on clean Windows machine")

if __name__ == "__main__":
    create_release()