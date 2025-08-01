@echo off
setlocal enabledelayedexpansion
title KPI Processor - Main Menu

:MAIN_MENU
cls
echo.
echo ================================================================================
echo                           KPI PROCESSING SYSTEM
echo                              Main Menu
echo ================================================================================
echo.
echo 1. Run Baseline Processing
echo 2. Run Incremental Processing  
echo 3. Run Targeted KPI Processing
echo 4. Validate Configuration
echo 5. Show Results
echo 6. Test System
echo 7. View Final Summary
echo 8. Quick Processing (with defaults)
echo 9. Advanced Options
echo.
echo 0. Exit
echo.
set /p choice="Enter your choice (0-9): "

if "%choice%"=="1" goto BASELINE
if "%choice%"=="2" goto INCREMENTAL
if "%choice%"=="3" goto TARGETED
if "%choice%"=="4" goto VALIDATE
if "%choice%"=="5" goto SHOW_RESULTS
if "%choice%"=="6" goto TEST_SYSTEM
if "%choice%"=="7" goto FINAL_SUMMARY
if "%choice%"=="8" goto QUICK_PROCESS
if "%choice%"=="9" goto ADVANCED
if "%choice%"=="0" goto EXIT

echo Invalid choice. Please try again.
pause
goto MAIN_MENU

:BASELINE
cls
echo.
echo ================================================================================
echo                          BASELINE PROCESSING
echo ================================================================================
echo.
echo Available data files:
dir /b data\*.csv 2>nul
echo.
set /p datafile="Enter data file name (from data folder): "
if not exist "data\%datafile%" (
    echo Error: File data\%datafile% not found!
    pause
    goto MAIN_MENU
)

echo.
echo Running baseline processing...
python scripts\complete_configurable_processor_fixed.py ^
    --config config\kpi_config.yaml ^
    --mode baseline ^
    --input data\%datafile% ^
    --output output\baseline_results.json

echo.
echo Baseline processing completed!
echo Results saved to: output\baseline_results.json
pause
goto MAIN_MENU

:INCREMENTAL
cls
echo.
echo ================================================================================
echo                         INCREMENTAL PROCESSING
echo ================================================================================
echo.
echo Available data files:
dir /b data\*.csv 2>nul
echo.
set /p datafile="Enter data file name (from data folder): "
if not exist "data\%datafile%" (
    echo Error: File data\%datafile% not found!
    pause
    goto MAIN_MENU
)

echo.
echo Running incremental processing...
python scripts\complete_configurable_processor_fixed.py ^
    --config config\kpi_config.yaml ^
    --mode incremental ^
    --input data\%datafile% ^
    --output output\incremental_results.json

echo.
echo Incremental processing completed!
echo Results saved to: output\incremental_results.json
pause
goto MAIN_MENU

:TARGETED
cls
echo.
echo ================================================================================
echo                          TARGETED KPI PROCESSING
echo ================================================================================
echo.
echo Available KPIs:
echo   SM001 - Major Incidents
echo   SM002 - ServiceNow Backlog
echo   SM003 - Service Request Aging
echo   SM004 - First Time Fix
echo   GEOGRAPHIC - Geographic Analysis
echo.
set /p kpi="Enter KPI ID (SM001/SM002/SM003/SM004/GEOGRAPHIC): "

echo.
echo Available data files:
dir /b data\*.csv 2>nul
echo.
set /p datafile="Enter data file name (from data folder): "
if not exist "data\%datafile%" (
    echo Error: File data\%datafile% not found!
    pause
    goto MAIN_MENU
)

echo.
echo Running targeted processing for %kpi%...
python scripts\complete_configurable_processor_fixed.py ^
    --config config\kpi_config.yaml ^
    --mode targeted ^
    --kpi %kpi% ^
    --input data\%datafile% ^
    --output output\targeted_%kpi%_results.json

echo.
echo Targeted processing completed!
echo Results saved to: output\targeted_%kpi%_results.json
pause
goto MAIN_MENU

:VALIDATE
cls
echo.
echo ================================================================================
echo                        CONFIGURATION VALIDATION
echo ================================================================================
echo.
echo 1. Validate configuration only
echo 2. Validate configuration with data file
echo.
set /p val_choice="Enter choice (1-2): "

