@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM ============================================
REM 小遥搜索 - 环境准备脚本
REM ============================================

echo ========================================
echo   小遥搜索 - 环境准备
echo ========================================
echo.

REM 获取脚本目录和项目根目录
set "SCRIPT_DIR=%~dp0"
REM 转换为绝对路径(解决双击运行时路径解析问题)
pushd "%SCRIPT_DIR%.."
set "PROJECT_ROOT=%CD%"
popd
set "RUNTIME_DIR=%PROJECT_ROOT%\runtime"

REM ============================================
REM 0. 解压 Python 嵌入式版本(关键！)
REM ============================================
echo [0/7] 设置 Python 嵌入式运行时...

set "PYTHON_EMBED_DIR=%RUNTIME_DIR%\python\python-embed"
set "PYTHON_ZIP=%RUNTIME_DIR%\python\python-3.10.11-embed-amd64.zip"

REM 检查是否需要解压
if not exist "%PYTHON_EMBED_DIR%\python.exe" (
    echo   正在解压 Python 嵌入式运行时...
    echo     这可能需要一分钟...

    REM 使用 PowerShell 解压(避免外部依赖)
    powershell -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_EMBED_DIR%' -Force"

    if %errorlevel% neq 0 (
        echo   [X] Python 嵌入式运行时解压失败
        pause
        exit /b 1
    )

    echo   [OK] Python 嵌入式运行时已解压
) else (
    echo   [OK] Python 嵌入式运行时已存在
)

REM 修改 python310._pth 以支持 site-packages(允许 pip)
set "PTH_FILE=%PYTHON_EMBED_DIR%\python310._pth"
if exist "%PTH_FILE%" (
    echo   正在配置 Python 以支持 pip...
    (
        echo python310.zip
        echo .
        echo Lib/site-packages
        echo #import site
    ) > "%PTH_FILE%"
    echo   [OK] Python 已配置支持 pip
)

echo.

REM ============================================
REM 1. 检查运行时目录
REM ============================================
echo [1/7] 检查运行时目录...

if not exist "%RUNTIME_DIR%\python\python-embed\python.exe" (
    echo   [X] 未找到 Python 嵌入式运行时
    echo     请确保 runtime\python\python-3.10.11-embed-amd64.zip 存在
    pause
    exit /b 1
)

if not exist "%RUNTIME_DIR%\nodejs\node.exe" (
    echo   [X] 未找到 Node.js 运行时
    echo     请确保 runtime\nodejs\ 存在
    pause
    exit /b 1
)

if not exist "%RUNTIME_DIR%\ffmpeg\bin\ffmpeg.exe" (
    echo   [X] 未找到 FFmpeg 运行时
    echo     请确保 runtime\ffmpeg\ 存在
    pause
    exit /b 1
)

echo   [OK] 运行时目录检查完成
echo.

REM ============================================
REM 2. 配置环境变量
REM ============================================
echo [2/7] 配置环境变量...

set "PATH=%RUNTIME_DIR%\python\python-embed;%PATH%"
set "PYTHONPATH=%RUNTIME_DIR%\python\python-embed\Lib\site-packages"
set "PATH=%RUNTIME_DIR%\nodejs;%PATH%"
set "PATH=%RUNTIME_DIR%\ffmpeg\bin;%PATH%"

echo   [OK] 环境变量已配置
echo.

REM ============================================
REM 3. 安装后端依赖
REM ============================================
echo [3/7] 安装后端依赖...
echo     正在安装 Python 包...
echo     使用清华大学镜像源加速下载...
echo.

REM 设置后端目录路径(不使用 cd, 避免路径问题)
set "BACKEND_DIR=%PROJECT_ROOT%\backend"
set "BACKEND_REQUIREMENTS=%BACKEND_DIR%\requirements.txt"

REM 检查后端目录和 requirements.txt 是否存在
if not exist "%BACKEND_DIR%" (
    echo   [X] 后端目录不存在:"%BACKEND_DIR%"
    pause
    exit /b 1
)

if not exist "%BACKEND_REQUIREMENTS%" (
    echo   [X] requirements.txt 不存在:"%BACKEND_REQUIREMENTS%"
    pause
    exit /b 1
)

