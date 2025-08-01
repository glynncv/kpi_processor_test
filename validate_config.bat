@echo off
REM Validate Configuration with menu options
setlocal enabledelayedexpansion

:VALIDATE_MENU
cls
echo.
echo ================================================================================
echo                        CONFIGURATION VALIDATOR
echo ================================================================================
echo.
echo 1. Quick validation (config only)
echo 2. Full validation (config + data compatibility)
echo 3. Strict validation (config only)
echo 4. Strict validation (config + data)
echo 5. Generate validation report
echo.
echo 0. Exit
echo.
set /p choice="Enter your choice (0-5): "

if "%choice%"=="1" goto QUICK_VALIDATE
if "%choice%"=="2" goto FULL_VALIDATE
if "%choice%"=="3" goto STRICT_VALIDATE
if "%choice%"=="4" goto STRICT_FULL_VALIDATE
if "%choice%"=="5" goto GENERATE_REPORT
if "%choice%"=="0" goto EXIT

echo Invalid choice. Please try again.
pause
goto VALIDATE_MENU

:QUICK_VALIDATE
cls
echo.
echo Running quick configuration validation...
echo.
python scripts\config_validator_fixed.py --config config\kpi_config.yaml
pause
goto VALIDATE_MENU

:FULL_VALIDATE
cls
echo.
echo Available data files:
dir /b data\*.csv 2>nul
echo.
set /p datafile="Enter data file name (from data folder): "
if not exist "data\%datafile%" (
    echo Error: File data\%datafile% not found!
    pause
    goto VALIDATE_MENU
)

echo.
echo Running full validation with data compatibility check...
echo.
python scripts\config_validator_fixed.py --config config\kpi_config.yaml --data data\%datafile%
pause
goto VALIDATE_MENU

:STRICT_VALIDATE
cls
echo.
echo Running strict configuration validation...
echo.
python scripts\config_validator_fixed.py --config config\kpi_config.yaml --strict
pause
goto VALIDATE_MENU

:STRICT_FULL_VALIDATE
cls
echo.
echo Available data files:
dir /b data\*.csv 2>nul
echo.
set /p datafile="Enter data file name (from data folder): "
if not exist "data\%datafile%" (
    echo Error: File data\%datafile% not found!
    pause
    goto VALIDATE_MENU
)

echo.
echo Running strict validation with data compatibility check...
echo.
python scripts\config_validator_fixed.py --config config\kpi_config.yaml --data data\%datafile% --strict
pause
goto VALIDATE_MENU

:GENERATE_REPORT
cls
echo.
echo Available data files:
dir /b data\*.csv 2>nul
echo.
set /p datafile="Enter data file name (from data folder, or press Enter to skip): "

if not exist "output" mkdir output

if "%datafile%"=="" (
    echo.
    echo Generating validation report (config only)...
    python scripts\config_validator_fixed.py --config config\kpi_config.yaml --report output\validation_report.txt
) else (
    if not exist "data\%datafile%" (
        echo Error: File data\%datafile% not found!
        pause
        goto VALIDATE_MENU
    )
    echo.
    echo Generating validation report (config + data)...
    python scripts\config_validator_fixed.py --config config\kpi_config.yaml --data data\%datafile% --report output\validation_report.txt
)

echo.
echo Validation report generated: output\validation_report.txt
pause
goto VALIDATE_MENU

:EXIT
exit /b
