@echo off
REM 快速测试脚本 - 在完整打包前验证依赖配置
REM 用法: quick_test.bat [cpu|gpu]
REM
REM 测试流程:
REM   1. 检查缺失依赖
REM   2. 清理构建目录
REM   3. 快速打包 (最小配置)
REM   4. 运行测试并快速验证启动
REM
REM 预期时间: 5-10分钟 (完整打包需要30-60分钟)

setlocal enabledelayedexpansion

REM 设置参数
set VERSION=%1
if "%VERSION%"=="" set VERSION=cpu

REM 颜色输出辅助函数
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (
  set "DEL=%%a"
)

REM 打印标题
echo.
echo ============================================================
echo   快速测试脚本 - %VERSION% 版本
echo ============================================================
echo.
echo 此脚本用于在完整打包前快速验证依赖配置
echo 预期耗时: 5-10 分钟 (完整打包需要 30-60 分钟)
echo.
echo ============================================================
echo.

REM 步骤 1: 检查依赖
echo [1/4] 检查常见缺失依赖...
echo.
python check_missing.py
if errorlevel 1 (
    echo.
    echo [错误] 发现缺失依赖，请先安装后再继续
    pause
    exit /b 1
)
echo.
echo [完成] 依赖检查通过
echo.
echo ============================================================
echo.

REM 步骤 2: 清理构建目录
echo [2/4] 清理旧的构建目录...
echo.
if exist build (
    rmdir /s /q build
    echo   - 已删除 build/
)
if exist dist (
    rmdir /s /q dist
    echo   - 已删除 dist/
)
echo.
echo [完成] 清理完成
echo.
echo ============================================================
echo.

REM 步骤 3: 快速打包
echo [3/4] 开始快速打包...
echo.
echo 使用配置文件: xiaoyao_backend_%VERSION%.spec
echo.
echo 注意: 这是快速测试打包，可能仍需要 5-10 分钟
echo       完整打包需要 30-60 分钟
echo.
pyinstaller --clean xiaoyao_backend_%VERSION%.spec

if errorlevel 1 (
    echo.
    echo ============================================================
    echo [错误] 打包失败，请检查错误信息
    echo ============================================================
    pause
    exit /b 1
)

echo.
echo [完成] 打包成功
echo.
echo ============================================================
echo.

REM 步骤 4: 运行测试
echo [4/4] 运行快速测试...
echo.
echo 测试可执行文件: dist\xiaoyao-backend-%VERSION%.exe
echo.
echo 注意: 此测试仅验证可执行文件能否正常启动
echo       完整功能测试需要配合 AI 模型文件
echo.
echo 测试步骤:
echo   1. 可执行文件将尝试启动
echo   2. 观察是否有模块导入错误
echo   3. 如果看到 FastAPI 启动信息，说明基本成功
echo   4. 按 Ctrl+C 停止测试
echo.
echo ============================================================
echo.
pause

REM 启动可执行文件
start "" dist\xiaoyao-backend-%VERSION%.exe

REM 等待用户观察
echo.
echo 可执行文件已在新窗口启动
echo 请观察输出是否有错误
echo.
echo 如果看到类似以下信息说明成功:
echo   INFO:     Started server process
echo   INFO:     Uvicorn running on http://127.0.0.1:8000
echo.
echo 如果看到 "ModuleNotFoundError" 说明仍有缺失依赖
echo.
pause

echo.
echo ============================================================
echo   快速测试完成
echo ============================================================
echo.
echo 如果测试成功，可以进行完整打包:
echo   pyinstaller --clean xiaoyao_backend_%VERSION%.spec
echo.
echo 如果发现错误，请根据错误信息调整 spec 文件后重试
echo.
echo ============================================================
echo.
pause
