@echo off
title Stop LinkForge
echo ==================================================
echo   Stopping LinkForge - Scalable URL Shortener
echo ==================================================
echo.

docker-compose down

echo.
echo ==================================================
echo   [SUCCESS] All containers stopped safely.
echo ==================================================
pause
