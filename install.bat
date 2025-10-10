@echo off
echo.
echo ========================================
echo    txttovoice - Professional Installer
echo    Visit: https://txttovoice.com
echo ========================================
echo.

REM Check if executable exists
if not exist "txttovoice.exe" (
    echo [ERROR] txttovoice.exe not found!
    echo Please make sure you downloaded the complete package.
    pause
    exit /b 1
)

REM Create application directory
set "INSTALL_DIR=%LOCALAPPDATA%\txttovoice"
echo 📁 Creating application directory...
mkdir "%INSTALL_DIR%" 2>nul

REM Copy executable and files
echo 📋 Installing txttovoice...
copy "txttovoice.exe" "%INSTALL_DIR%\txttovoice.exe" >nul
if exist "README.md" copy "README.md" "%INSTALL_DIR%\" >nul
if exist "LICENSE" copy "LICENSE" "%INSTALL_DIR%\" >nul

REM Create desktop shortcut
echo 🖥️ Creating desktop shortcut...
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\txttovoice.lnk"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\txttovoice.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'txttovoice - Professional Text-to-Speech'; $Shortcut.Save()"

if exist "%SHORTCUT%" (
    echo ✅ Desktop shortcut created
) else (
    echo ⚠️ Could not create desktop shortcut
)

REM Create start menu shortcut
echo 📋 Creating start menu shortcut...
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\txttovoice.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\txttovoice.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'txttovoice - Professional Text-to-Speech'; $Shortcut.Save()"

REM Add to startup (optional)
echo.
set /p "STARTUP=Add txttovoice to Windows startup? (y/n): "
if /i "%STARTUP%"=="y" (
    echo 🚀 Adding to Windows startup...
    reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "txttovoice" /t REG_SZ /d "%INSTALL_DIR%\txttovoice.exe" /f >nul
    echo ✅ Added to startup
)

REM Create uninstaller
echo 📝 Creating uninstaller...
(
echo @echo off
echo echo 🗑️ txttovoice - Uninstaller
echo echo ============================
echo echo Removing txttovoice...
echo reg delete "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "txttovoice" /f ^>nul 2^>^&1
echo del "%DESKTOP%\txttovoice.lnk" ^>nul 2^>^&1
echo del "%START_MENU%\txttovoice.lnk" ^>nul 2^>^&1
echo cd /d "%LOCALAPPDATA%"
echo rmdir /s /q "txttovoice"
echo echo ✅ txttovoice has been uninstalled successfully!
echo pause
) > "%INSTALL_DIR%\Uninstall.bat"

echo.
echo 🎉 Installation Complete!
echo.
echo txttovoice has been installed successfully!
echo.
echo 📁 Installed to: %INSTALL_DIR%
echo 🖥️ Desktop shortcut: txttovoice
echo 📋 Start menu: txttovoice  
echo 🗑️ Uninstaller: "%INSTALL_DIR%\Uninstall.bat"
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
    start "" "%INSTALL_DIR%\txttovoice.exe"
)

echo.
echo Thank you for using txttovoice! 🎤
echo Visit https://txttovoice.com for support
pause