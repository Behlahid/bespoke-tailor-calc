@echo off
echo Starting Bombay Master Tailors - Bespoke Measurement & Yardage Studio...
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python main.py
pause
