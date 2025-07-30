import re
import os
from parser import VideoSource, parse_video_id, parse_video_share_url

from fastmcp import FastMCP
from fastmcp.server.auth import BearerAuthProvider

# 尝试从本地文件加载公钥
public_key = None
if os.path.exists("keys/public_key.pem"):
    with open("keys/public_key.pem", "r") as f:
        public_key = f.read()

auth = BearerAuthProvider(
        public_key=public_key,
        issuer="https://yby6.com",
        audience="parse-video-py"
        
)

# 创建FastMCP实例
mcp = FastMCP("Video Parser MCP")

# # 添加一个路由用于生成测试令牌
# @mcp.http_route("/auth/token", methods=["GET"])
# async def generate_token():
#     """生成测试令牌的HTTP路由"""
#     # 检查是否有本地私钥
#     if not os.path.exists("keys/private_key.pem"):
#         # 如果没有私钥，生成新的密钥对
#         key_pair = RSAKeyPair.generate()
        
#         # 保存密钥对
#         os.makedirs("keys", exist_ok=True)
#         with open("keys/public_key.pem", "w") as f:
#             f.write(key_pair.public_key)
#         with open("keys/private_key.pem", "w") as f:
#             f.write(key_pair.private_key)
#     else:
#         # 如果有私钥，加载私钥
#         with open("keys/private_key.pem", "r") as f:
#             private_key = f.read()
#         with open("keys/public_key.pem", "r") as f:
#             public_key = f.read()
#         key_pair = RSAKeyPair(private_key=private_key, public_key=public_key)
    
#     # 生成令牌
#     token = key_pair.create_token(
#         subject="parse-video-user",
#         issuer="https://yby6.com",
#         audience="parse-video-py",
#         scopes=["video:parse", "platform:list"],
#         expires_in_seconds=3600  # 1小时有效期
#     )
    
#     return {"token": token}


# 添加MCP工具 - 解析视频分享链接
@mcp.tool()
async def share_url_parse_tool(url: str) -> dict:
    """解析视频分享链接，获取视频信息"""
    url_reg = re.compile(r"http[s]?:\/\/[\w.-]+[\w\/-]*[\w.-]*\??[\w=&:\-\+\%]*[/]*")
    video_share_url = url_reg.search(url).group()

    try:
        video_info = await parse_video_share_url(video_share_url)
        return {"code": 200, "msg": "解析成功", "data": video_info.__dict__}
    except Exception as err:
        return {
            "code": 500,
            "msg": str(err),
        }


# 添加MCP工具 - 根据视频ID解析
@mcp.tool()
async def video_id_parse_tool(source: str, video_id: str) -> dict:
    """根据视频来源和ID解析视频信息"""
    try:
        video_source = VideoSource(source)
        video_info = await parse_video_id(video_source, video_id)
        return {"code": 200, "msg": "解析成功", "data": video_info.__dict__}
    except Exception as err:
        return {
            "code": 500,
            "msg": str(err),
        }


# 添加MCP资源 - 获取支持的视频平台列表
@mcp.resource("video-platforms://list")
async def get_supported_platforms() -> dict:
    """获取所有支持的视频平台列表"""
    platforms = {}
    for source in VideoSource:
        platforms[source.value] = {
            "name": source.value,
            "description": source.name,
        }
    
    return {
        "supported_platforms": platforms,
        "count": len(platforms),
        "version": "1.0.0"
    }


# 添加MCP提示模板 - 视频解析使用指南
@mcp.prompt("video_parser_guide")
async def generate_video_parser_guide(platform: str = None) -> str:
    """生成视频解析使用指南"""
    
    # 通用指南
    general_guide = """
# 视频解析工具使用指南

本工具可以解析各种短视频平台的分享链接，提取出无水印的视频地址、封面图和相关信息。

## 基本使用方法

1. 使用 `share_url_parse_tool` 工具解析视频分享链接
   - 参数: `url` - 视频分享链接
   - 返回: 包含视频信息的JSON对象

2. 使用 `video_id_parse_tool` 工具通过视频ID解析
   - 参数: `source` - 视频平台来源
   - 参数: `video_id` - 视频唯一标识符
   - 返回: 包含视频信息的JSON对象

3. 使用 `video-platforms://list` 资源获取支持的平台列表

## 示例

```python
# 解析分享链接
result = await share_url_parse_tool(url="https://v.douyin.com/abc123/")

# 通过ID解析
result = await video_id_parse_tool(source="douyin", video_id="7123456789")
```
"""

    # 如果指定了特定平台，添加该平台的详细信息
    if platform:
        try:
            source = VideoSource(platform)
            platform_guide = f"""
## {source.value} 平台特别说明

- 平台名称: {source.value}
- 平台标识: {source.name}
- 分享链接格式: 根据实际情况提供
- 视频ID格式: 根据实际情况提供
"""
            return general_guide + platform_guide
        except ValueError:
            return general_guide + f"\n\n注意: 未找到名为 '{platform}' 的平台，请使用 video-platforms://list 资源查看支持的平台列表。"
    
    return general_guide


def main():
    """作为Python包入口点的主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="视频解析MCP服务器")
    parser.add_argument("--transport", type=str, default="http", 
                        choices=["stdio", "sse", "http"], 
                        help="传输方式: stdio, sse, http")
    parser.add_argument("--host", type=str, default="0.0.0.0", 
                        help="主机地址")
    parser.add_argument("--port", type=int, default=8000, 
                        help="端口号")
    parser.add_argument("--path", type=str, default=None, 
                        help="自定义路径")
    
    args = parser.parse_args()
    
    print("🚀 启动视频解析MCP服务器...")
    print("📋 可用工具:")
    print("   - share_url_parse_tool - 解析视频分享链接")
    print("   - video_id_parse_tool - 根据视频ID解析")
    print("📋 可用资源:")
    print("   - video-platforms://list - 获取支持的视频平台列表")
    print("📝 可用提示模板:")
    print("   - video_parser_guide - 生成视频解析使用说明")
    
    # 根据命令行参数选择传输方式
    if args.transport == "stdio":
        print("💡 使用 STDIO 传输方式")
        mcp.run(transport="stdio")
    elif args.transport == "sse":
        path = args.path if args.path else "/sse/"
        print(f"💡 使用 SSE 传输方式: http://{args.host}:{args.port}{path}")
        mcp.run(transport="sse", host=args.host, port=args.port, path=path)
    else:  # http
        path = args.path if args.path else "/mcp"
        print(f"💡 使用 Streamable HTTP 传输方式: http://{args.host}:{args.port}{path}")
        mcp.run(transport="http", host=args.host, port=args.port, path=path) 


if __name__ == "__main__":
    main() 