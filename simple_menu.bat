@echo off
setlocal enabledelayedexpansion
title KPI Processor - Enhanced Simple Menu

:MAIN_MENU
cls
echo.
echo ================================================================================
echo                           KPI PROCESSING SYSTEM
echo                            Enhanced Simple Menu
echo ================================================================================
echo.
echo 1. Quick Baseline Processing (Default Settings)
echo 2. Run System Test
echo 3. Show Latest Results
echo 4. View System Summary
echo 5. Validate Configuration
echo 6. Browse Output Files
echo 7. Clear Cache
echo 8. Advanced Menu
echo 9. Exit
echo.

REM Check system status
echo Status Checks:
if exist "config\kpi_config.yaml" (
    echo   ✓ Configuration file found
) else (
    echo   ✗ Configuration file missing
)

if exist "data\consolidated_data.csv" (
    echo   ✓ Default data file found
) else (
    echo   ✗ Default data file missing
)

if exist "output" (
    for /f %%i in ('dir /b output\*.json 2^>nul ^| find /c /v ""') do set result_count=%%i
    if !result_count! GTR 0 (
        echo   ✓ !result_count! result files available
    ) else (
        echo   ? No result files found
    )
) else (
    echo   ? Output directory not found
)

echo.
set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" goto QUICK_BASELINE
if "%choice%"=="2" goto TEST_SYSTEM
if "%choice%"=="3" goto SHOW_RESULTS
if "%choice%"=="4" goto SYSTEM_SUMMARY
if "%choice%"=="5" goto VALIDATE_CONFIG
if "%choice%"=="6" goto BROWSE_OUTPUT
if "%choice%"=="7" goto CLEAR_CACHE
if "%choice%"=="8" goto ADVANCED_MENU
if "%choice%"=="9" goto EXIT

:QUICK_BASELINE
cls
echo.
echo ================================================================================
echo                          QUICK BASELINE PROCESSING
echo ================================================================================
echo.

REM Pre-flight checks
echo Performing pre-flight checks...
if not exist "config\kpi_config.yaml" (
    echo ❌ ERROR: Configuration file not found!
    echo Please ensure config\kpi_config.yaml exists.
    pause
    goto MAIN_MENU
)

if not exist "data\consolidated_data.csv" (
    echo ⚠️  WARNING: Default data file not found!
    echo.
    echo Available data files:
    if exist "data" (
        dir /b data\*.csv 2>nul
        echo.
        set /p datafile="Enter data file name (with .csv extension): "
        if not exist "data\!datafile!" (
            echo ❌ ERROR: File data\!datafile! not found!
            pause
            goto MAIN_MENU
        )
        set "input_file=data\!datafile!"
    ) else (
        echo ❌ ERROR: Data directory not found!
        pause
        goto MAIN_MENU
    )
) else (
    set "input_file=data\consolidated_data.csv"
    echo ✅ Using default data file: consolidated_data.csv
)

REM Create output directory if it doesn't exist
if not exist "output" mkdir output

echo.
echo ================================================================================
echo Starting baseline processing...
echo Configuration: config\kpi_config.yaml
echo Input Data: !input_file!
echo Output: output\quick_results.json
echo ================================================================================
echo.

python scripts\complete_configurable_processor_fixed.py --config config\kpi_config.yaml --mode baseline --input "!input_file!" --output output\quick_results.json

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ SUCCESS: Baseline processing completed!
    echo 📄 Results saved to: output\quick_results.json
    echo.
    set /p view="View results now? (y/n): "
    if /i "!view!"=="y" (
        python show_results.py
    )
) else (
    echo.
    echo ❌ ERROR: Processing failed with error code %ERRORLEVEL%
    echo Please check the configuration and data files.
)

echo.
echo Press any key to return to menu...
pause > nul
goto MAIN_MENU

:SYSTEM_SUMMARY
cls
echo.
echo ================================================================================
echo                             SYSTEM SUMMARY
echo ================================================================================
echo.

python final_summary.py

echo.
echo Press any key to return to menu...
pause > nul
goto MAIN_MENU

:VALIDATE_CONFIG
cls
echo.
echo ================================================================================
echo                          CONFIGURATION VALIDATION
echo ================================================================================
echo.