REM 检查是否已安装 pip
set "PIP_PY=%PROJECT_ROOT%\runtime\python\python-embed\get-pip.py"
set "PYTHON_EXE=%RUNTIME_DIR%\python\python-embed\python.exe"

if not exist "%PYTHON_EXE%" (
    echo   [X] 未在 %PYTHON_EXE% 找到 Python 嵌入版
    pause
    exit /b 1
)

REM 检查是否需要安装 pip
if not exist "%RUNTIME_DIR%\python\python-embed\Scripts\pip.exe" (
    echo     正在安装 pip...
    echo       正在下载 get-pip.py...

    REM 下载 get-pip.py
    powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PIP_PY%'"

    if %errorlevel% neq 0 (
        echo   [X] 下载 get-pip.py 失败
        pause
        exit /b 1
    )

    echo       正在安装 pip 到嵌入式 Python...
    "%PYTHON_EXE%" "%PIP_PY%" --target="%RUNTIME_DIR%\python\python-embed\Lib\site-packages" --no-warn-script-location

    if %errorlevel% neq 0 (
        echo   [X] 安装 pip 失败
        pause
        exit /b 1
    )

    REM 创建 pip.bat 启动器
    (
        echo @echo off
        echo "%PYTHON_EXE%" -m pip %%*
    ) > "%RUNTIME_DIR%\python\python-embed\Scripts\pip.bat"

    echo     [OK] pip 已安装
) else (
    echo     [OK] pip 已安装
)

REM 使用 pip 安装依赖(使用阿里云镜像源)
"%PYTHON_EXE%" -m pip install -r "%BACKEND_REQUIREMENTS%" -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

if %errorlevel% neq 0 (
    echo   [X] 后端依赖安装失败
    echo.
    echo     错误详情:
    echo     -- 确保已将 Python 3.10.11 嵌入版解压到 runtime\python\python-embed\
    echo     -- 检查网络连接到 mirrors.aliyun.com
    echo.
    echo     请尝试手动安装:
    echo     1. cd runtime\python\python-embed
    echo     2. python.exe -m pip install ..\..\..\backend\requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
    pause
    exit /b 1
)

echo   [OK] 后端依赖已安装
echo.

REM ============================================
REM 3.5 安装 faster-whisper 和 CUDA 支持
REM ============================================
echo [3.5/7] 安装 faster-whisper 和 GPU 支持...
echo     正在安装 faster-whisper 语音识别...
echo.

"%PYTHON_EXE%" -m pip install faster-whisper -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

if %errorlevel% neq 0 (
    echo   [!] 警告:faster-whisper 安装失败, 语音识别可能无法工作
    echo     您可以稍后手动安装:
    echo     python.exe -m pip install faster-whisper -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
    echo.
) else (
    echo   [OK] faster-whisper 已安装
)
echo.

REM 询问是否启用 CUDA
echo ========================================
echo   CUDA GPU 加速设置
echo ========================================
echo.
echo 是否要启用 CUDA 以使用 GPU 加速?
echo.
echo 要求:
echo   - NVIDIA GPU, RTX 3060 或更高版本(推荐 6GB+ 显存)
echo   - 已安装 CUDA Toolkit 12.1
echo   - 驱动版本:527.41 或更高
echo.
echo 注意:如果您没有 NVIDIA GPU 或未安装 CUDA, 请选择 NO
echo.
set /p CUDA_CHOICE=是否启用 CUDA?Y/N:
echo.

if /i "!CUDA_CHOICE!"=="Y" goto cuda_install
goto cuda_skip

:cuda_install
echo   正在安装支持 CUDA 的 PyTorch...
echo     这将用 GPU 版本替换 CPU 版本
echo     来源:https://download.pytorch.org/whl/cu121
echo.

REM 卸载 CPU 版本
echo     正在卸载 CPU 版本...
"%PYTHON_EXE%" -m pip uninstall -y torch torchaudio torchvision >nul 2>&1