if "%val_choice%"=="1" (
    echo.
    echo Validating configuration...
    python scripts\config_validator_fixed.py --config config\kpi_config.yaml --strict
) else if "%val_choice%"=="2" (
    echo.
    echo Available data files:
    dir /b data\*.csv 2>nul
    echo.
    set /p datafile="Enter data file name (from data folder): "
    if not exist "data\%datafile%" (
        echo Error: File data\%datafile% not found!
        pause
        goto MAIN_MENU
    )
    echo.
    echo Validating configuration with data...
    python scripts\config_validator_fixed.py --config config\kpi_config.yaml --data data\!datafile! --strict
)

echo.
pause
goto MAIN_MENU

:SHOW_RESULTS
cls
echo.
echo ================================================================================
echo                             SHOW RESULTS
echo ================================================================================
echo.
python show_results.py
echo.
pause
goto MAIN_MENU

:TEST_SYSTEM
cls
echo.
echo ================================================================================
echo                              TEST SYSTEM
echo ================================================================================
echo.
python test_system.py
echo.
pause
goto MAIN_MENU

:FINAL_SUMMARY
cls
echo.
echo ================================================================================
echo                            FINAL SUMMARY
echo ================================================================================
echo.
python final_summary.py
echo.
pause
goto MAIN_MENU

:QUICK_PROCESS
cls
echo.
echo ================================================================================
echo                           QUICK PROCESSING
echo ================================================================================
echo.
echo This will run baseline processing with default settings...
echo Using: config\kpi_config.yaml and data\consolidated_data.csv
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" goto MAIN_MENU

if not exist "data\consolidated_data.csv" (
    echo Error: Default data file data\consolidated_data.csv not found!
    echo Please ensure your data file exists or use the manual options.
    pause
    goto MAIN_MENU
)

echo.
echo Running quick baseline processing...
python scripts\complete_configurable_processor_fixed.py ^
    --config config\kpi_config.yaml ^
    --mode baseline ^
    --input data\consolidated_data.csv ^
    --output output\quick_results.json

echo.
echo Quick processing completed!
echo Results saved to: output\quick_results.json
pause
goto MAIN_MENU

:ADVANCED
cls
echo.
echo ================================================================================
echo                            ADVANCED OPTIONS
echo ================================================================================
echo.
echo 1. Run with custom cache directory
echo 2. Run without configuration validation
echo 3. Run with custom output file
echo 4. View cache contents
echo 5. Clear cache
echo 6. Back to main menu
echo.
set /p adv_choice="Enter choice (1-6): "

if "%adv_choice%"=="1" goto CUSTOM_CACHE
if "%adv_choice%"=="2" goto NO_VALIDATION
if "%adv_choice%"=="3" goto CUSTOM_OUTPUT
if "%adv_choice%"=="4" goto VIEW_CACHE
if "%adv_choice%"=="5" goto CLEAR_CACHE
if "%adv_choice%"=="6" goto MAIN_MENU

echo Invalid choice.
pause
goto ADVANCED

:CUSTOM_CACHE
echo.
set /p cache_dir="Enter custom cache directory name: "
set /p datafile="Enter data file name (from data folder): "
echo.
echo Running with custom cache directory: %cache_dir%
python scripts\complete_configurable_processor_fixed.py ^
    --config config\kpi_config.yaml ^
    --mode baseline ^
    --input data\%datafile% ^
    --cache-dir %cache_dir%
pause
goto ADVANCED

:NO_VALIDATION
echo.
set /p datafile="Enter data file name (from data folder): "
echo.
echo Running without configuration validation...
python scripts\complete_configurable_processor_fixed.py ^
    --config config\kpi_config.yaml ^
    --mode baseline ^
    --input data\%datafile% ^
    --no-validation
pause
goto ADVANCED

:CUSTOM_OUTPUT
echo.
set /p datafile="Enter data file name (from data folder): "
set /p output_file="Enter output file name (with .json extension): "
echo.
echo Running with custom output file: %output_file%
python scripts\complete_configurable_processor_fixed.py ^
    --config config\kpi_config.yaml ^
    --mode baseline ^
    --input data\%datafile% ^
    --output %output_file%
pause
goto ADVANCED

:VIEW_CACHE
echo.
echo Cache directory contents:
echo.
if exist "cache" (
    dir cache /b
) else (
    echo Cache directory does not exist.
)
echo.
pause
goto ADVANCED

:CLEAR_CACHE
echo.
set /p confirm="Are you sure you want to clear the cache? (y/n): "
if /i "%confirm%"=="y" (
    if exist "cache" (
        rd /s /q cache
        echo Cache cleared.
    ) else (
        echo Cache directory does not exist.
    )
) else (
    echo Cache not cleared.
)
pause
goto ADVANCED

:EXIT
echo.
echo Thank you for using the KPI Processing System!
pause
exit /b