echo Validating system configuration...
echo.

if exist "scripts\config_validator_fixed.py" (
    python scripts\config_validator_fixed.py --config config\kpi_config.yaml --strict
) else if exist "scripts\config_validator.py" (
    echo ⚠️  Using fallback validator...
    python scripts\config_validator.py --config config\kpi_config.yaml --strict
) else (
    echo ❌ ERROR: Configuration validator not found!
    echo Please ensure config validator script exists in scripts directory.
)

echo.
echo Press any key to return to menu...
pause > nul
goto MAIN_MENU

:BROWSE_OUTPUT
cls
echo.
echo ================================================================================
echo                            BROWSE OUTPUT FILES
echo ================================================================================
echo.

if not exist "output" (
    echo ❌ Output directory does not exist!
    echo Run some processing first to generate output files.
    pause
    goto MAIN_MENU
)

echo 📁 Output Directory Contents:
echo.
dir output\*.json /o:d 2>nul

if %ERRORLEVEL% NEQ 0 (
    echo ❌ No JSON result files found in output directory.
    echo Run some processing first to generate results.
) else (
    echo.
    echo Recent files are listed last.
    echo.
    set /p open_folder="Open output folder in Windows Explorer? (y/n): "
    if /i "!open_folder!"=="y" (
        start explorer output
    )
)

echo.
echo Press any key to return to menu...
pause > nul
goto MAIN_MENU

:CLEAR_CACHE
cls
echo.
echo ================================================================================
echo                               CLEAR CACHE
echo ================================================================================
echo.

echo This will clear all cached processing data including:
echo • Baseline counts
echo • KPI cache
echo • Record signatures
echo • Last processed information
echo.
echo ⚠️  WARNING: This will require full baseline reprocessing next time!
echo.
set /p confirm="Are you sure you want to clear the cache? (y/n): "

if /i "%confirm%"=="y" (
    echo.
    echo Clearing cache...
    
    if exist "cache" (
        rd /s /q cache
        echo ✅ Cache directory cleared.
    ) else (
        echo ℹ️  Cache directory does not exist.
    )
    
    if exist "test_cache" (
        rd /s /q test_cache
        echo ✅ Test cache directory cleared.
    )
    
    echo.
    echo ✅ Cache clearing completed!
    echo Next processing run will perform full baseline calculation.
) else (
    echo ❌ Cache clearing cancelled.
)

echo.
echo Press any key to return to menu...
pause > nul
goto MAIN_MENU

:ADVANCED_MENU
cls
echo.
echo ================================================================================
echo                             ADVANCED OPTIONS
echo ================================================================================
echo.
echo 1. Run Incremental Processing
echo 2. Run Targeted KPI Processing
echo 3. Custom Processing Options
echo 4. System Management
echo 5. Back to Simple Menu
echo.
set /p adv_choice="Enter your choice (1-5): "

if "%adv_choice%"=="1" goto INCREMENTAL_PROCESSING
if "%adv_choice%"=="2" goto TARGETED_PROCESSING
if "%adv_choice%"=="3" goto CUSTOM_PROCESSING
if "%adv_choice%"=="4" goto SYSTEM_MANAGEMENT
if "%adv_choice%"=="5" goto MAIN_MENU

echo Invalid choice. Please try again.
pause
goto ADVANCED_MENU

:INCREMENTAL_PROCESSING
cls
echo.
echo ================================================================================
echo                         INCREMENTAL PROCESSING
echo ================================================================================
echo.

echo Checking for baseline cache...
if not exist "cache\baseline_counts.json" (
    echo ❌ ERROR: No baseline cache found!
    echo You must run baseline processing first.
    echo.
    set /p run_baseline="Run baseline processing now? (y/n): "
    if /i "!run_baseline!"=="y" goto QUICK_BASELINE
    pause
    goto ADVANCED_MENU
)

echo ✅ Baseline cache found. Proceeding with incremental processing...
echo.

