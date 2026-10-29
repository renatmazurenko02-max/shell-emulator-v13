@echo off
cd /d "%~dp0.."
py -3 scripts/create_fixtures.py
py -3 -m src.main --vfs generated/minimal.zip --startup examples/vfs.txt
py -3 -m src.main --vfs generated/multiple.zip --startup examples/binary.txt
py -3 -m src.main --vfs generated/deep.zip --startup examples/deep.txt
pause
