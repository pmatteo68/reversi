@echo off
setlocal

cd /d "%~dp0"
CALL bin\env
CALL %VENV_NAME%\Scripts\activate

python src\main.py %*
