import asyncio
import os
from fastmcp import Client
from fastmcp.client.transports import SSETransport, StreamableHttpTransport
from fastmcp.client.auth import BearerTokenAuth

# 测试SSE连接（无认证）
async def test_sse_client_no_auth():
    """测试SSE连接到MCP服务器（无认证）"""
    print("=== 使用SSE连接测试（无认证）===")
    
    # 使用SSE传输
    transport = SSETransport(url="http://localhost:8000/sse/")
    client = Client(transport)
    
    async with client:
        # 测试ping
        print("测试连接...")
        await client.ping()
        print("连接成功!")
        
        # 获取可用工具列表
        tools = await client.list_tools()
        print(f"可用工具: {', '.join([tool.name for tool in tools])}")
        
        # 获取支持的平台列表
        print("\n获取支持的视频平台列表...")
        platforms = await client.read_resource("video-platforms://list")
        print(f"支持的平台数量: {platforms[0].data['count']}")
        
        # 解析示例视频链接
        print("\n解析抖音视频链接...")
        try:
            result = await client.call_tool("share_url_parse_tool", {"url": "https://v.douyin.com/i8mxvKV/"})
            print(f"解析结果: {result}")
        except Exception as e:
            print(f"解析失败: {str(e)}")


# 测试SSE连接（使用Bearer Token认证）
async def test_sse_client_with_auth():
    """测试SSE连接到MCP服务器（使用Bearer Token认证）"""
    print("\n=== 使用SSE连接测试（带认证）===")
    
    # 获取令牌
    token = await get_token()
    if not token:
        return
    
    # 创建认证对象
    auth = BearerTokenAuth(token)
    
    # 使用SSE传输和认证
    transport = SSETransport(url="http://localhost:8000/sse/", auth=auth)
    client = Client(transport)
    
    async with client:
        # 测试ping
        print("测试连接...")
        await client.ping()
        print("连接成功!")
        
        # 获取可用工具列表
        tools = await client.list_tools()
        print(f"可用工具: {', '.join([tool.name for tool in tools])}")
        
        # 获取支持的平台列表
        print("\n获取支持的视频平台列表...")
        platforms = await client.read_resource("video-platforms://list")
        print(f"支持的平台数量: {platforms[0].data['count']}")
        
        # 解析示例视频链接
        print("\n解析抖音视频链接...")
        try:
            result = await client.call_tool("share_url_parse_tool", {"url": "https://v.douyin.com/i8mxvKV/"})
            print(f"解析结果: {result}")
        except Exception as e:
            print(f"解析失败: {str(e)}")


# 测试HTTP连接（使用Bearer Token认证）
async def test_http_client_with_auth():
    """测试Streamable HTTP连接到MCP服务器（使用Bearer Token认证）"""
    print("\n=== 使用Streamable HTTP连接测试（带认证）===")
    
    # 获取令牌
    token = await get_token()
    if not token:
        return
    
    # 创建认证对象
    auth = BearerTokenAuth(token)
    
    # 使用Streamable HTTP传输和认证
    transport = StreamableHttpTransport(url="http://localhost:8000/mcp", auth=auth)
    client = Client(transport)
    
    async with client:
        # 测试ping
        print("测试连接...")
        await client.ping()
        print("连接成功!")
        
        # 获取可用工具列表
        tools = await client.list_tools()
        print(f"可用工具: {', '.join([tool.name for tool in tools])}")
        
        # 获取支持的平台列表
        print("\n获取支持的视频平台列表...")
        platforms = await client.read_resource("video-platforms://list")
        print(f"支持的平台数量: {platforms[0].data['count']}")
        
        # 解析示例视频链接
        print("\n解析抖音视频链接...")
        try:
            result = await client.call_tool("share_url_parse_tool", {"url": "https://v.douyin.com/i8mxvKV/"})
            print(f"解析结果: {result}")
        except Exception as e:
            print(f"解析失败: {str(e)}")


# 获取令牌的统一函数
async def get_token():
    """获取令牌的统一函数"""
    # 首先尝试从环境变量获取
    token = os.environ.get("MCP_TOKEN")
    
    # 如果环境变量中没有，尝试从token.txt文件读取
    if not token and os.path.exists("token.txt"):
        with open("token.txt", "r") as f:
            token = f.read().strip()
    
    # 如果文件中也没有，尝试从服务器获取
    if not token:
        print("未找到令牌，尝试从服务器获取...")
        token = await get_token_from_server()
    
    if not token:
        print("❌ 无法获取令牌，请确保服务器正在运行并支持令牌生成")
        print("可以尝试以下方法之一:")
        print("1. 运行 python generate_token.py 生成令牌")
        print("2. 访问 http://localhost:8000/auth/token 获取令牌")
        print("3. 设置环境变量 MCP_TOKEN 为有效的令牌")
        return None
    
    return token


# 从服务器获取令牌
async def get_token_from_server():
    """从服务器获取令牌"""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/auth/token") as response:
                if response.status == 200:
                    data = await response.json()
                    token = data.get("token")
                    
                    if token:
                        # 保存令牌到文件
                        with open("token.txt", "w") as f:
                            f.write(token)
                        
                        print("✅ 令牌已从服务器获取并保存到token.txt文件")
                        print(f"令牌: {token[:20]}...{token[-20:]}")
                        return token
                    else:
                        print("❌ 获取令牌失败: 响应中没有token字段")
                else:
                    print(f"❌ 获取令牌失败: HTTP状态码 {response.status}")
    except Exception as e:
        print(f"❌ 获取令牌失败: {str(e)}")
    
    return None


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="视频解析MCP客户端示例")
    parser.add_argument("--get-token", action="store_true", help="获取并保存认证令牌")
    parser.add_argument("--no-auth", action="store_true", help="不使用认证")
    parser.add_argument("--sse", action="store_true", help="使用SSE传输")
    parser.add_argument("--http", action="store_true", help="使用Streamable HTTP传输")
    
    args = parser.parse_args()
    
    # 如果没有指定传输方式，默认都测试
    if not (args.sse or args.http):
        args.sse = True
        args.http = True
    
    # 获取令牌
    if args.get_token:
        await get_token_from_server()
        return
    
    # 测试无认证连接
    if args.no_auth and args.sse:
        await test_sse_client_no_auth()
    
    # 测试带认证的连接
    if not args.no_auth:
        if args.sse:
            await test_sse_client_with_auth()
        
        if args.http:
            await test_http_client_with_auth()


if __name__ == "__main__":
    asyncio.run(main()) 