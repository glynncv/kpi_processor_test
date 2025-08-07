@echo off
REM Complete Pipeline
echo  Complete Pipeline
echo ===================

python --version >nul 2>&1
if errorlevel 1 (
    echo  Python not found!
    pause
    exit /b 1
)

if not exist "kpi_processor.py" (
    echo  kpi_processor.py not found!
    pause
    exit /b 1
)

echo Running baseline...
python kpi_processor.py --mode baseline

echo Running incremental...
python kpi_processor.py --mode incremental

echo  Pipeline complete!
pause
