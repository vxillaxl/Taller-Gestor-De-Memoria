@echo off
chcp 65001 >nul
cd /d "%~dp0"
python gestor_memoria.py
if errorlevel 1 pause
