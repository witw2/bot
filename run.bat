@echo off


:: Aktywuj venv (zakładam, że folder to 'venv')
call .venv\Scripts\activate.bat

:: Uruchom bota
python Sveneusz.py

:: Zatrzymaj zamknięcie konsoli
pause
