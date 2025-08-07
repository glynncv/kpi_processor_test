@echo off
REM Configuration Validation
echo  Config Validator
echo ==================

python --version >nul 2>&1
if errorlevel 1 (
    echo  Python not found!
    pause
    exit /b 1
)

echo Checking directories...
if not exist "data" mkdir data
if not exist "output" mkdir output

echo  Validation complete!
pause
