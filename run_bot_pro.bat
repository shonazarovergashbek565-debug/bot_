@echo off
set "LOG_FILE=bot_logs.txt"
set "VENV_DIR=.venv"
set "PYTHON_SCRIPT=main.py"

:: Log faylini yaratamiz
echo %date% %time% - Bot skripti ishga tushmoqda >> %LOG_FILE%

:: Virtual environment yo'q bo'lsa, yaratamiz
if not exist "%VENV_DIR%" (
    echo %date% %time% - Virtual environment topilmadi. Yaratilmoqda... >> %LOG_FILE%
    python -m venv %VENV_DIR%
    if errorlevel 1 (
        echo %date% %time% - Virtual environment yaratishda xatolik yuz berdi! >> %LOG_FILE%
        echo Virtual environment yaratishda xatolik yuz berdi! Konsolni yopmaymang...
        pause
        exit /b 1
    )
    echo %date% %time% - Virtual environment muvaffaqiyatli yaratildi. >> %LOG_FILE%
    
    :: Kerakli paketlarni o'rnatamiz
    call %VENV_DIR%\Scripts\activate.bat
    pip install python-telegram-bot python-dotenv
    if errorlevel 1 (
        echo %date% %time% - Paketlar o'rnatishda xatolik yuz berdi! >> %LOG_FILE%
        echo Paketlar o'rnatishda xatolik yuz berdi! Konsolni yopmaymang...
        pause
        exit /b 1
    )
    echo %date% %time% - Barcha paketlar muvaffaqiyatli o'rnatildi. >> %LOG_FILE%
)

:: Botni doimiy ravishda ishga tushirish sikli
:LOOP
echo %date% %time% - Bot ishga tushmoqda... >> %LOG_FILE%
echo %date% %time% - Bot ishga tushmoqda...

:: Virtual environmentni ishga tushiramiz
call %VENV_DIR%\Scripts\activate.bat
if errorlevel 1 (
    echo %date% %time% - Virtual environment aktivlashda xatolik yuz berdi! >> %LOG_FILE%
    echo Virtual environment aktivlashda xatolik yuz berdi! 5 soniyadan keyin qayta urunib ko'ramiz...
    timeout /t 5 >nul
    goto LOOP
)

:: Botni ishga tushiramiz
python %PYTHON_SCRIPT% >> %LOG_FILE% 2>&1
if errorlevel 1 (
    echo %date% %time% - Bot to'xtab qoldi. Xato kodi: %ERRORLEVEL% >> %LOG_FILE%
    echo Bot to'xtab qoldi! 10 soniyadan keyin qayta ishga tushiriladi...
    timeout /t 10 >nul
    goto LOOP
) else (
    echo %date% %time% - Bot muvaffaqiyatli tugadi. Qayta ishga tushirilmoqda... >> %LOG_FILE%
    goto LOOP
)
