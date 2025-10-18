@echo off
echo ========================================
echo txttovoice - Professional Installer Builder
echo ConQuest Data Limited
echo ========================================

REM Try to find NSIS in common locations
set "NSIS_PATH="
where makensis >nul 2>nul && set "NSIS_PATH=makensis"
if "%NSIS_PATH%"=="" if exist "C:\Program Files (x86)\NSIS\makensis.exe" set "NSIS_PATH=C:\Program Files (x86)\NSIS\makensis.exe"
if "%NSIS_PATH%"=="" if exist "C:\Program Files\NSIS\makensis.exe" set "NSIS_PATH=C:\Program Files\NSIS\makensis.exe"

if "%NSIS_PATH%"=="" (
    echo ERROR: NSIS not found!
    echo.
    echo Please install NSIS from: https://nsis.sourceforge.io/Download
    echo Make sure to add NSIS to PATH during installation
    pause
    exit /b 1
)

if not exist "txttovoice.exe" (
    echo ERROR: txttovoice.exe not found!
    echo.
    echo Build it first with: pyinstaller txttovoice.spec
    pause
    exit /b 1
)

echo Building professional installer...
echo Using NSIS: %NSIS_PATH%
echo.

"%NSIS_PATH%" txttovoice_installer.nsi

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: txttovoice-installer.exe created!
    echo.
    echo Benefits:
    echo - Significantly fewer Windows security warnings
    echo - Professional installation experience
    echo - Proper uninstaller and shortcuts
    echo.
    set /p "TEST=Test installer now? (y/n): "
    if /i "%TEST%"=="y" start "" "txttovoice-installer.exe"
) else (
    echo ERROR: Build failed!
)

pause