@echo off

REM Start main.exe
start "" "main.exe"
echo Waiting for process to close...

:loop
tasklist | find /i "main.exe" >nul
if errorlevel 1 (
    timeout /t 1 >nul
    exit
) else (
    timeout /t 1 >nul
    goto loop
)

