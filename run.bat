@echo off
title Danyar Engine Launcher
cd /d "%~dp0"
python run.py
if errorlevel 1 pause
