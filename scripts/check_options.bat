@echo off
cd /d "%~dp0.."
py -3 -m src.main --help
py -3 -m src.main --unknown
py -3 -m src.main --vfs
py -3 -m src.main
py -3 -m src.main --vfs fixtures/custom.zip
py -3 -m src.main --startup examples/success.txt
py -3 -m src.main --vfs fixtures/custom.zip --startup examples/exit.txt
pause
