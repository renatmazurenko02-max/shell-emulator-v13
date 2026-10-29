@echo off
cd /d "%~dp0.."
py -3 scripts/create_fixtures.py
py -3 -m src.main --vfs generated/minimal.zip --startup examples/error.txt
py -3 -m src.main --vfs generated/minimal.zip --startup examples/arguments-error.txt
py -3 -m src.main --vfs generated/minimal.zip --startup examples/missing.txt
pause
