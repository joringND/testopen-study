@echo off
setlocal

set PYTHON=C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe
set ENV=%1
if "%ENV%"=="" set ENV=test

set FILES=tests
if not "%ENV%"=="test" set FILES=tests\day37_homework.py

for /f %%i in ('powershell -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TS=%%i
set REPORT=report_%ENV%_%TS%.html

if not exist logs mkdir logs
if not exist artifacts mkdir artifacts

echo === Running tests, env: %ENV% ===
%PYTHON% -m pytest %FILES% --env %ENV% -v --tb=short --html=%REPORT% --self-contained-html

echo === Report: %REPORT% ===
start "" %REPORT%
pause