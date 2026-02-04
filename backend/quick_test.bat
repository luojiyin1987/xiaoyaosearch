@echo off
REM Quick Test Script - Verify dependency configuration before full packaging
REM Usage: quick_test.bat [cpu|gpu]
REM
REM Test Process:
REM   1. Check for missing dependencies
REM   2. Clean build directories
REM   3. Quick package build
REM   4. Run test and verify startup
REM
REM Expected time: 5-10 minutes (full package takes 30-60 minutes)

setlocal enabledelayedexpansion

REM Set parameters
set VERSION=%1
if "%VERSION%"=="" set VERSION=cpu

REM Print title
echo.
echo ============================================================
echo   Quick Test Script - %VERSION% Version
echo ============================================================
echo.
echo This script verifies dependency configuration before full packaging
echo Estimated time: 5-10 minutes (full package takes 30-60 minutes)
echo.
echo ============================================================
echo.

REM Step 1: Check dependencies
echo [1/4] Checking for missing dependencies...
echo.
python check_missing.py
if errorlevel 1 (
    echo.
    echo [ERROR] Missing dependencies found, please install them first
    pause
    exit /b 1
)
echo.
echo [OK] Dependency check passed
echo.
echo ============================================================
echo.

REM Step 2: Clean build directories
echo [2/4] Cleaning old build directories...
echo.
if exist build (
    rmdir /s /q build
    echo   - Deleted build/
)
if exist dist (
    rmdir /s /q dist
    echo   - Deleted dist/
)
echo.
echo [OK] Cleanup complete
echo.
echo ============================================================
echo.

REM Step 3: Quick package
echo [3/4] Starting quick package...
echo.
echo Using config file: xiaoyao_backend_%VERSION%.spec
echo.
echo NOTE: This is a quick test package, may take 5-10 minutes
echo       Full package takes 30-60 minutes
echo.
pyinstaller --clean xiaoyao_backend_%VERSION%.spec

if errorlevel 1 (
    echo.
    echo ============================================================
    echo [ERROR] Package failed, please check error messages
    echo ============================================================
    pause
    exit /b 1
)

echo.
echo [OK] Package successful
echo.
echo ============================================================
echo.

REM Step 4: Run test
echo [4/4] Running quick test...
echo.
echo Testing executable: dist\xiaoyao-backend-%VERSION%.exe
echo.
echo NOTE: This test only verifies if the executable can start
echo       Full function testing requires AI model files
echo.
echo Test steps:
echo   1. Executable will try to start
echo   2. Observe for module import errors
echo   3. If you see FastAPI startup info, it's basically successful
echo   4. Press Ctrl+C to stop the test
echo.
echo ============================================================
echo.
pause

REM Start executable
start "" dist\xiaoyao-backend-%VERSION%.exe

REM Wait for user to observe
echo.
echo Executable started in new window
echo Please observe output for errors
echo.
echo If you see something like this, it's successful:
echo   INFO:     Started server process
echo   INFO:     Uvicorn running on http://127.0.0.1:8000
echo.
echo If you see "ModuleNotFoundError", there are still missing dependencies
echo.
pause

echo.
echo ============================================================
echo   Quick Test Complete
echo ============================================================
echo.
echo If test passed, you can proceed with full package:
echo   pyinstaller --clean xiaoyao_backend_%VERSION%.spec
echo.
echo If errors found, please adjust spec file based on error messages and retry
echo.
echo ============================================================
echo.
pause
