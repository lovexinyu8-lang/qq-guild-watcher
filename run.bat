@echo off
chcp 65001 >nul
title QQ Guild Watcher - 频道监控与预警
echo ======================================================
echo   QQ Guild Watcher (QQ频道多论坛监控与预警系统)
echo ======================================================
echo.

cd /d "%~dp0"

REM 优先使用系统 PATH 中的 python，若不存在则探测常见安装路径
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python src\main.py %*
) else (
    if exist "C:\Users\39024\miniconda3\python.exe" (
        "C:\Users\39024\miniconda3\python.exe" src\main.py %*
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" src\main.py %*
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" src\main.py %*
    ) else (
        echo ======================================================
        echo [提示] 未检测到 Python 运行环境！
        echo 纯小白极速安装方法 (Windows 10 / 11):
        echo 1. 按 Win + R 输入 cmd 打开黑窗口；
        echo 2. 粘贴输入并回车: winget install Python.Python.3.11
        echo 3. 安装完成后重新双击本脚本即可。
        echo ======================================================
        pause
    )
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 程序异常退出，错误代码: %ERRORLEVEL%
    pause
)
