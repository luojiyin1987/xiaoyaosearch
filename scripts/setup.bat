@echo off
setlocal enabledelayedexpansion

REM ============================================
REM 小遥搜索 - 环境准备脚本
REM ============================================

echo ========================================
echo   XiaoyaoSearch - Environment Setup
echo ========================================
echo.

REM 获取脚本目录和项目根目录
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "RUNTIME_DIR=%PROJECT_ROOT%\runtime"

REM ============================================
REM 0. 解压 Python 嵌入式版本（关键！）
REM ============================================
echo [0/7] Setup Python embed runtime...

set "PYTHON_EMBED_DIR=%RUNTIME_DIR%\python\python-embed"
set "PYTHON_ZIP=%RUNTIME_DIR%\python\python-3.10.11-embed-amd64.zip"

REM 检查是否需要解压
if not exist "%PYTHON_EMBED_DIR%\python.exe" (
    echo   Extracting Python embed runtime...
    echo     This may take a minute...

    REM 使用 PowerShell 解压（避免外部依赖）
    powershell -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_EMBED_DIR%' -Force"

    if %errorlevel% neq 0 (
        echo   [X] Failed to extract Python embed runtime
        pause
        exit /b 1
    )

    echo   [OK] Python embed extracted
) else (
    echo   [OK] Python embed already exists
)

REM 修改 python310._pth 以支持 site-packages（允许 pip）
set "PTH_FILE=%PYTHON_EMBED_DIR%\python310._pth"
if exist "%PTH_FILE%" (
    echo   Configuring Python for pip support...
    (
        echo python310.zip
        echo .
        echo Lib/site-packages
        echo #import site
    ) > "%PTH_FILE%"
    echo   [OK] Python configured for pip
)

echo.

REM ============================================
REM 1. 检查运行时目录
REM ============================================
echo [1/7] Check runtime directories...

if not exist "%RUNTIME_DIR%\python\python-embed\python.exe" (
    echo   [X] Python embed runtime not found
    echo     Please ensure runtime\python\python-3.10.11-embed-amd64.zip exists
    pause
    exit /b 1
)

if not exist "%RUNTIME_DIR%\nodejs\node.exe" (
    echo   [X] Node.js runtime not found
    echo     Please ensure runtime\nodejs\ exists
    pause
    exit /b 1
)

if not exist "%RUNTIME_DIR%\ffmpeg\bin\ffmpeg.exe" (
    echo   [X] FFmpeg runtime not found
    echo     Please ensure runtime\ffmpeg\ exists
    pause
    exit /b 1
)

echo   [OK] Runtime directories complete
echo.

REM ============================================
REM 2. 配置环境变量
REM ============================================
echo [2/7] Configure environment variables...

set "PATH=%RUNTIME_DIR%\python\python-embed;%PATH%"
set "PYTHONPATH=%RUNTIME_DIR%\python\python-embed\Lib\site-packages"
set "PATH=%RUNTIME_DIR%\nodejs;%PATH%"
set "PATH=%RUNTIME_DIR%\ffmpeg\bin;%PATH%"

echo   [OK] Environment variables configured
echo.

REM ============================================
REM 3. 安装后端依赖
REM ============================================
echo [3/7] Install backend dependencies...
echo     Installing Python packages...
echo     Using Tsinghua mirror for faster download...
echo.

cd "%PROJECT_ROOT%\backend"

REM 检查是否已安装 pip
set "PIP_PY=%PROJECT_ROOT%\runtime\python\python-embed\get-pip.py"
set "PYTHON_EXE=%RUNTIME_DIR%\python\python-embed\python.exe"

if not exist "%PYTHON_EXE%" (
    echo   [X] Python embed not found at %PYTHON_EXE%
    pause
    exit /b 1
)

