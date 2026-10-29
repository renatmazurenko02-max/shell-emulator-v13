@echo off
cd /d "%~dp0.."
py -3 scripts/create_fixtures.py
py -3 -m src.main --help
py -3 -m src.main --unknown
py -3 -m src.main --vfs
py -3 -m src.main
py -3 -m src.main --vfs generated/deep.zip
py -3 -m src.main --startup examples/success.txt
py -3 -m src.main --vfs generated/deep.zip --startup examples/exit.txt
pause
