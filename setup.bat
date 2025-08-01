@echo off
REM Setup and Installation Helper
setlocal

:SETUP_MENU
cls
echo.
echo ================================================================================
echo                           SETUP AND INSTALLATION
echo ================================================================================
echo.
echo 1. Check Python Installation
echo 2. Install Required Packages
echo 3. Setup Virtual Environment
echo 4. Create Required Directories
echo 5. Check All Dependencies
echo 6. First-Time Setup (Complete)
echo.
echo 0. Exit
echo.
set /p choice="Enter your choice (0-6): "

if "%choice%"=="1" goto CHECK_PYTHON
if "%choice%"=="2" goto INSTALL_PACKAGES
if "%choice%"=="3" goto SETUP_VENV
if "%choice%"=="4" goto CREATE_DIRS
if "%choice%"=="5" goto CHECK_DEPS
if "%choice%"=="6" goto FIRST_TIME_SETUP
if "%choice%"=="0" goto EXIT

echo Invalid choice. Please try again.
pause
goto SETUP_MENU

:CHECK_PYTHON
cls
echo.
echo ================================================================================
echo                          CHECK PYTHON INSTALLATION
echo ================================================================================
echo.
echo Python Version:
python --version
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH!
    echo Please install Python 3.8 or higher.
    pause
    goto SETUP_MENU
)

echo.
echo Python Executable Location:
where python

echo.
echo Pip Version:
python -m pip --version

pause
goto SETUP_MENU

:INSTALL_PACKAGES
cls
echo.
echo ================================================================================
echo                         INSTALL REQUIRED PACKAGES
echo ================================================================================
echo.
echo Installing packages from requirements.txt...
echo.

if exist "requirements.txt" (
    python -m pip install -r requirements.txt
    echo.
    echo Package installation completed.
) else (
    echo requirements.txt not found. Installing core packages manually...
    python -m pip install pandas PyYAML pathlib
)

pause
goto SETUP_MENU

:SETUP_VENV
cls
echo.
echo ================================================================================
echo                        SETUP VIRTUAL ENVIRONMENT
echo ================================================================================
echo.
echo Creating virtual environment...
python -m venv venv

echo.
echo Virtual environment created. To activate:
echo   venv\Scripts\activate.bat
echo.
echo Install packages in virtual environment? (y/n):
set /p install_venv=""
if /i "%install_venv%"=="y" (
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    if exist "requirements.txt" (
        python -m pip install -r requirements.txt
    ) else (
        python -m pip install pandas PyYAML pathlib
    )
)

pause
goto SETUP_MENU

:CREATE_DIRS
cls
echo.
echo ================================================================================
echo                         CREATE REQUIRED DIRECTORIES
echo ================================================================================
echo.
echo Creating directory structure...

if not exist "scripts" mkdir scripts
if not exist "config" mkdir config
if not exist "data" mkdir data
if not exist "output" mkdir output
if not exist "cache" mkdir cache
if not exist "logs" mkdir logs

echo.
echo Directory structure created:
echo   ✓ scripts/
echo   ✓ config/
echo   ✓ data/
echo   ✓ output/
echo   ✓ cache/
echo   ✓ logs/

pause
goto SETUP_MENU

:CHECK_DEPS
cls
echo.
echo ================================================================================
echo                          CHECK ALL DEPENDENCIES
echo ================================================================================
echo.
echo Checking Python packages...
echo.
python -c "import pandas; print('✓ pandas version:', pandas.__version__)" 2>nul || echo "✗ pandas not found"
python -c "import yaml; print('✓ PyYAML available')" 2>nul || echo "✗ PyYAML not found"
python -c "import pathlib; print('✓ pathlib available')" 2>nul || echo "✗ pathlib not found"
python -c "import json; print('✓ json available')" 2>nul || echo "✗ json not found"
python -c "import pickle; print('✓ pickle available')" 2>nul || echo "✗ pickle not found"
python -c "import hashlib; print('✓ hashlib available')" 2>nul || echo "✗ hashlib not found"
python -c "import logging; print('✓ logging available')" 2>nul || echo "✗ logging not found"
python -c "import re; print('✓ re available')" 2>nul || echo "✗ re not found"
python -c "import argparse; print('✓ argparse available')" 2>nul || echo "✗ argparse not found"

echo.
echo Checking file structure...
if exist "scripts\complete_configurable_processor_fixed.py" echo ✓ Main processor script
if exist "scripts\config_validator_fixed.py" echo ✓ Config validator script
if exist "config\kpi_config.yaml" echo ✓ Configuration file
if exist "test_system.py" echo ✓ Test system script
if exist "show_results.py" echo ✓ Show results script
if exist "final_summary.py" echo ✓ Final summary script

pause
goto SETUP_MENU

:FIRST_TIME_SETUP
cls
echo.
echo ================================================================================
echo                           FIRST-TIME SETUP
echo ================================================================================
echo.
echo This will perform complete first-time setup:
echo 1. Check Python installation
echo 2. Create directory structure
echo 3. Install required packages
echo 4. Verify all dependencies
echo.
set /p confirm="Continue with first-time setup? (y/n): "
if /i not "%confirm%"=="y" goto SETUP_MENU

echo.
echo Step 1: Checking Python...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo Python installation check failed!
    pause
    goto SETUP_MENU
)

echo.
echo Step 2: Creating directories...
if not exist "scripts" mkdir scripts
if not exist "config" mkdir config
if not exist "data" mkdir data
if not exist "output" mkdir output
if not exist "cache" mkdir cache
if not exist "logs" mkdir logs
echo Directory structure created.

echo.
echo Step 3: Installing packages...
if exist "requirements.txt" (
    python -m pip install -r requirements.txt
) else (
    python -m pip install pandas PyYAML pathlib
)

echo.
echo Step 4: Verifying dependencies...
python -c "import pandas, yaml, pathlib; print('All core packages available')"
if %ERRORLEVEL% EQU 0 (
    echo ✓ First-time setup completed successfully!
) else (
    echo ✗ Setup encountered issues with package installation.
)

echo.
echo Setup complete! You can now use the KPI processing system.
pause
goto SETUP_MENU

:EXIT
exit /b