REM 检查是否需要安装 pip
if not exist "%RUNTIME_DIR%\python\python-embed\Scripts\pip.exe" (
    echo     Installing pip...
    echo       Downloading get-pip.py...

    REM 下载 get-pip.py
    powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PIP_PY%'"

    if %errorlevel% neq 0 (
        echo   [X] Failed to download get-pip.py
        pause
        exit /b 1
    )

    echo       Installing pip to embed Python...
    "%PYTHON_EXE%" "%PIP_PY%" --target="%RUNTIME_DIR%\python\python-embed\Lib\site-packages" --no-warn-script-location

    if %errorlevel% neq 0 (
        echo   [X] Failed to install pip
        pause
        exit /b 1
    )

    REM 创建 pip.bat 启动器
    (
        echo @echo off
        echo "%PYTHON_EXE%" -m pip %%*
    ) > "%RUNTIME_DIR%\python\python-embed\Scripts\pip.bat"

    echo     [OK] pip installed
) else (
    echo     [OK] pip already installed
)

REM 使用 pip 安装依赖
"%PYTHON_EXE%" -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

if %errorlevel% neq 0 (
    echo   [X] Backend dependencies installation failed
    echo.
    echo     Error details:
    echo     - Make sure Python 3.10.11 embed is extracted in runtime\python\python-embed\
    echo     - Check network connection to pypi.tuna.tsinghua.edu.cn
    echo.
    echo     Please try manually:
    echo     1. cd runtime\python\python-embed
    echo     2. python.exe -m pip install ..\..\..\backend\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    pause
    exit /b 1
)

echo   [OK] Backend dependencies installed
echo.

REM ============================================
REM 3.5 安装 faster-whisper 和 CUDA 支持
REM ============================================
echo [3.5/7] Install faster-whisper and GPU support...
echo     Installing faster-whisper for speech recognition...
echo.

"%PYTHON_EXE%" -m pip install faster-whisper -i https://pypi.tuna.tsinghua.edu.cn/simple

if %errorlevel% neq 0 (
    echo   [!] Warning: faster-whisper installation failed, speech recognition may not work
    echo     You can install it manually later:
    echo     python.exe -m pip install faster-whisper -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo.
) else (
    echo   [OK] faster-whisper installed
)
echo.

REM 询问是否启用 CUDA
echo ========================================
echo   CUDA GPU Acceleration Setup
echo ========================================
echo.
echo Do you want to enable CUDA for GPU acceleration?
echo.
echo Requirements:
echo   - NVIDIA GPU with RTX 3060 or higher (6GB+ VRAM recommended)
echo   - CUDA Toolkit 12.1 installed
echo   - Driver version: 527.41 or higher
echo.
echo Note: If you don't have NVIDIA GPU or CUDA installed, select NO
echo.
set /p CUDA_CHOICE="Enable CUDA? (Y/N): "

if /i "%CUDA_CHOICE%"=="Y" (
    echo.
    echo   Installing CUDA-enabled PyTorch...
    echo     This will replace CPU version with GPU version
    echo     Source: https://download.pytorch.org/whl/cu121
    echo.

    REM 卸载 CPU 版本
    echo     Uninstalling CPU version...
    "%PYTHON_EXE%" -m pip uninstall -y torch torchaudio torchvision >nul 2>&1

    REM 安装 CUDA 版本
    echo     Installing CUDA version (PyTorch 2.1.0 + CUDA 12.1)...
    "%PYTHON_EXE%" -m pip install torch==2.1.0+cu121 torchaudio==2.1.0+cu121 torchvision==0.16.0+cu121 --index-url https://download.pytorch.org/whl/cu121

    if %errorlevel% equ 0 (
        echo   [OK] CUDA-enabled PyTorch installed
        echo.
        echo   To verify CUDA installation:
        echo     python.exe -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
        echo.
    ) else (
        echo   [!] CUDA installation failed, CPU version will be used
        echo     You may need to install CUDA Toolkit from: https://developer.nvidia.com/cuda-downloads
        echo     Reinstalling CPU version...
        "%PYTHON_EXE%" -m pip install torch torchaudio torchvision -i https://pypi.tuna.tsinghua.edu.cn/simple
    )
) else (
    echo   [OK] CPU version will be used (no GPU acceleration)
)
echo.

REM ============================================
REM 4. 安装前端依赖
REM ============================================
echo [4/7] Install frontend dependencies...
echo     Installing Node packages...
echo     Using taobao mirror for faster download...

