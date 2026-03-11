@echo off
chcp 65001 >nul 2>&1
REM ============================================
REM 小遥搜索 - 启动脚本
REM ============================================

echo ========================================
echo   小遥搜索 - 应用启动器
echo ========================================
echo.

REM 获取脚本目录和项目根目录
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "PROJECT_ROOT=%SCRIPT_DIR%\.."
set "RUNTIME_DIR=%PROJECT_ROOT%\runtime"

REM 转换为绝对路径
pushd "%PROJECT_ROOT%"
set "PROJECT_ROOT=%CD%"
popd

set "RUNTIME_DIR=%PROJECT_ROOT%\runtime"
set "BACKEND_DIR=%PROJECT_ROOT%\backend"
set "FRONTEND_DIR=%PROJECT_ROOT%\frontend"

REM ============================================
REM 1. 配置环境变量
REM ============================================
echo 配置环境变量...

set "PATH=%RUNTIME_DIR%\python\python-embed;%PATH%"
set "PYTHONPATH=%RUNTIME_DIR%\python\python-embed\Lib\site-packages"
set "PATH=%RUNTIME_DIR%\nodejs;%PATH%"
set "PATH=%RUNTIME_DIR%\ffmpeg\bin;%PATH%"

echo   [OK] 环境变量已配置
echo.

REM ============================================
REM 2. 启动后端
REM ============================================
echo [1/2] 启动后端服务...

REM 从 backend 目录启动后端，与本地开发方式一致
REM config.py 会使用绝对路径查找 backend/.env 配置文件
start "小遥搜索-后端" /d "%BACKEND_DIR%" cmd /k ""%RUNTIME_DIR%\python\python-embed\python.exe" main.py && pause"

echo   [OK] 后端服务已启动
echo.

REM ============================================
REM 3. 等待后端启动完成
REM ============================================
echo 等待后端服务就绪...

set /a MAX_WAIT=30
set /a WAIT_COUNT=0

:wait_loop
timeout /t 1 /nobreak >nul
set /a WAIT_COUNT+=1

REM 检测方式1：HTTP健康检查
curl -s http://127.0.0.1:8000/ >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] 后端服务已就绪
    goto :backend_ready
)

REM 检测方式2：端口检查
netstat -ano | find ":8000" | find "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] 后端端口已监听
    goto :backend_ready
)

REM 超时判断
if %WAIT_COUNT% geq %MAX_WAIT% (
    echo   [!] 等待后端超时 (30秒), 但继续启动前端
    echo     如果后端启动失败, 请检查 backend\ 目录
    goto :backend_ready
)

REM 检测进程是否还在运行
tasklist | find "python.exe" >nul 2>&1
if %errorlevel% neq 0 (
    echo   [X] 后端进程已停止, 启动失败
    echo     请检查 backend\main.py 是否存在
    echo     或手动启动后端查看错误信息
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
echo [2/2] 启动前端服务...

start "小遥搜索-前端" /d "%FRONTEND_DIR%" cmd /k "npm run dev"

echo   [OK] 前端服务已启动
echo.

REM ============================================
REM 5. 等待前端启动并打开浏览器
REM ============================================
echo 等待前端启动...
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   应用已启动!
echo ========================================
echo.
echo 停止方法:
echo   关闭 "小遥搜索-后端" 和 "小遥搜索-前端" 窗口
echo.
pause
exit /b 0
