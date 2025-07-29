import typer
import os
import httpx
import uuid

# 从 server.py 导入 mcp 实例和 config 字典
from .server import mcp, config

# 创建一个 Typer 应用
app = typer.Typer(add_completion=False, rich_markup_mode="markdown")


@app.command()
def main():
    """
    启动 **gewe-notice** MCP 服务器。

    一个通过微信机器人发送AI任务状态通知的轻量级工具。
    所有配置均通过环境变量进行设置。
    """
    print("🚀 正在启动 gewe-notice MCP 服务器...")

    # 从环境变量读取配置
    base_url = os.getenv("GEWE_NOTICE_BASE_URL", "http://api.geweapi.com")
    token = os.getenv("GEWE_NOTICE_TOKEN")
    app_id = os.getenv("GEWE_NOTICE_APP_ID")
    wxid = os.getenv("GEWE_NOTICE_WXID")
    at_list_str = os.getenv("GEWE_NOTICE_AT_LIST", "")

    # -- at_list 处理逻辑 --
    at_list = []  # 默认空列表
    if at_list_str:
        # 优先处理 "all" 的情况
        if at_list_str.strip().lower() == "all":
            at_list = ["all"]
        else:
            # 分割、去空格、过滤空值，确保列表干净
            at_list = [item.strip()
                       for item in at_list_str.split(',') if item.strip()]

    # -- 环境变量格式校验 --
    error_messages = []
    # 1. 校验 Token 格式 (UUID)
    try:
        if token:
            uuid.UUID(token, version=4)
        else:
            raise ValueError()
    except (ValueError, TypeError):
        error_messages.append("❌ `GEWE_NOTICE_TOKEN` 格式无效，它应该是一个有效的 UUID。")

    # 2. 校验 App ID 格式
    if not app_id or not app_id.startswith("wx_"):
        error_messages.append("❌ `GEWE_NOTICE_APP_ID` 格式无效，它应该以 'wx_' 开头。")

    # 3. 校验 WXID 格式
    if not wxid:
        error_messages.append("❌ `GEWE_NOTICE_WXID` 不能为空。")
    elif "@chatroom" in wxid and not wxid.endswith("@chatroom"):
        error_messages.append(
            "❌ `GEWE_NOTICE_WXID` 格式无效，群聊ID似乎格式不正确，它应该以 '@chatroom' 结尾。")

    if error_messages:
        print("\n**配置错误**: 发现以下问题：")
        for msg in error_messages:
            print(f"   - {msg}")
        print("💡 请检查您的 MCP 配置文件中的环境变量。")
        raise typer.Exit(code=1)
    # -- 校验结束 --

    # 验证必要的参数是否已提供
    if not all([token, app_id, wxid]):
        print("\n❌ **错误**: 缺少必要的环境变量: `GEWE_NOTICE_TOKEN`, `GEWE_NOTICE_APP_ID`, `GEWE_NOTICE_WXID`")
        print("💡 请检查您的 MCP 配置文件。")
        raise typer.Exit(code=1)

    # -- 启动前在线检查 --
    print("🔬 正在检查微信机器人在线状态...")
    check_url = f"{base_url}/gewe/v2/api/login/checkOnline"
    headers = {"X-GEWE-TOKEN": token}
    payload = {"appId": app_id}
    try:
        with httpx.Client() as client:
            response = client.post(
                check_url, headers=headers, json=payload, timeout=10.0)

        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("data") is True:
                print("✅ 机器人在线，准备就绪。")
            else:
                print("\n❌ **错误**: 机器人当前不在线。")
                print(f"   - App ID: {app_id}")
                print("💡 请检查您的微信客户端是否已登录，或Gewe服务是否正常。")
                raise typer.Exit(code=1)
        else:
            print(f"\n❌ **错误**: 在线状态检查失败，HTTP状态码: {response.status_code}")
            print(f"   - 响应内容: {response.text}")
            raise typer.Exit(code=1)

    except httpx.RequestError as e:
        print(f"\n❌ **错误**: 在线状态检查时发生网络错误: {e}")
        print("💡 请检查您的网络连接或 Base URL 配置是否正确。")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"\n❌ **错误**: 在线状态检查时发生未知错误: {e}")
        raise typer.Exit(code=1)
    # -- 在线检查结束 --

    # 将从环境变量接收到的参数存入全局 config 字典
    config["base_url"] = base_url
    config["token"] = token
    config["app_id"] = app_id
    config["wxid"] = wxid
    config["at_list"] = at_list

    print("🔧 配置加载成功 (来自环境变量):")
    print(f"   - Base URL: {config['base_url']}")
    print(f"   - App ID:   {config['app_id']}")
    print(f"   - WXID:     {config['wxid']}")
    if config["at_list"]:
        print(f"   - At List:  {config['at_list']}")  # 直接打印列表
    print("-" * 20)

    # 运行 MCP 服务器
    mcp.run()


if __name__ == "__main__":
    app()