cd "%PROJECT_ROOT%\frontend"

REM 使用完整路径运行npm
"%RUNTIME_DIR%\nodejs\node.exe" "%RUNTIME_DIR%\nodejs\node_modules\npm\bin\npm-cli.js" install --registry=https://registry.npmmirror.com

if %errorlevel% neq 0 (
    echo   [X] Frontend dependencies installation failed
    echo.
    echo     Error details:
    echo     - Make sure Node.js 21.x is installed in runtime\nodejs\
    echo     - Check network connection to registry.npmmirror.com
    echo.
    echo     Please try manually:
    echo     1. cd runtime\nodejs
    echo     2. node.exe ..\..\frontend\node_modules\npm\bin\npm-cli.js install ..\..\frontend
    pause
    exit /b 1
)

cd "%PROJECT_ROOT%"

echo   [OK] Frontend dependencies installed
echo.

REM ============================================
REM 5. 生成配置文件
REM ============================================
echo [5/7] Generate config files...

if not exist "%PROJECT_ROOT%\backend\.env" (
    if exist "%PROJECT_ROOT%\backend\.env.example" (
        copy "%PROJECT_ROOT%\backend\.env.example" "%PROJECT_ROOT%\backend\.env" >nul
        echo   [OK] Generated backend\.env
    ) else (
        echo   [!] Warning: backend\.env.example not found, skipping config generation
    )
) else (
    echo   [-] backend\.env already exists, skipping
)

echo.

REM ============================================
REM 6. 创建数据目录
REM ============================================
echo [6/7] Create data directories...

if not exist "%PROJECT_ROOT%\data\database" mkdir "%PROJECT_ROOT%\data\database"
if not exist "%PROJECT_ROOT%\data\indexes" mkdir "%PROJECT_ROOT%\data\indexes"
if not exist "%PROJECT_ROOT%\data\indexes\faiss" mkdir "%PROJECT_ROOT%\data\indexes\faiss"
if not exist "%PROJECT_ROOT%\data\indexes\whoosh" mkdir "%PROJECT_ROOT%\data\indexes\whoosh"
if not exist "%PROJECT_ROOT%\data\logs" mkdir "%PROJECT_ROOT%\data\logs"
if not exist "%PROJECT_ROOT%\data\models" mkdir "%PROJECT_ROOT%\data\models"
if not exist "%PROJECT_ROOT%\data\uploads" mkdir "%PROJECT_ROOT%\data\uploads"

echo   [OK] Data directories created
echo.

REM ============================================
REM 7. 检查和引导
REM ============================================
echo [7/7] Check optional components...
echo ========================================
echo.

REM 检查 Ollama
where ollama >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Ollama is installed
    for /f "tokens=*" %%v in ('ollama --version 2^>^&1') do echo     Version: %%v
) else (
    echo [!] Ollama not installed ^(optional component^)
    echo.
    echo     Ollama is optional, used for LLM features
    echo.
    echo     Installation methods:
    echo       1. Use package in runtime\ollama\
    echo       2. Download from: https://ollama.com/download
    echo.
    echo     After installation, run:
    echo       ollama serve
    echo       ollama pull qwen2.5:1.5b
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
    echo [OK] AI models are downloaded
) else (
    echo [!] AI models not downloaded or incomplete
    echo.
    echo     Baidu Drive link ^(contains all default models^):
    echo       Link: https://pan.baidu.com/s/1jRcTztvjf8aiExUh6oayVg
    echo       Code: ycr5
    echo.
    echo     Model directory structure:
    echo       data\models\
    echo       ├── embedding\BAAI\bge-m3\
    echo       ├── cn-clip\
    echo       └── faster-whisper\
)

echo.
echo ========================================
echo   Environment Setup Complete!
echo ========================================
echo.
echo Notes:
echo   - Your system environment variables were NOT modified
echo   - All settings are temporary and only used during script execution
echo   - The py.ini file was backed up to prevent conflicts
echo.
echo Next step: Run startup.bat to launch the application
echo.
pause
exit /b 0
