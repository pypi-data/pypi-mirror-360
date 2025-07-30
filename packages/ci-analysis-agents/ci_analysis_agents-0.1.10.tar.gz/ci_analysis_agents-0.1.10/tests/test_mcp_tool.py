import pytest
from dotenv import load_dotenv
from agents.mcp import MCPServerSse

@pytest.mark.asyncio
async def test_mcp_tool_call():
    """测试直接调用MCP工具，验证参数类型"""
    load_dotenv()
    
    # 连接MCP服务器
    mcp_server = MCPServerSse(
        name="Test MCP Server",
        params={
            "url": "http://localhost:8003/sse",
        },
    )
    await mcp_server.connect()
    print("MCP服务器连接成功")
    
    # 直接调用MCP工具，传递字符串类型的参数
    try:
        result = await mcp_server.call_tool(
            "report_appium_error_log_fetch",
            {"beats_test_id": "80016651"}  # 确保是字符串类型
        )
        print(f"MCP工具调用成功: {result}")
    except Exception as e:
        print(f"MCP工具调用失败: {e}")
    
    await mcp_server.disconnect() 