@echo off
cd /d "%~dp0"
py -3 -m src.main
if errorlevel 1 pause
