import asyncio
import os
import sys
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client.auth import BearerTokenAuth
from generate_token import generate_and_save_token

async def test_token_auth():
    """测试令牌认证功能"""
    print("=== 测试令牌认证功能 ===")
    
    # 检查是否已经有令牌
    token = None
    if os.path.exists("token.txt"):
        with open("token.txt", "r") as f:
            token = f.read().strip()
    
    # 如果没有令牌，生成一个新的
    if not token:
        print("未找到令牌，正在生成新的令牌...")
        _, token = generate_and_save_token()
    
    # 确保服务器正在运行
    print("\n确保视频解析MCP服务器正在运行...")
    print("如果服务器未运行，请先运行: python mcp_server.py")
    
    # 使用令牌创建客户端
    print("\n使用令牌创建客户端并测试连接...")
    auth = BearerTokenAuth(token)
    transport = StreamableHttpTransport(url="http://localhost:8000/mcp", auth=auth)
    client = Client(transport)
    
    try:
        async with client:
            # 测试ping
            print("测试连接...")
            await client.ping()
            print("✅ 连接成功!")
            
            # 获取可用工具列表
            tools = await client.list_tools()
            print(f"✅ 可用工具: {', '.join([tool.name for tool in tools])}")
            
            # 获取支持的平台列表
            print("\n获取支持的视频平台列表...")
            platforms = await client.read_resource("video-platforms://list")
            print(f"✅ 支持的平台数量: {platforms[0].data['count']}")
            
            # 解析示例视频链接
            print("\n解析抖音视频链接...")
            try:
                result = await client.call_tool("share_url_parse_tool", {"url": "https://v.douyin.com/i8mxvKV/"})
                print("✅ 解析成功!")
                print(f"视频标题: {result.get('data', {}).get('title', '未知')}")
                print(f"作者: {result.get('data', {}).get('author', '未知')}")
            except Exception as e:
                print(f"❌ 解析失败: {str(e)}")
    
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        print("请确保服务器正在运行，并且配置了正确的认证方式")
        return False
    
    print("\n✅ 令牌认证测试成功!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_token_auth())
    sys.exit(0 if success else 1) 