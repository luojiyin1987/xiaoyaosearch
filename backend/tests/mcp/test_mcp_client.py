"""
MCP 客户端测试脚本 - 参考 FastMCP 官方文档
"""
import asyncio
import sys
import io
from fastmcp import Client
from fastmcp.client import SSETransport

# 设置 UTF-8 输出（避免 Windows GBK 编码问题）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


async def test_mcp_client():
    """测试 MCP 客户端连接和工具调用"""
    # 连接到 MCP 服务器
    # 显式使用 SSE 传输
    transport = SSETransport("http://127.0.0.1:8000/mcp/")
    client = Client(transport)

    print("=" * 60)
    print("MCP 客户端测试")
    print("=" * 60)
    print(f"\n连接到: http://127.0.0.1:8000/mcp\n")

    try:
        async with client:
            print("连接成功!\n")

            # 1. 获取工具列表
            print("-" * 60)
            print("1. 获取工具列表")
            print("-" * 60)
            tools = await client.list_tools()
            print(f"\n找到 {len(tools)} 个工具:\n")
            for tool in tools:
                print(f"  [{tool.name}]")
                print(f"  描述: {tool.description[:80]}...")
                print()

            # 2. 测试语义搜索
            print("-" * 60)
            print("2. 测试语义搜索 (semantic_search)")
            print("-" * 60)
            result = await client.call_tool(
                "semantic_search",
                {
                    "query": "测试",
                    "limit": 3,
                    "threshold": 0.5
                }
            )
            # CallToolResult 有 content 属性
            content = result.content[0].text if result.content else "无结果"
            print(f"\n搜索结果:\n{content[:500]}...\n")

            # 3. 测试全文搜索
            print("-" * 60)
            print("3. 测试全文搜索 (fulltext_search)")
            print("-" * 60)
            result = await client.call_tool(
                "fulltext_search",
                {
                    "query": "python",
                    "limit": 3,
                    "file_types": None  # 明确传递 None
                }
            )
            content = result.content[0].text if result.content else "无结果"
            print(f"\n搜索结果:\n{content[:500]}...\n")

            # 4. 测试混合搜索
            print("-" * 60)
            print("4. 测试混合搜索 (hybrid_search)")
            print("-" * 60)
            result = await client.call_tool(
                "hybrid_search",
                {
                    "query": "代码",
                    "limit": 3,
                    "threshold": 0.5
                }
            )
            content = result.content[0].text if result.content else "无结果"
            print(f"\n搜索结果:\n{content[:500]}...\n")

            print("=" * 60)
            print("所有测试完成!")
            print("=" * 60)

    except Exception as e:
        print(f"\n错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mcp_client())
