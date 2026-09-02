@echo off
setlocal enabledelayedexpansion
title Nexdemy — Smart Academic & Student Management Portal

:: Ensure working directory is always the script directory
cd /d "%~dp0"

echo ======================================================================
echo   Nexdemy — Smart Academic & Student Management Portal
echo   MySQL Engine: root / 2006 (nexdemy_db)
echo ======================================================================
echo.
echo [+] Initializing single-click launcher...
echo [+] Project Directory: %~dp0
echo.

:: 1. Try running via 'python'
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [+] Python detected. Starting Nexdemy backend server and browser...
    python run.py
    goto end
)

:: 2. Try running via Python Launcher 'py'
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [+] Python Launcher (py) detected. Starting Nexdemy backend server...
    py run.py
    goto end
)

:: 3. Try running via 'python3'
where python3 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [+] Python 3 detected. Starting Nexdemy backend server...
    python3 run.py
    goto end
)

:: 4. Fallback if Python is not installed on this computer
echo [!] Python is not found in PATH on this computer.
echo [+] Launching Nexdemy directly in your default web browser...
start "" "%~dp0index.html"
echo [OK] Nexdemy launched successfully.

:end
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Server session closed.
)
echo.
pause
