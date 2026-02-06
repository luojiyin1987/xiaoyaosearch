@echo off
REM ============================================
REM 小遥搜索 - 启动脚本
REM ============================================

echo ========================================
echo   XiaoyaoSearch - Application Launcher
echo ========================================
echo.

REM 获取脚本目录和项目根目录
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "RUNTIME_DIR=%PROJECT_ROOT%\runtime"

REM ============================================
REM 1. 配置环境变量
REM ============================================
echo Configure environment variables...

set "PATH=%RUNTIME_DIR%\python\python-embed;%PATH%"
set "PYTHONPATH=%RUNTIME_DIR%\python\python-embed\Lib\site-packages"
set "PATH=%RUNTIME_DIR%\nodejs;%PATH%"
set "PATH=%RUNTIME_DIR%\ffmpeg\bin;%PATH%"

echo   [OK] Environment variables configured
echo.

REM ============================================
REM 2. 启动后端
REM ============================================
echo [1/2] Start backend service...

cd "%PROJECT_ROOT%\backend"
start "XiaoyaoSearch-Backend" /min cmd /c "%RUNTIME_DIR%\python\python-embed\python.exe main.py"

echo   [OK] Backend service started
echo.

REM ============================================
REM 3. 等待后端启动完成
REM ============================================
echo Waiting for backend to be ready...

set /a MAX_WAIT=30
set /a WAIT_COUNT=0

:wait_loop
timeout /t 1 /nobreak >nul
set /a WAIT_COUNT+=1

REM 检测方式1：HTTP健康检查
curl -s http://127.0.0.1:8000/ >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Backend service is ready
    goto :backend_ready
)

REM 检测方式2：端口检查
netstat -ano | find ":8000" | find "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Backend port is listening
    goto :backend_ready
)

REM 超时判断
if %WAIT_COUNT% geq %MAX_WAIT% (
    echo   [!] Timeout waiting for backend (30s), but continue to start frontend
    echo     If backend failed to start, please check backend\ directory
    goto :backend_ready
)

REM 检测进程是否还在运行
tasklist | find "python.exe" >nul 2>&1
if %errorlevel% neq 0 (
    echo   [X] Backend process has stopped, startup failed
    echo     Please check backend\main.py exists
    echo     Or manually start backend to see error messages
    pause
    exit /b 1
)

REM 继续等待
goto :wait_loop

:backend_ready
echo.

REM ============================================
REM 4. 启动前端
REM ============================================
echo [2/2] Start frontend service...

cd "%PROJECT_ROOT%\frontend"
start "XiaoyaoSearch-Frontend" cmd /k "npm run dev"

echo   [OK] Frontend service started
echo.

REM ============================================
REM 5. 等待前端启动并打开浏览器
REM ============================================
echo Waiting for frontend to start...
timeout /t 3 /nobreak >nul

echo Opening browser...
start http://127.0.0.1:5173

echo.
echo ========================================
echo   Application Started!
echo ========================================
echo.
echo Frontend: http://127.0.0.1:5173
echo Backend:  http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo.
echo To stop:
echo   Close "XiaoyaoSearch-Backend" and "XiaoyaoSearch-Frontend" windows
echo.
pause
exit /b 0
