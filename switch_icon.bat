@echo off
cd /d "%~dp0"
echo =======================================
echo     PRODIGIT DESKTOP ICON SWITCHER
echo =======================================
echo 1. Emerald Chrono (Default Modern Dark Glass)
echo 2. Swiss Monochrome (Pure Black and White)
echo 3. Cyber Cyan Pulse (Electric Cyan and Neon Violet)
echo =======================================
set /p choice="Select an icon concept (1-3): "
python switch_icon.py %choice%
pause
