@echo off
REM Complete build script for txttovoice professional installer
REM ConQuest Data Limited

echo ========================================
echo txttovoice - Complete Build Process
echo ConQuest Data Limited
echo ========================================

REM Step 1: Build executable
echo Step 1: Building executable...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "txttovoice.exe" del "txttovoice.exe"

pyinstaller txttovoice.spec

if exist "dist\txttovoice.exe" (
    copy "dist\txttovoice.exe" "txttovoice.exe" >nul
    echo SUCCESS: Executable built
) else (
    echo ERROR: Executable build failed!
    pause
    exit /b 1
)

REM Step 2: Build installer
echo.
echo Step 2: Building professional installer...
call make_installer.bat

echo.
echo Build complete! Files ready for distribution:
echo - txttovoice-installer.exe (RECOMMENDED - fewer security warnings)
echo - txttovoice.exe (raw executable)
echo.