@echo off
REM ============================================
REM testopen-study one-click: full tests + HTML report
REM Usage: double-click or type run_tests.bat
REM Prereq: mock_server.py running on port 8000
REM ============================================
set PYTHON=C:/Users/lenovo/AppData/Local/Programs/Python/Python39/python.exe

for /f %%i in ('powershell -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TS=%%i

echo [1/2] Running all tests...
%PYTHON% -m pytest day25_homework.py day27_homework.py day28_homework.py day30_homework.py -v --tb=short --html=report_%TS%.html --self-contained-html

echo [2/2] Done. Report: report_%TS%.html
start report_%TS%.html
pause