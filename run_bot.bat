@echo off
cd /d "%~dp0"
echo Bot ishga tushmoqda...
if exist ".venv" (
    echo Virtual environment topildi. Ishlatilmoqda...
    call .venv\Scripts\activate.bat
) else (
    echo Virtual environment topilmadi. To'g'ridan-to'g'ri ishga tushmoqda...
)
python main.py
pause