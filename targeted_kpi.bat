@echo off
REM Targeted KPI Processing with menu - Updated for data/raw/ auto-detection
setlocal enabledelayedexpansion

:TARGETED_MENU
cls
echo.
echo ================================================================================
echo                        TARGETED KPI PROCESSING
echo ================================================================================
echo.
echo Auto-detects latest data from data\raw\ (or data\ as fallback)
echo.
echo Select KPI to process:
echo.
echo 1. SM001 - Major Incidents (Priority 1 & 2)
echo 2. SM002 - ServiceNow Backlog
echo 3. SM003 - Service Request Aging (if enabled)
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

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  Python not found!
    pause
    goto TARGETED_MENU
)

REM Check for main processor
if not exist "kpi_processor.py" (
    echo  kpi_processor.py not found!
    pause
    goto TARGETED_MENU
)

echo Available data files:
echo.
echo In data\raw\:
if exist "data\raw\" (
    dir /b data\raw\*.csv 2>nul
) else (
    echo   (data\raw\ directory not found)
)

echo.
echo In data\:
if exist "data\" (
    dir /b data\*.csv 2>nul
) else (
    echo   (data\ directory not found)
)

echo.
echo Auto-detecting latest CSV file...

REM Create output directory if it doesn't exist
if not exist "output" mkdir output

echo.
echo  Processing KPI: %kpi%
echo   Using latest data file (auto-detected)
echo   Config: config\kpi_config.yaml
echo.

REM Use the updated kpi_processor.py with auto-detection
python kpi_processor.py --mode targeted --kpi %kpi% --config config/kpi_config.yaml

if %ERRORLEVEL% EQU 0 (
    echo.
    echo  Targeted processing completed successfully!
    echo Results processed and saved to output directory
    echo.
    echo KPI Details:
    if "%kpi%"=="SM001" echo   - Tracks Priority 1 and Priority 2 incidents
    if "%kpi%"=="SM002" echo   - Monitors ServiceNow backlog aging
    if "%kpi%"=="SM003" echo   - Analyzes service request aging patterns (may be disabled)
    if "%kpi%"=="SM004" echo   - Measures first-time fix rate effectiveness
    if "%kpi%"=="GEOGRAPHIC" echo   - Provides geographic distribution analysis
    
    echo.
    echo Output files:
    if exist "output\" (
        dir /b output\*.json | findstr /i "%kpi%"
        if errorlevel 1 (
            echo   Latest results in output directory:
            dir /b output\*.json | sort /r
        )
    )
) else (
    echo.
    echo  Processing failed with error code %ERRORLEVEL%
    echo.
    echo Possible issues:
    echo   - No CSV files found in data\raw\ or data\
    echo   - Configuration file missing: config\kpi_config.yaml
    echo   - Invalid KPI selection: %kpi%
)

echo.
set /p continue="Process another KPI? (y/n): "
if /i "%continue%"=="y" goto TARGETED_MENU

:EXIT
exit /b
