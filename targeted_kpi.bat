@echo off
REM Targeted KPI Processing with menu
setlocal enabledelayedexpansion

:TARGETED_MENU
cls
echo.
echo ================================================================================
echo                        TARGETED KPI PROCESSING
echo ================================================================================
echo.
echo Select KPI to process:
echo.
echo 1. SM001 - Major Incidents (Priority 1 & 2)
echo 2. SM002 - ServiceNow Backlog
echo 3. SM003 - Service Request Aging  
echo 4. SM004 - First Time Fix Rate
echo 5. GEOGRAPHIC - Geographic Analysis
echo.
echo 0. Exit
echo.
set /p choice="Enter your choice (0-5): "

if "%choice%"=="1" set "kpi=SM001" & goto PROCESS_KPI
if "%choice%"=="2" set "kpi=SM002" & goto PROCESS_KPI  
if "%choice%"=="3" set "kpi=SM003" & goto PROCESS_KPI
if "%choice%"=="4" set "kpi=SM004" & goto PROCESS_KPI
if "%choice%"=="5" set "kpi=GEOGRAPHIC" & goto PROCESS_KPI
if "%choice%"=="0" goto EXIT

echo Invalid choice. Please try again.
pause
goto TARGETED_MENU

:PROCESS_KPI
cls
echo.
echo ================================================================================
echo                     PROCESSING KPI: %kpi%
echo ================================================================================
echo.
echo Available data files:
dir /b data\*.csv 2>nul
echo.
set /p datafile="Enter data file name (from data folder): "
if not exist "data\%datafile%" (
    echo Error: File data\%datafile% not found!
    pause
    goto TARGETED_MENU
)

REM Create output directory if it doesn't exist
if not exist "output" mkdir output

echo.
echo Processing %kpi% with data\%datafile%...
echo.

python scripts\complete_configurable_processor_fixed.py ^
    --config config\kpi_config.yaml ^
    --mode targeted ^
    --kpi %kpi% ^
    --input data\%datafile% ^
    --output output\targeted_%kpi%_results.json

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Targeted processing completed successfully!
    echo Results saved to: output\targeted_%kpi%_results.json
    echo.
    echo KPI Details:
    if "%kpi%"=="SM001" echo   - Tracks Priority 1 and Priority 2 incidents
    if "%kpi%"=="SM002" echo   - Monitors ServiceNow backlog aging
    if "%kpi%"=="SM003" echo   - Analyzes service request aging patterns
    if "%kpi%"=="SM004" echo   - Measures first-time fix rate effectiveness
    if "%kpi%"=="GEOGRAPHIC" echo   - Provides geographic distribution analysis
) else (
    echo.
    echo ✗ Processing failed with error code %ERRORLEVEL%
)

echo.
set /p continue="Process another KPI? (y/n): "
if /i "%continue%"=="y" goto TARGETED_MENU

:EXIT
exit /b
