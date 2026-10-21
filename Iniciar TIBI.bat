@echo off
chcp 65001 > nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo.
echo  =========================================
echo   MasOrange TV Agent ^(TIBI^) arrancando...
echo  =========================================
echo.
echo  Interfaz web: http://localhost:8000
echo  Pulsa Ctrl+C para detener.
echo.
.venv\Scripts\python.exe main.py server
pause
