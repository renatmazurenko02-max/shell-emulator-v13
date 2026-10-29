@echo off
cd /d "%~dp0.."
py -3 scripts/create_fixtures.py
py -3 -m src.main --vfs "generated/minimal.zip" --startup examples/success.txt
py -3 -m src.main --vfs "generated/vfs with spaces.zip" --startup examples/success.txt
pause