REM 安装 CUDA 版本
echo     正在安装 CUDA 版本(PyTorch 2.10.0 + CUDA 12.8)...
"%PYTHON_EXE%" -m pip install torch==2.10.0+cu128 torchaudio==2.10.0+cu128 torchvision==0.25.0+cu128 --index-url https://download.pytorch.org/whl/cu128

if !errorlevel! equ 0 (
    echo   [OK] 支持 CUDA 的 PyTorch 已安装
    echo.
    echo   验证 CUDA 安装:
    echo     python.exe -c "import torch; print('CUDA available:', torch.cuda.is_available())"
    echo.
) else (
    echo   [!] CUDA 安装失败, 将使用 CPU 版本
    echo     您可能需要从以下地址安装 CUDA Toolkit:https://developer.nvidia.com/cuda-downloads
    echo     正在重新安装 CPU 版本...
    "%PYTHON_EXE%" -m pip install torch torchaudio torchvision -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
)
goto cuda_done

:cuda_skip
echo   [OK] 将使用 CPU 版本(无 GPU 加速)

:cuda_done
echo.

REM ============================================
REM 4. 安装前端依赖
REM ============================================
echo [4/7] 安装前端依赖...
echo     正在安装 Node 包...
echo     使用淘宝镜像源加速下载...

REM 设置前端目录路径(不使用 cd, 避免路径问题)
set "FRONTEND_DIR=%PROJECT_ROOT%\frontend"

REM 检查前端目录是否存在
if not exist "%FRONTEND_DIR%" (
    echo   [X] 前端目录不存在:"%FRONTEND_DIR%"
    pause
    exit /b 1
)

REM 使用完整路径运行npm(指定工作目录)
"%RUNTIME_DIR%\nodejs\node.exe" "%RUNTIME_DIR%\nodejs\node_modules\npm\bin\npm-cli.js" install --prefix "%FRONTEND_DIR%" --registry=https://registry.npmmirror.com

if %errorlevel% neq 0 (
    echo   [X] 前端依赖安装失败
    echo.
    echo     错误详情:
    echo     - 确保已在 runtime\nodejs\ 安装 Node.js 21.x
    echo     - 检查网络连接到 registry.npmmirror.com
    echo.
    echo     请尝试手动安装:
    echo     1. cd runtime\nodejs
    echo     2. node.exe ..\..\frontend\node_modules\npm\bin\npm-cli.js install ..\..\frontend
    pause
    exit /b 1
)

echo   [OK] 前端依赖已安装
echo.

REM ============================================
REM 5. 生成配置文件
REM ============================================
echo [5/7] 生成配置文件...

if not exist "%PROJECT_ROOT%\backend\.env" (
    if exist "%PROJECT_ROOT%\backend\.env.example" (
        copy "%PROJECT_ROOT%\backend\.env.example" "%PROJECT_ROOT%\backend\.env" >nul
        echo   [OK] 已生成 backend\.env
    ) else (
        echo   [!] 警告:未找到 backend\.env.example, 跳过配置生成
    )
) else (
    echo   [-] backend\.env 已存在, 跳过
)

echo.

REM ============================================
REM 6. 创建数据目录
REM ============================================
echo [6/7] 创建数据目录...

if not exist "%PROJECT_ROOT%\data\database" mkdir "%PROJECT_ROOT%\data\database"
if not exist "%PROJECT_ROOT%\data\indexes" mkdir "%PROJECT_ROOT%\data\indexes"
if not exist "%PROJECT_ROOT%\data\indexes\faiss" mkdir "%PROJECT_ROOT%\data\indexes\faiss"
if not exist "%PROJECT_ROOT%\data\indexes\whoosh" mkdir "%PROJECT_ROOT%\data\indexes\whoosh"
if not exist "%PROJECT_ROOT%\data\logs" mkdir "%PROJECT_ROOT%\data\logs"
if not exist "%PROJECT_ROOT%\data\models" mkdir "%PROJECT_ROOT%\data\models"
if not exist "%PROJECT_ROOT%\data\uploads" mkdir "%PROJECT_ROOT%\data\uploads"

echo   [OK] 数据目录已创建
echo.

REM ============================================
REM 7. 检查和引导
REM ============================================
echo [7/7] 检查必需组件...
echo ========================================
echo.

