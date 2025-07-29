# gewe-notice

<p>
  <a href="https://github.com/wangnov/gewe-notice/blob/master/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  </a>
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python version">
  </a>
  <img src="https://img.shields.io/badge/version-0.1.0-orange" alt="Version">
</p>

一个轻量级的 MCP 服务器，用于通过 [Gewe API](https://www.geweapi.com) 提供的微信机器人发送 AI 任务状态通知。

## ✨ 功能特性

- **MCP 服务器**: 提供一个符合 MCP 规范的工具服务器，可轻松集成到任何支持 MCP 的 AI Agent 框架中。
- **文本通知**: 支持向指定的微信用户或群聊发送文本消息。
- **群聊 @ 功能**:
    - **@全体成员**: 在群聊中，可以通过参数轻松实现 `@所有人`。
    - **@特定成员**: 支持根据 `wxid` 列表在群聊中 `@` 一个或多个指定用户。
    - **智能容错**:
        - 自动获取群成员昵称，使 `@` 信息更具可读性。
        - 如果提供的 `wxid` 无效或不在群内，会自动跳过并打印警告。
        - 获取群成员列表失败时，会跳过 `@` 功能，仅发送纯文本，确保消息送达。
- **权限自动降级**: 当 `@所有人` 因权限不足失败时，服务器会自动重试，改为发送不带 `@` 的纯文本消息，最大程度保证通知的成功率。
- **清晰的错误处理**: 对接 Gewe API 的常见错误（如不在群内、用户不存在、无权限等）进行了分类处理，并在服务端打印出清晰的错误信息，便于快速定位问题。
- **灵活的配置**: 所有关键参数均可通过命令行进行配置。

## 效果图

<table>
  <tr>
    <td align="center">个人通知效果</td>
    <td align="center">群@通知效果</td>
  </tr>
  <tr>
    <td><img src="assets/friend_notice.png" width="350"></td>
    <td><img src="assets/group_notice.png" width="350"></td>
  </tr>
</table>

## 🤔 使用场景说明

需要注意的是，`gewe-notice` 的设计初衷是作为**单向的、非交互式**的状态通知工具，它与 `mcp-feedback-enhanced` 等交互式工具的用途有着本质区别。

-   **`gewe-notice` (单向通知)**: 核心价值在于**无人值守**的场景。当您的 AI Agent 在执行一个远程或耗时较长的任务时（例如：服务器上的代码生成、数据分析、自动化测试等），它可以主动将关键节点（如任务成功、失败）的状态通过微信推送给您。它是一种"即发即忘"的通知机制，不中断 Agent 的执行流程，或 Agent 的执行流程已经结束。此时收到强提醒的微信通知后，您可以选择回到IDE中继续规划下一任务或重试错误任务等等。

-   **交互式工具 (双向反馈)**: `mcp-feedback-enhanced` 等工具的本质是**双向交互**，它们会暂停 Agent 的执行流程，并明确地**等待用户的输入**或反馈来决定下一步操作。

简单来说，如果您需要 Agent 在执行过程中**通知**您发生了什么，请使用 `gewe-notice`。如果您需要 Agent **询问** 该怎么做，请使用交互式工具。

建议在User Rules、Project Rules、Agent Rules 等地方固化这些区分概念，以免在存在多种工具调用时候的冲突情况。

## 🚀 快速开始

对于普通用户来说，最推荐的安装和使用方式是在 AI IDE（如 Cursor）中直接配置 MCP。

### 1. (可选) 安装 uv

本工具使用 `uvx` 命令运行，它由 `uv` 提供。如果您的环境中尚未安装 `uv`，可以通过 `pip` 进行安装：

```bash
pip install uv
```

>如果您希望安装uv standalone来尝试使用uv强大的python环境管理和包管理能力，并且希望一劳永逸地配置好国内的镜像环境，欢迎使用作者的开源项目：[uv-custom](https://github.com/Wangnov/uv-custom)

### 2. 配置 MCP

将以下配置代码添加到您的AI IDE （如Cursor）或 CLI 工具（如 Claude Code）的 mcp json 文件中。

```json
"gewe-notice": {
  "command": "uvx",
  "args": [
    "gewe-notice",
    "--token",
    "YOUR_GEWE_TOKEN",
    "--app-id",
    "YOUR_BOT_APP_ID",
    "--wxid",
    "YOUR_TARGET_WXID",
    "-a",
    "all"
  ]
}
```

**配置说明:**

*   `command`: 使用 `uvx`。`uvx` 命令可以临时下载并执行一个 PyPI 包，确保您总能方便地使用最新版本。
*   `args`:
    *   第一个参数必须是 PyPI 上的包名 `gewe-notice`。
    *   后续参数是 `gewe-notice` 的启动参数。您需要将 `YOUR_GEWE_TOKEN`、`YOUR_BOT_APP_ID` 和 `YOUR_TARGET_WXID` 替换为您自己的实际值。
    *   `"-a", "all"` 是可选的，用于在群聊中@其他人，或@所有人。

### 配置示例

<details>
<summary>点击展开查看四种不同场景的配置示例</summary>

#### 1. 发送给个人

```json
"gewe-notice": {
  "command": "uvx",
  "args": [
    "gewe-notice",
    "--token", "YOUR_GEWE_TOKEN",
    "--app-id", "YOUR_BOT_APP_ID",
    "--wxid", "wxid_xxxxxxxxxxxxx"
  ]
}
```

#### 2. 发送到群聊（不@任何人）

```json
"gewe-notice": {
  "command": "uvx",
  "args": [
    "gewe-notice",
    "--token", "YOUR_GEWE_TOKEN",
    "--app-id", "YOUR_BOT_APP_ID",
    "--wxid", "xxxxxxxxxx@chatroom"
  ]
}
```

#### 3. 发送到群聊并@所有人

```json
"gewe-notice": {
  "command": "uvx",
  "args": [
    "gewe-notice",
    "--token", "YOUR_GEWE_TOKEN",
    "--app-id", "YOUR_BOT_APP_ID",
    "--wxid", "xxxxxxxxxx@chatroom",
    "-a", "all"
  ]
}
```

#### 4. 发送到群聊并@特定成员

`args` 列表会按顺序平铺所有 `-a` 参数。

```json
"gewe-notice": {
  "command": "uvx",
  "args": [
    "gewe-notice",
    "--token", "YOUR_GEWE_TOKEN",
    "--app-id", "YOUR_BOT_APP_ID",
    "--wxid", "xxxxxxxxxx@chatroom",
    "-a", "wxid_aaaaaaaa",
    "-a", "wxid_bbbbbbbb"
  ]
}
```

</details>

配置完成后，您的 AI IDE 或 AI CLI 会在启动时自动运行 `gewe-notice` 服务器。

## ⚙️ 前置条件

在开始之前，您需要从您的 Gewe API 管理后台的 [微信管理页面](https://manager.geweapi.com/#/account/wechat) 中获取以下信息：

0. **Base_Url**: 默认无需配置，已设为 `http://api.geweapi.com` ，如果 Gewe 通知您 Base_Url 发生变动，则可通过管理后台的 [用户主页](https://manager.geweapi.com/index#/account/index) - 开通信息 查看 `API接口域名` 。如果你使用私有部署的Gewe API服务，则设为对应的服务器域名或IP地址。
1.  **API Token**: 用于认证的 `X-GEWE-TOKEN`。
2.  **App ID**: 您的微信机器人实例的 `appId`。
3.  **接收者 WXID**: 您希望接收通知的个人微信ID (`wxid_...`) 或群聊ID (`..._chatroom`)。
4.  **(可选) @对象的 WXID**: 如果您想在群聊中 `@` 特定的人，需要预先知道他们的 `wxid` 或者直接输入 `all` 以@所有人（需要管理员或群主权限）。

>关于如何获取他人或群聊的wxid，需要您自行测试，例如：启动一个http服务，用于接收 Gewe API 的回调消息。然后在官方微信客户端中发送消息（或从群聊中发送）给您的微信机器人，在回调消息结构体中找到对应的wxid。
>
>又例如：您可以调用 Gewe API 的 `搜索好友` 接口来搜索您想找到的机器人的好友 wxid ，调用 Gewe API 的 `获取通讯录列表` 接口来列出您的全部通讯录信息，从中找到想要获取的好友或群的 wxid 等。

## 🛠️ MCP 工具: `post_text`

本 MCP 服务器提供了一个名为 `post_text` 的工具。

### 参数

- `content` (string): 要发送的通知文本内容。

### 推荐的内容格式

为了保持通知的一致性和可读性，建议 `content` 遵循以下格式：

`[状态表情] [模块/主题] - [具体消息]`

- **状态表情**:
  - `✅ [Success]` - 操作成功完成。
  - `❌ [Error]` - 发生错误。

### 调用示例

您可以通过任何 MCP 客户端向此服务器发起工具调用。

```json
{
  "tool_name": "post_text",
  "parameters": {
    "content": "✅ [Project Init] - 项目初始化成功，所有依赖已安装。"
  }
}
```

另一个例子：

```json
{
  "tool_name": "post_text",
  "parameters": {
    "content": "❌ [API Call] - 编码任务失败，由于工具调用失败而终止。请返回 Agent 检查API密钥或网络连接。"
  }
}
```

您也可以自行在Agent中用提示词自由地配置指定通知的格式。

## 👨‍💻 开发者安装

如果您需要修改源代码或进行二次开发，可以克隆本仓库并从本地安装。

```bash
git clone https://github.com/wangnov/gewe-notice.git
cd gewe-notice
uv sync
```


## 📄 许可证

本项目基于 [MIT License](LICENSE) 授权。