echo Available data files:
if exist "data" (
    dir /b data\*.csv 2>nul
    echo.
    set /p datafile="Enter data file name (with .csv extension): "
    if not exist "data\!datafile!" (
        echo ❌ ERROR: File data\!datafile! not found!
        pause
        goto ADVANCED_MENU
    )
) else (
    echo ❌ ERROR: Data directory not found!
    pause
    goto ADVANCED_MENU
)

echo.
echo Running incremental processing...
python scripts\complete_configurable_processor_fixed.py --config config\kpi_config.yaml --mode incremental --input "data\!datafile!" --output output\incremental_results.json

echo.
echo Press any key to return to advanced menu...
pause > nul
goto ADVANCED_MENU

:TARGETED_PROCESSING
cls
echo.
echo ================================================================================
echo                          TARGETED KPI PROCESSING
echo ================================================================================
echo.

echo Available KPIs:
echo   SM001 - Major Incidents (Priority 1 & 2)
echo   SM002 - ServiceNow Backlog
echo   SM003 - Service Request Aging
echo   SM004 - First Time Fix Rate
echo   GEOGRAPHIC - Geographic Analysis
echo.
set /p kpi_id="Enter KPI ID: "

echo.
echo Available data files:
if exist "data" (
    dir /b data\*.csv 2>nul
    echo.
    set /p datafile="Enter data file name (with .csv extension): "
    if not exist "data\!datafile!" (
        echo ❌ ERROR: File data\!datafile! not found!
        pause
        goto ADVANCED_MENU
    )
) else (
    echo ❌ ERROR: Data directory not found!
    pause
    goto ADVANCED_MENU
)

echo.
echo Running targeted processing for %kpi_id%...
python scripts\complete_configurable_processor_fixed.py --config config\kpi_config.yaml --mode targeted --kpi %kpi_id% --input "data\!datafile!" --output "output\targeted_%kpi_id%_results.json"

echo.
echo Press any key to return to advanced menu...
pause > nul
goto ADVANCED_MENU

:CUSTOM_PROCESSING
cls
echo.
echo ================================================================================
echo                           CUSTOM PROCESSING OPTIONS
echo ================================================================================
echo.

echo 1. Process with custom cache directory
echo 2. Process without configuration validation
echo 3. Process with custom output file
echo 4. Back to advanced menu
echo.
set /p custom_choice="Enter your choice (1-4): "

if "%custom_choice%"=="1" goto CUSTOM_CACHE
if "%custom_choice%"=="2" goto NO_VALIDATION
if "%custom_choice%"=="3" goto CUSTOM_OUTPUT
if "%custom_choice%"=="4" goto ADVANCED_MENU

echo Invalid choice. Please try again.
pause
goto CUSTOM_PROCESSING

:CUSTOM_CACHE
echo.
set /p cache_dir="Enter custom cache directory name: "
set /p datafile="Enter data file name (from data folder): "
echo.
echo Running with custom cache directory: %cache_dir%
python scripts\complete_configurable_processor_fixed.py --config config\kpi_config.yaml --mode baseline --input "data\%datafile%" --cache-dir "%cache_dir%"
pause
goto CUSTOM_PROCESSING

:NO_VALIDATION
echo.
set /p datafile="Enter data file name (from data folder): "
echo.
echo Running without configuration validation...
python scripts\complete_configurable_processor_fixed.py --config config\kpi_config.yaml --mode baseline --input "data\%datafile%" --no-validation
pause
goto CUSTOM_PROCESSING

:CUSTOM_OUTPUT
echo.
set /p datafile="Enter data file name (from data folder): "
set /p output_file="Enter output file name (with .json extension): "
echo.
echo Running with custom output file: %output_file%
python scripts\complete_configurable_processor_fixed.py --config config\kpi_config.yaml --mode baseline --input "data\%datafile%" --output "%output_file%"
pause
goto CUSTOM_PROCESSING

:SYSTEM_MANAGEMENT
cls
echo.
echo ================================================================================
echo                            SYSTEM MANAGEMENT
echo ================================================================================
echo.

echo 1. View System Information
echo 2. Check Python Environment
echo 3. View Log Files
echo 4. Backup Results
echo 5. Back to advanced menu
echo.
set /p sys_choice="Enter your choice (1-5): "

