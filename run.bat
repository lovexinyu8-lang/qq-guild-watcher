@echo off
chcp 65001 >nul
cd /d "%~dp0"

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python src\main.py %*
    goto end
)

if exist "C:\Users\39024\miniconda3\python.exe" (
    "C:\Users\39024\miniconda3\python.exe" src\main.py %*
    goto end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" src\main.py %*
    goto end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" src\main.py %*
    goto end
)

echo ======================================================
echo [Error] Python runtime not detected!
echo Windows 10/11 Quick Install: winget install Python.Python.3.11
echo ======================================================
pause

:end
if %ERRORLEVEL% NEQ 0 (
    pause
)
