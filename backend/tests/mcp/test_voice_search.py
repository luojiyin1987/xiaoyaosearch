"""
测试 MCP 语音搜索工具
"""
import asyncio
import base64
import sys
import io
from fastmcp import Client
from fastmcp.client import SSETransport

# 设置 UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


async def test_voice_search():
    """测试语音搜索工具"""
    # 读取测试音频并转换为 base64
    audio_path = r"d:\MyWorkProjects\freelance\indiehacker\xiaoyaosearch\docs\测试文档\测试数据\test.mp3"

    with open(audio_path, "rb") as f:
        audio_data = base64.b64encode(f.read()).decode('utf-8')

    print(f"音频已读取，大小: {len(audio_data)} 字符 (base64 编码)\n")

    # 连接到 MCP 服务器
    transport = SSETransport("http://127.0.0.1:8000/mcp/")
    client = Client(transport)

    try:
        async with client:
            print("=" * 60)
            print("测试语音搜索工具 (voice_search)")
            print("=" * 60)

            result = await client.call_tool(
                "voice_search",
                {
                    "audio_data": audio_data,
                    "search_type": "semantic",
                    "limit": 5,
                    "threshold": 0.5
                }
            )

            content = result.content[0].text if result.content else "无结果"
            print(f"\n搜索结果:\n{content}\n")

            print("=" * 60)
            print("语音搜索测试完成!")
            print("=" * 60)

    except Exception as e:
        print(f"\n错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_voice_search())