if "%sys_choice%"=="1" goto SYSTEM_INFO
if "%sys_choice%"=="2" goto PYTHON_INFO
if "%sys_choice%"=="3" goto VIEW_LOGS
if "%sys_choice%"=="4" goto BACKUP_RESULTS
if "%sys_choice%"=="5" goto ADVANCED_MENU

echo Invalid choice. Please try again.
pause
goto SYSTEM_MANAGEMENT

:SYSTEM_INFO
echo.
echo System Information:
echo ===================
echo Current Directory: %CD%
echo Date/Time: %DATE% %TIME%
echo.
echo Directory Structure:
if exist "config" echo ✓ config directory exists
if exist "data" echo ✓ data directory exists
if exist "output" echo ✓ output directory exists
if exist "scripts" echo ✓ scripts directory exists
if exist "cache" echo ✓ cache directory exists
if exist "logs" echo ✓ logs directory exists
echo.
pause
goto SYSTEM_MANAGEMENT

:PYTHON_INFO
echo.
echo Python Environment Information:
echo ===============================
python --version 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python not found in PATH
) else (
    echo ✅ Python is available
)
echo.
echo Checking required modules...
python -c "import pandas; print('✓ pandas available')" 2>nul || echo "❌ pandas not available"
python -c "import yaml; print('✓ yaml available')" 2>nul || echo "❌ yaml not available"
python -c "import pathlib; print('✓ pathlib available')" 2>nul || echo "❌ pathlib not available"
echo.
pause
goto SYSTEM_MANAGEMENT

:VIEW_LOGS
echo.
echo Log Files:
echo ==========
if exist "logs" (
    dir logs\*.log /o:d 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo No log files found.
    ) else (
        echo.
        set /p view_log="View latest log file? (y/n): "
        if /i "!view_log!"=="y" (
            for /f "delims=" %%i in ('dir logs\*.log /b /o:d 2^>nul') do set latest_log=%%i
            if defined latest_log (
                type "logs\!latest_log!"
            )
        )
    )
) else (
    echo Logs directory does not exist.
)
echo.
pause
goto SYSTEM_MANAGEMENT

:BACKUP_RESULTS
echo.
echo Backup Results:
echo ===============
if not exist "output" (
    echo No output directory found.
    pause
    goto SYSTEM_MANAGEMENT
)

set backup_name=backup_%DATE:~-4%%DATE:~-7,2%%DATE:~-10,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set backup_name=%backup_name: =0%

echo Creating backup: %backup_name%
xcopy output "backup\%backup_name%\output" /E /I /Y >nul 2>&1
if exist "cache" xcopy cache "backup\%backup_name%\cache" /E /I /Y >nul 2>&1

if %ERRORLEVEL% EQU 0 (
    echo ✅ Backup created successfully in backup\%backup_name%
) else (
    echo ❌ Backup failed
)
echo.
pause
goto SYSTEM_MANAGEMENT

:TEST_SYSTEM
cls
echo.
echo ================================================================================
echo                              TEST SYSTEM
echo ================================================================================
echo.

echo Running comprehensive system test...
echo This will validate configuration, test processing, and check system health.
echo.

python test_system.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ System test completed successfully!
) else (
    echo.
    echo ⚠️  System test completed with warnings or errors.
    echo Please review the output above for details.
)

echo.
echo Press any key to return to menu...
pause > nul
goto MAIN_MENU

:SHOW_RESULTS
cls
echo.
echo ================================================================================
echo                             SHOW RESULTS
echo ================================================================================
echo.

echo Loading results display system...
python show_results.py

echo.
echo Press any key to return to menu...
pause > nul
goto MAIN_MENU

:EXIT
cls
echo.
echo ================================================================================
echo                    THANK YOU FOR USING KPI PROCESSOR
echo ================================================================================
echo.
echo 🎯 System Features Used:
echo   • Enhanced menu navigation
echo   • Automated error checking
echo   • Comprehensive result display
echo   • System health monitoring
echo.
echo 💡 Next Steps:
echo   • Schedule regular KPI processing
echo   • Review system recommendations
echo   • Monitor performance trends
echo.
echo 📧 Support: IT Service Management Team
echo ================================================================================
echo.
pause
exit /b
