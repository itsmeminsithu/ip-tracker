@echo off
rem Copyright (c) 2026 Min SiThu (devminsithu). SPDX-License-Identifier: MIT
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto usepython
py -3 launch.py
goto done
:usepython
where python >nul 2>nul
if errorlevel 1 goto missing
python launch.py
:done
if errorlevel 1 pause
exit /b
:missing
echo Install Python 3.11 or newer from https://www.python.org/downloads/
echo Enable Add Python to PATH during installation.
pause
exit /b 1
