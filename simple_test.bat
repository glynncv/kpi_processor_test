@echo off
echo Testing simple menu flow...
echo.

:MENU
echo 1. Test Python Script
echo 2. Exit
set /p choice="Enter choice: "

if "%choice%"=="1" goto TEST_PYTHON
if "%choice%"=="2" goto EXIT
goto MENU

:TEST_PYTHON
echo Running Python test...
python --version
echo Python finished with exit code: %ERRORLEVEL%
pause
goto MENU

:EXIT
echo Goodbye!
pause
