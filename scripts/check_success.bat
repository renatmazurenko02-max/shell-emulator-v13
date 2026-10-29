@echo off
cd /d "%~dp0.."
py -3 -m src.main --vfs "fixtures/demo-vfs.zip" --startup examples/success.txt
py -3 -m src.main --vfs "fixtures/vfs with spaces.zip" --startup examples/success.txt
pause
