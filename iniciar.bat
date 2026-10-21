@echo off
chcp 65001 > nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
title MasOrange TV Agent — TIBI

cd /d "%~dp0"

echo.
echo  ================================================
echo   MasOrange TV Agent ^(TIBI^) arrancando...
echo  ================================================
echo.

:: Comprobar que se ha instalado antes
if not exist ".venv\Scripts\python.exe" (
    echo  ERROR: El entorno virtual no existe.
    echo  Ejecuta primero "instalar.bat" para configurar el agente.
    echo.
    pause
    exit /b 1
)

echo  Interfaz TV  :  http://127.0.0.1:8000
echo  API chat     :  http://127.0.0.1:8000/api/chat
echo  Salud        :  http://127.0.0.1:8000/health
echo.
echo  Pulsa Ctrl+C para detener el servidor.
echo.
echo  ------------------------------------------------

:: Abrir el navegador tras 4 segundos (en paralelo)
start /b cmd /c "timeout /t 4 /nobreak > nul && start http://127.0.0.1:8000"

.venv\Scripts\python.exe main.py server
