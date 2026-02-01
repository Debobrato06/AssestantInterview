@echo off
setlocal

echo Starting AI Interview Assistant (FastAPI Server)...
echo URL: http://localhost:8000

:: 1. Check if python is in PATH
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PY_CMD=python
    goto :run
)

:: 2. Check if py launcher is in PATH
py --version >nul 2>&1
if %errorlevel% == 0 (
    set PY_CMD=py
    goto :run
)

:: 3. Check common installation path (newly installed)
set LOCAL_PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
if exist "%LOCAL_PY%" (
    set PY_CMD="%LOCAL_PY%"
    goto :run
)

echo ERROR: Python not found! 
echo.
echo I tried searching in PATH and in %LOCALAPPDATA%\Programs\Python\Python312\
echo.
echo Please install Python from https://www.python.org/
echo Crucial: Check "Add Python to PATH" during installation.
pause
exit /b

:run
%PY_CMD% app.py
pause
