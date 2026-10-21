@echo off
chcp 65001 > nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
title MasOrange TV Agent — Instalador

echo.
echo  =========================================
echo   MasOrange TV Agent ^(TIBI^) — Instalador
echo  =========================================
echo.

:: Cambiar al directorio del script
cd /d "%~dp0"

:: Buscar ejecutable de Python válido (incluyendo instalación de uv en AppData)
set "PY_EXE=python"
if exist "%APPDATA%\uv\python\cpython-3.12.15-windows-x86_64-none\python.exe" (
    set "PY_EXE=%APPDATA%\uv\python\cpython-3.12.15-windows-x86_64-none\python.exe"
)

:: Verificar que Python está disponible
"%PY_EXE%" --version > nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python no encontrado en el sistema.
    echo.
    echo  Por favor instala Python 3.10 o superior desde:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANTE: Durante la instalacion marca la casilla
    echo  "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

:: Ejecutar el instalador Python
"%PY_EXE%" instalador.py

:: Si el instalador fallo, pausar para ver el error
if errorlevel 1 (
    echo.
    echo  La instalacion finalizo con errores.
    pause
)
