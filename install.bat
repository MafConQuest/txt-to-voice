@echo off
echo.
echo ========================================
echo    txttovoice - Professional Installer
echo    Visit: https://txttovoice.com
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python found
python --version
echo.

REM Install dependencies
echo 📦 Installing dependencies...
echo.
python -m pip install --upgrade pip --quiet
python -m pip install pygame requests pyautogui pyperclip pystray pillow pynput --quiet

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies
    echo Try running as Administrator or check your internet connection
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully
echo.

REM Create desktop shortcut
echo 🖥️ Creating desktop shortcut...
set "SCRIPT_DIR=%~dp0"
set "PYTHON_SCRIPT=%SCRIPT_DIR%txttovoice.py"
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\txttovoice.lnk"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = '\"%PYTHON_SCRIPT%\"'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.Description = 'txttovoice - Professional Text-to-Speech'; $Shortcut.Save()"

if exist "%SHORTCUT%" (
    echo ✅ Desktop shortcut created
) else (
    echo ⚠️ Could not create desktop shortcut
)

echo.
echo 🎉 Installation Complete!
echo.
echo txttovoice has been installed successfully!
echo.
echo 🚀 Next Steps:
echo 1. Get an OpenAI API key from: https://platform.openai.com/api-keys
echo 2. Launch txttovoice from your desktop
echo 3. Click 'Settings' and enter your API key
echo 4. Start converting text to speech!
echo.
echo 💡 Pro Tips:
echo • Use Ctrl+Shift+J to convert selected text from anywhere
echo • Minimize to system tray for background operation
echo • Visit txttovoice.com for updates and support
echo.

set /p "RUN_NOW=Launch txttovoice now? (y/n): "
if /i "%RUN_NOW%"=="y" (
    echo.
    echo 🚀 Starting txttovoice...
    python "%PYTHON_SCRIPT%"
)

echo.
echo Thank you for using txttovoice! 🎤
echo Visit https://txttovoice.com for support
pause