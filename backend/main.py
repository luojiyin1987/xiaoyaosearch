"""
小遥搜索后端服务主入口
启动FastAPI应用并配置所有必要的组件
"""
import os
import sys
from pathlib import Path

# 将 backend 目录添加到 Python 模块搜索路径
# 这样无论从哪里运行 main.py，都能正确找到 app 模块
backend_dir = Path(__file__).parent.absolute()
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 首先配置AI模型相关的日志设置（必须在导入AI相关库之前）
from app.core.logging_config import setup_ai_logging
setup_ai_logging()

# 导入核心模块
from app.core import init_database, setup_exception_handlers
from app.core.logging_config import setup_logging, get_logger, logger

# 配置日志系统
setup_logging()
from app.api import (
    search_router,
    index_router,
    config_router,
    system_router,
    settings_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    启动时初始化数据库和其他组件，关闭时清理资源
    """
    # 启动时执行
    logger.info("=" * 50)
    logger.info("小遥搜索服务启动中...")
    logger.info("=" * 50)

    try:
        # 初始化数据库
        logger.info("初始化数据库...")
        init_database()
        logger.info("数据库初始化完成")

            # 初始化AI模型服务
        logger.info("加载AI模型...")
        try:
            from app.services.ai_model_manager import ai_model_service
            await ai_model_service.initialize()
            ai_model_service._initialized = True  # 设置初始化标志
            logger.info("AI模型服务加载完成")
        except Exception as e:
            logger.warning(f"AI模型服务初始化失败: {str(e)}")
            logger.info("继续运行，但AI功能可能不可用")
            # 确保即使初始化失败也设置标志，避免重复尝试
            try:
                ai_model_service._initialized = False
            except:
                pass

        # 初始化索引缓存
        logger.info("初始化索引缓存...")
        try:
            from app.services.file_index_service import get_file_index_service
            index_service = get_file_index_service()
            await index_service.load_indexed_files_cache()
            logger.info("索引缓存初始化完成")
        except Exception as e:
            logger.warning(f"索引缓存初始化失败: {str(e)}")
            logger.info("继续运行，但首次增量更新可能较慢")

        logger.info("✅ 小遥搜索服务启动完成")
        logger.info(f"📖 API文档: http://127.0.0.1:8000/docs")
        logger.info(f"📋 ReDoc文档: http://127.0.0.1:8000/redoc")

    except Exception as e:
        logger.error(f"❌ 服务启动失败: {str(e)}")
        raise

    yield

    # 关闭时执行
    logger.info("小遥搜索服务关闭中...")
    try:
        # TODO: 清理资源
        # await cleanup_resources()
        logger.info("资源清理完成")
    except Exception as e:
        logger.error(f"资源清理失败: {str(e)}")

    logger.info("小遥搜索服务已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="小遥搜索 API",
    description="多模态AI智能搜索桌面应用后端服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS中间件，支持Electron跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://[::1]:3000",
        "http://[::1]:5173"
    ],  # Electron渲染进程地址（包括IPv6）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置异常处理器
setup_exception_handlers(app)

# 注册API路由
app.include_router(search_router)
app.include_router(index_router)
app.include_router(config_router)
app.include_router(system_router)
app.include_router(settings_router)

# 根路径
@app.get("/")
async def root():
    """
    根路径，返回API基本信息
    """
    return {
        "name": "小遥搜索 API",
        "version": "1.0.0",
        "description": "多模态AI智能搜索桌面应用后端服务",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health_check": "/api/system/health"
    }

# 启动服务
if __name__ == "__main__":
    import uvicorn

    # 从环境变量获取配置
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info")

    logger.info(f"🚀 启动服务: http://{host}:{port}")
    logger.info(f"🔄 热重载: {'开启' if reload else '关闭'}")
    logger.info(f"📊 日志级别: {log_level}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )