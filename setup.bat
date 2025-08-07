@echo off
REM KPI Processing System Setup
echo   KPI System Setup
echo ===================

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo  Python not found!
    pause
    exit /b 1
)

echo  Python found!

echo Creating directories...
if not exist "data" mkdir data
if not exist "output" mkdir output
if not exist "config" mkdir config

echo  Setup complete!
pause
