"""
MCP 服务器配置管理
"""
from pydantic import BaseModel, Field
from typing import Optional


class MCPConfig(BaseModel):
    """MCP 服务器配置"""

    # 服务器配置
    server_name: str = Field(default="xiaoyao-search", description="服务器名称")
    server_version: str = Field(default="1.0.0", description="服务器版本")

    # SSE 配置
    sse_enabled: bool = Field(default=True, description="是否启用 SSE 传输")
    sse_path: str = Field(default="/mcp/sse", description="SSE 端点路径")

    # 搜索配置
    default_limit: int = Field(default=20, ge=1, le=100, description="默认结果数量")
    default_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="默认相似度阈值")

    # 语音搜索配置
    voice_enabled: bool = Field(default=True, description="是否启用语音搜索")
    voice_max_duration: int = Field(default=30, ge=1, le=60, description="最大音频时长（秒）")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")

    class Config:
        env_prefix = "MCP_"


# 全局配置实例
_mcp_config: Optional[MCPConfig] = None


def get_mcp_config() -> MCPConfig:
    """获取 MCP 配置"""
    global _mcp_config
    if _mcp_config is None:
        _mcp_config = MCPConfig()
    return _mcp_config


def set_mcp_config(config: MCPConfig):
    """设置 MCP 配置"""
    global _mcp_config
    _mcp_config = config
