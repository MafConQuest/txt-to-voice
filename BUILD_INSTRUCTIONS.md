# txttovoice - Build Instructions

## Building the Professional Installer

This project creates a professional Windows installer that significantly reduces security warnings.

### Prerequisites

1. **Python 3.x** with required packages:
   ```cmd
   pip install -r requirements.txt
   ```

2. **NSIS (Nullsoft Scriptable Install System)**:
   - Download from: https://nsis.sourceforge.io/Download
   - Install and make sure to check "Add NSIS to PATH"

### Build Process

1. **Build the executable**:
   ```cmd
   pyinstaller txttovoice.spec
   copy dist\txttovoice.exe txttovoice.exe
   ```

2. **Create the professional installer**:
   ```cmd
   make_installer.bat
   ```
   
   Or manually:
   ```cmd
   makensis txttovoice_installer.nsi
   ```

### Output

- `txttovoice-installer.exe` - Professional installer with minimal security warnings
- Distribute this file instead of the raw executable

### Key Files

- `txttovoice.py` - Main application
- `txttovoice.spec` - PyInstaller configuration
- `txttovoice_installer.nsi` - NSIS installer script
- `make_installer.bat` - Simple build script
- `version_info.txt` - Windows version information
- `LICENSE` - MIT License (ConQuest Data Limited)

### Benefits

- ✅ Significantly fewer Windows security warnings
- ✅ Professional installation experience
- ✅ Proper uninstaller in Add/Remove Programs
- ✅ Desktop and Start Menu shortcuts
- ✅ Registry integration
- ✅ Optional startup integration

---
Copyright (c) 2025 ConQuest Data Limited