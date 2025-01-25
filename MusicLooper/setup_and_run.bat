@echo off
setlocal enabledelayedexpansion

:: Set English messages
set "LANG_PYTHON_NOT_FOUND=Python not found! Please install Python 3.x first"
set "LANG_PYTHON_DOWNLOAD=You can download Python from https://www.python.org/downloads/"
set "LANG_CREATING_VENV=Creating virtual environment..."
set "LANG_VENV_FAILED=Failed to create virtual environment!"
set "LANG_ACTIVATING_VENV=Activating virtual environment..."
set "LANG_INSTALL_ERROR=Installation process failed!"
set "LANG_STARTING=Starting Music Looper..."

:: Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo %LANG_PYTHON_NOT_FOUND%
    echo %LANG_PYTHON_DOWNLOAD%
    pause
    exit /b 1
)
cd Data
:: Check if virtual environment exists
if not exist "venv" (
    echo %LANG_CREATING_VENV%
    python -m venv venv
    if errorlevel 1 (
        echo %LANG_VENV_FAILED%
        pause
        exit /b 1
    )
)

:: Activate virtual environment and install dependencies
echo %LANG_ACTIVATING_VENV%
call venv\Scripts\activate.bat

:: Run installation script
echo Python install packages,this may take a while...
pip install -r requirements.txt
if errorlevel 1 (
    echo %LANG_INSTALL_ERROR%
    pause
    exit /b 1
)
cls
echo Environment setup completed

:: Run the program and close CMD window
echo %LANG_STARTING%
start /b pythonw __main__.py
echo.
echo  __  __           _      _                              
echo ^|  \/  ^|_   _ ___^(_) ___^| ^|     ___   ___  _ __   ___ _ __ 
echo ^| ^|\/^| ^| ^| ^| / __^| ^|/ __^| ^|    / _ \ / _ \^| '_ \ / _ \ '__^|
echo ^| ^|  ^| ^| ^|_^| \__ \ ^| (__^| ^|___^| (_) ^| (_) ^| ^|_) ^|  __/ ^|   
echo ^|_^|  ^|_^|\__,_^|___/_^|\___^|______\___/ \___/^| .__/ \___^|_^|   
echo                                           ^|_^|            
echo.

:: Wait for pythonw.exe to start
:wait_loop
timeout /t 1 /nobreak > nul
tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I /N "pythonw.exe">NUL
if "%ERRORLEVEL%"=="1" goto wait_loop

exit