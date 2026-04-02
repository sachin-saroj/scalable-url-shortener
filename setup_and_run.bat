@echo off
setlocal
title LinkForge - Scalable URL Shortener Setup
echo ==================================================
echo   LinkForge - Scalable URL Shortener Setup
echo ==================================================
echo.

:: Check if Docker is installed
docker -v >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not installed or not in PATH.
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

:: Check if Docker daemon is running
docker info >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker daemon is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)
echo [PASS] Docker is installed and running!

:: Handle .env file
IF NOT EXIST ".env" (
    echo [INFO] .env file not found. Setting it up from .env.example...
    copy .env.example .env >nul
    echo [SUCCESS] Created .env file.
) ELSE (
    echo [PASS] .env file already exists.
)

echo.
echo [INFO] Building and starting all containers... 
echo (This may take a few minutes during the first run as it downloads dependencies)
echo.

docker-compose up --build -d

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] DOCKER COMPOSE FAILED. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ==================================================
echo   SUCCESS! APPLICATION IS NOW LIVE
echo ==================================================
echo.
echo   WebApp / Dashboard : http://localhost:5173
echo   API Documentation  : http://localhost:8000/docs
echo   Backend URL        : http://localhost:8000
echo.
echo   Note: The Celery background workers and Postgres 
echo         database are fully configured and running!
echo.
echo   To stop the application, simply run: stop.bat
echo ==================================================
echo.
pause
