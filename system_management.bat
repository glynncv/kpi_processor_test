@echo off
REM System Information and Management
setlocal enabledelayedexpansion

:SYSTEM_MENU
cls
echo.
echo ================================================================================
echo                         SYSTEM MANAGEMENT
echo ================================================================================
echo.
echo 1. View System Status
echo 2. Check Cache Status  
echo 3. Clear Cache
echo 4. View Log Files
echo 5. Show Results Summary
echo 6. Test System
echo 7. Show Final Summary
echo 8. Environment Check
echo.
echo 0. Exit
echo.
set /p choice="Enter your choice (0-8): "

if "%choice%"=="1" goto SYSTEM_STATUS
if "%choice%"=="2" goto CACHE_STATUS
if "%choice%"=="3" goto CLEAR_CACHE
if "%choice%"=="4" goto VIEW_LOGS
if "%choice%"=="5" goto SHOW_RESULTS
if "%choice%"=="6" goto TEST_SYSTEM
if "%choice%"=="7" goto FINAL_SUMMARY
if "%choice%"=="8" goto ENV_CHECK
if "%choice%"=="0" goto EXIT

echo Invalid choice. Please try again.
pause
goto SYSTEM_MENU

:SYSTEM_STATUS
cls
echo.
echo ================================================================================
echo                            SYSTEM STATUS
echo ================================================================================
echo.
echo Configuration Status:
if exist "config\kpi_config.yaml" (
    echo   ✓ Configuration file: config\kpi_config.yaml
) else (
    echo   ✗ Configuration file: MISSING
)
echo.

echo Data Status:
echo   Available data files:
if exist "data" (
    dir /b data\*.csv 2>nul
    if %ERRORLEVEL% NEQ 0 echo     No CSV files found
) else (
    echo     Data directory not found
)
echo.

echo Cache Status:
if exist "cache" (
    echo   ✓ Cache directory exists
    if exist "cache\baseline_counts.json" echo   ✓ Baseline cache available
    if exist "cache\kpi_cache.json" echo   ✓ KPI cache available
    if exist "cache\record_signatures.pkl" echo   ✓ Record signatures available
    if exist "cache\last_processed.json" echo   ✓ Last processed metadata available
) else (
    echo   ✗ Cache directory not found
)
echo.

echo Output Status:
if exist "output" (
    echo   ✓ Output directory exists
    dir /b output\*.json 2>nul
    if %ERRORLEVEL% NEQ 0 echo     No result files found
) else (
    echo   ✗ Output directory not found
)

pause
goto SYSTEM_MENU

:CACHE_STATUS
cls
echo.
echo ================================================================================
echo                            CACHE STATUS
echo ================================================================================
echo.
if not exist "cache" (
    echo Cache directory does not exist.
    echo No processing has been performed yet.
) else (
    echo Cache directory contents:
    echo.
    dir cache /s
    echo.
    if exist "cache\last_processed.json" (
        echo Last processing metadata:
        type cache\last_processed.json
    )
)
pause
goto SYSTEM_MENU

:CLEAR_CACHE
cls
echo.
echo ================================================================================
echo                             CLEAR CACHE
echo ================================================================================
echo.
echo Warning: This will remove all cached processing data.
echo You will need to run baseline processing again.
echo.
set /p confirm="Are you sure you want to clear the cache? (y/n): "
if /i "%confirm%"=="y" (
    if exist "cache" (
        echo Clearing cache...
        rd /s /q cache
        echo ✓ Cache cleared successfully.
    ) else (
        echo Cache directory does not exist.
    )
) else (
    echo Cache not cleared.
)
pause
goto SYSTEM_MENU

:VIEW_LOGS
cls
echo.
echo ================================================================================
echo                             VIEW LOGS
echo ================================================================================
echo.
if exist "logs" (
    echo Available log files:
    dir /b logs\*.log 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo.
        set /p logfile="Enter log file name to view (or press Enter to skip): "
        if not "!logfile!"=="" (
            if exist "logs\!logfile!" (
                echo.
                echo Contents of logs\!logfile!:
                echo ----------------------------------------
                type logs\!logfile!
            ) else (
                echo Log file not found.
            )
        )
    ) else (
        echo No log files found.
    )
) else (
    echo Logs directory does not exist.
)
pause
goto SYSTEM_MENU

:SHOW_RESULTS
cls
echo.
echo ================================================================================
echo                           SHOW RESULTS
echo ================================================================================
echo.
python show_results.py
pause
goto SYSTEM_MENU

:TEST_SYSTEM
cls
echo.
echo ================================================================================
echo                            TEST SYSTEM
echo ================================================================================
echo.
python test_system.py
pause
goto SYSTEM_MENU

:FINAL_SUMMARY
cls
echo.
echo ================================================================================
echo                           FINAL SUMMARY
echo ================================================================================
echo.
python final_summary.py
pause
goto SYSTEM_MENU

:ENV_CHECK
cls
echo.
echo ================================================================================
echo                          ENVIRONMENT CHECK
echo ================================================================================
echo.
echo Python Version:
python --version
echo.

echo Python Executable:
where python
echo.

echo Required Packages:
echo Checking pandas...
python -c "import pandas; print('✓ pandas version:', pandas.__version__)" 2>nul || echo "✗ pandas not found"
echo Checking PyYAML...
python -c "import yaml; print('✓ PyYAML available')" 2>nul || echo "✗ PyYAML not found"
echo Checking pathlib...
python -c "import pathlib; print('✓ pathlib available')" 2>nul || echo "✗ pathlib not found"

echo.
echo Current Directory:
cd
echo.

echo Directory Structure:
if exist "scripts" echo   ✓ scripts/
if exist "config" echo   ✓ config/
if exist "data" echo   ✓ data/
if exist "output" echo   ✓ output/
if exist "cache" echo   ✓ cache/
if exist "logs" echo   ✓ logs/

pause
goto SYSTEM_MENU

:EXIT
exit /b
