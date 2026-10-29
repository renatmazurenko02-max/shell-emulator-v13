@echo off
cd /d "%~dp0.."
py -3 scripts/create_fixtures.py
py -3 -m src.main --vfs generated/broken.zip --startup examples/vfs.txt
py -3 -m src.main --vfs generated/unsafe.zip --startup examples/vfs.txt
py -3 -m src.main --vfs generated/missing.zip --startup examples/vfs.txt
pause
