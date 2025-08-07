@echo off
REM Test Menu for KPI Processing System
echo  KPI System Test Menu
echo ========================

:menu
echo.
echo Test Options:
echo 1. Run System Tests
echo 2. Test Baseline Processing
echo 3. Test Targeted Processing
echo 4. View Results
echo 0. Exit

set /p choice="Choice (0-4): "

if "%choice%"=="0" goto :exit
if "%choice%"=="1" if exist "test_system.py" python test_system.py
if "%choice%"=="2" if exist "kpi_processor.py" python kpi_processor.py --mode baseline
if "%choice%"=="3" if exist "kpi_processor.py" python kpi_processor.py --mode targeted --kpi SM001
if "%choice%"=="4" if exist "show_results.py" python show_results.py

pause
goto :menu

:exit
echo Goodbye!
pause
