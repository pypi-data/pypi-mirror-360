import typer
from typing_extensions import Annotated
from typing import List

# 从 server.py 导入 mcp 实例和 config 字典
from .server import mcp, config

# 创建一个 Typer 应用
app = typer.Typer(add_completion=False, rich_markup_mode="markdown")

@app.command()
def main(
    base_url: Annotated[str, typer.Option(help="Gewe API 的基础 URL。")] = "http://api.geweapi.com",
    token: Annotated[str, typer.Option(help="Gewe API 的认证 Token。", rich_help_panel="必要参数")] = "",
    app_id: Annotated[str, typer.Option(help="微信机器人的 App ID。", rich_help_panel="必要参数")] = "",
    wxid: Annotated[str, typer.Option(help="接收通知的微信用户或群组 ID (例如: 'wxid_xxxx' 或 'xxxx@chatroom')。", rich_help_panel="必要参数")] = "",
    at_list: Annotated[List[str], typer.Option(
        "--at-list", "-a",
        help="要@的群成员wxid列表, 可多次使用。或填 'all' @全体成员。仅对群聊有效。",
        rich_help_panel="@人功能"
    )] = None,
):
    """
    启动 **gewe-notice** MCP 服务器。

    一个通过微信机器人发送AI任务状态通知的轻量级工具。
    """
    print("🚀 正在启动 gewe-notice MCP 服务器...")

    # 验证必要的参数是否已提供
    if not all([token, app_id, wxid]):
        print("\n❌ **错误**: 缺少必要的参数: `--token`, `--app-id`, `--wxid`")
        print("💡 请使用 `--help` 查看所有可用选项。")
        raise typer.Exit(code=1)

    # 将从命令行接收到的参数存入全局 config 字典
    config["base_url"] = base_url
    config["token"] = token
    config["app_id"] = app_id
    config["wxid"] = wxid
    # 新增 at_list
    config["at_list"] = at_list if at_list else []

    print("🔧 配置加载成功:")
    print(f"   - Base URL: {config['base_url']}")
    print(f"   - App ID:   {config['app_id']}")
    print(f"   - WXID:     {config['wxid']}")
    if config["at_list"]:
        print(f"   - At List:  {', '.join(config['at_list'])}")
    print("-" * 20)

    # 运行 MCP 服务器
    mcp.run()

if __name__ == "__main__":
    app()