REM 检查 Ollama (必选项)
echo 正在检查 Ollama 安装...
where ollama >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Ollama 已安装
    for /f "tokens=*" %%v in ('ollama --version 2^>^&1') do (
        set "OLLAMA_VERSION=%%v"
    )
    echo     版本: !OLLAMA_VERSION!
) else (
    echo   [X] 未安装 Ollama
    echo.
    echo     Ollama 是 AI 聊天功能的必需组件
    echo.
    echo     安装方式:
    echo       1. 使用本地安装包:双击 runtime\ollama\OllamaSetup.exe
    echo       2. 或从官网下载:https://ollama.com/download
    echo.
    echo     安装完成后, 请运行以下命令:
    echo       - 打开新终端并运行:ollama serve
    echo       - 然后拉取模型:ollama pull qwen2.5:1.5b
    echo.
    echo     安装完成后, 请重新运行 setup.bat
    pause
    exit /b 1
)

echo.

REM 检查 AI 模型
set "MODELS_OK=1"

if not exist "%PROJECT_ROOT%\data\models\embedding\BAAI\bge-m3" (
    set "MODELS_OK=0"
)
if not exist "%PROJECT_ROOT%\data\models\cn-clip" (
    set "MODELS_OK=0"
)
if not exist "%PROJECT_ROOT%\data\models\faster-whisper" (
    set "MODELS_OK=0"
)

if %MODELS_OK%==1 (
    echo [OK] AI 模型已下载
) else (
    echo [!] AI 模型未下载或不完整
    echo.
    echo     百度网盘链接 【包含所有默认模型】:
    echo       链接:https://pan.baidu.com/s/1jRcTztvjf8aiExUh6oayVg
    echo       提取码:ycr5
    echo.
    echo     模型目录结构:
    echo       data\models\
    echo       ├── embedding\BAAI\bge-m3\
    echo       ├── cn-clip\
    echo       └── faster-whisper\
)

echo.

REM ============================================
REM 8. 激活 pywin32 (Windows MCP 支持)
REM ============================================
echo [8/8] 激活 pywin32 (MCP 支持)...
echo.

REM Step 1: 重新安装 pywin32
echo [1/4] 重新安装 pywin32...
"%PYTHON_EXE%" -m pip install --force-reinstall pywin32 -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

if %errorlevel% neq 0 (
    echo   [!] pywin32 安装失败
    echo     MCP 功能可能无法使用
) else (
    echo   [OK] pywin32 已安装
)
echo.

REM Step 2: 运行 postinstall 脚本
echo [2/4] 运行 pywin32 后安装脚本...
"%PYTHON_EXE%" "%RUNTIME_DIR%\python\python-embed\Scripts\pywin32_postinstall.py" -install

if %errorlevel% neq 0 (
    echo   [!] 后安装脚本执行失败
    echo     将尝试使用备用方案...
) else (
    echo   [OK] 后安装脚本执行成功
)
echo.

REM Step 3: 复制 python310._pth 配置文件
echo [3/4] 复制 Python 路径配置文件...
set "PTH_SOURCE=%PROJECT_ROOT%\scripts\win32\python310._pth"
set "PTH_TARGET=%RUNTIME_DIR%\python\python-embed\python310._pth"

if exist "%PTH_SOURCE%" (
    copy /Y "%PTH_SOURCE%" "%PTH_TARGET%" >nul
    echo   [OK] python310._pth 已复制
) else (
    echo   [!] 未找到 %PTH_SOURCE%
)
echo.

REM Step 4: 验证 pywintypes 模块
echo [4/4] 验证 pywintypes 模块...
"%PYTHON_EXE%" -c "import pywintypes; print('成功!')" 2>nul

if %errorlevel% equ 0 (
    echo   [OK] pywin32 激活成功
) else (
    echo   [!] pywin32 激活失败
    echo     MCP 功能可能无法使用
)

echo.

echo ========================================
echo   环境准备完成！
echo ========================================
echo.
echo 注意:
echo   - 系统环境变量未被修改
echo   - 所有设置均为临时, 仅在脚本执行期间有效
echo.
echo 下一步:运行 startup.bat 启动应用程序
echo.
pause
exit /b 0
