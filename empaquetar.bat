@echo off
chcp 65001 > nul
title Empaquetador TIBI

cd /d "%~dp0"

echo.
echo  ================================================
echo   MasOrange TV Agent ^(TIBI^) -- Empaquetador
echo  ================================================
echo.
echo  Empaquetando...
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0empaquetar.ps1"

if errorlevel 1 (
    echo.
    echo  ERROR: no se pudo crear el ZIP.
    pause
    exit /b 1
)

echo.
echo  ================================================
echo   Listo.
echo  ================================================
echo.
pause
