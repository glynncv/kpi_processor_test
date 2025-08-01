@echo off
REM Quick Incremental Processing - No prompts, uses defaults
setlocal

echo.
echo ================================================================================
echo                     QUICK INCREMENTAL PROCESSING
echo ================================================================================
echo.

REM Check if default data file exists
if not exist "data\consolidated_data.csv" (
    echo Error: Default data file 'data\consolidated_data.csv' not found!
    echo.
    echo Available data files:
    dir /b data\*.csv 2>nul
    echo.
    echo Please ensure consolidated_data.csv exists in the data folder.
    pause
    exit /b 1
)

REM Check if config exists
if not exist "config\kpi_config.yaml" (
    echo Error: Configuration file 'config\kpi_config.yaml' not found!
    pause
    exit /b 1
)

REM Check if baseline cache exists
if not exist "cache\baseline_counts.json" (
    echo Warning: No baseline cache found!
    echo You may need to run baseline processing first.
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "!continue!"=="y" exit /b 0
)

REM Create output directory if it doesn't exist
if not exist "output" mkdir output

echo Running incremental processing with default settings...
echo Config: config\kpi_config.yaml
echo Data: data\consolidated_data.csv
echo Output: output\incremental_quick.json
echo.

python scripts\complete_configurable_processor_fixed.py ^
    --config config\kpi_config.yaml ^
    --mode incremental ^
    --input data\consolidated_data.csv ^
    --output output\incremental_quick.json

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Quick incremental processing completed successfully!
    echo Results saved to: output\incremental_quick.json
) else (
    echo.
    echo ✗ Processing failed with error code %ERRORLEVEL%
)

echo.
pause
