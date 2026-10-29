@echo off
cd /d "%~dp0.."
py -3 -m src.main --vfs fixtures/demo-vfs.zip --startup examples/error.txt
py -3 -m src.main --vfs fixtures/demo-vfs.zip --startup examples/arguments-error.txt
py -3 -m src.main --vfs fixtures/demo-vfs.zip --startup examples/missing.txt
pause
