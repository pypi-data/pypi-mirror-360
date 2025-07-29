import httpx
from fastmcp import FastMCP
from typing_extensions import Annotated
from pydantic import Field
from typing import Dict, Optional
from loguru import logger

# 全局配置字典
config = {
    "base_url": "http://api.geweapi.com",
    "token": "",
    "app_id": "",
    "wxid": "",
    "at_list": []
}

# 实例化 MCP 服务器
mcp = FastMCP(
    name="Gewe Notice Server",
    instructions="一个通过微信机器人发送通知的 MCP 服务器。"
)


def _get_chatroom_member_names(chatroom_id: str) -> Optional[Dict[str, str]]:
    """调用API获取群成员列表，并返回一个 wxid -> name 的映射字典。"""
    logger.info(f"正在为群 {chatroom_id} 获取成员列表...")
    url = f"{config['base_url']}/gewe/v2/api/group/getChatroomMemberList"
    headers = {"X-GEWE-TOKEN": config["token"],
               "Content-Type": "application/json"}
    payload = {"appId": config["app_id"], "chatroomId": chatroom_id}

    try:
        with httpx.Client() as client:
            response = client.post(url, headers=headers,
                                   json=payload, timeout=20.0)

        # 尝试解析响应
        response_data = None
        try:
            response_data = response.json()
        except Exception:
            # 即使JSON解析失败，也继续检查状态码
            pass

        # 检查特定业务错误: ret=500, msg="获取群成员列表异常:null"
        if response_data and response_data.get("ret") == 500 and response_data.get("msg") == "获取群成员列表异常:null":
            logger.error(
                f"❌ 获取群成员列表失败: 你可能已不在群 {chatroom_id} 内或该群聊不存在。(ret: 500)")
            return None

        if response.status_code == 200 and response_data:
            data = response_data.get("data", {})
            member_list = data.get("memberList", [])
            if not member_list:
                # 这种情况可能是群里只有自己，或者API行为如此
                logger.warning("⚠️ 警告: 获取到空的群成员列表。")
                return {}

            # 创建 wxid -> name 的映射
            # 优先使用 displayName，如果为空，则使用 nickName
            name_map = {
                member["wxid"]: member["displayName"] or member["nickName"]
                for member in member_list
            }
            logger.info("✅ 成功获取并解析群成员列表。")
            return name_map
        else:
            logger.error(
                f"❌ 获取群成员列表失败，状态码: {response.status_code}, 响应: {response.text}")
            return None
    except httpx.RequestError as e:
        logger.error(f"❌ 获取群成员时发生网络错误: {e}")
        return None


@mcp.tool()
def post_text(
    content: Annotated[str, Field(description="要发送的通知文本内容。")]
):
    """
    发送 AI 任务状态通知。Agent 应在任务完成或发生关键错误时调用此工具。
    Sends AI task status notifications. The Agent should call this tool upon task completion or when a critical error occurs.

    ### 调用时机 (When to Call):
    - **任务完成时 (On Task Completion)**: 在成功执行完整个任务后，发送最终结果通知。
    - **发生关键错误时 (On Critical Error)**: 当任务因无法自动解决的错误而中断时。

    ### 内容格式 (Content Format):
    为了保持通知的一致性和可读性，`content` 参数应遵循以下结构化格式:
    To maintain consistency and readability, the `content` parameter should follow this structured format:
    `[状态表情] [模块/主题] - [具体消息]`

    - **状态表情 (Status Emoji)**:
      - `✅ [Success]`   - 操作成功完成 (Operation completed successfully)。
      - `❌ [Error]`     - 发生错误 (An error occurred)。

    ### 使用示例 (Usage Examples):
    - `✅ [Project Init] - 项目初始化成功，依赖已安装。`
    - `✅ [Project Init] - Project initialization successful, dependencies installed.`
    - `❌ [API Call] - 调用 Gewe API 失败，请检查凭证或网络连接。`
    - `❌ [API Call] - Failed to call Gewe API, please check credentials or network connection.`
    """
    logger.info(f"准备发送通知: '{content}'")

    if not all([config["token"], config["app_id"], config["wxid"]]):
        error_msg = "错误：缺少必要的配置参数 (token, app_id, wxid)。"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}

    final_content = content
    ats_payload = None

    # 核心逻辑：检查是否为群聊且 at_list 有效
    is_chatroom = "@chatroom" in config["wxid"]
    at_list = config.get("at_list")

    if is_chatroom and at_list:
        logger.info("检测到群聊@请求，正在处理...")

        # 处理 @全体成员 的情况
        if at_list == ["all"]:
            ats_payload = "notify@all"
            final_content = "@所有人 " + content
            logger.info("将@全体成员，并在内容中添加@所有人。")
        else:
            # 处理 @特定成员 的情况
            member_name_map = _get_chatroom_member_names(config["wxid"])
            if member_name_map is not None:
                at_names = []
                valid_at_wxids = []
                for wxid in at_list:
                    name = member_name_map.get(wxid)
                    if name:
                        at_names.append(f"@{name}")
                        valid_at_wxids.append(wxid)
                    else:
                        logger.warning(f"⚠️ 警告: 在群成员列表中未找到 wxid: {wxid}")

                if at_names:
                    # 拼接@字符串到内容开头
                    mention_string = " ".join(at_names) + " "
                    final_content = mention_string + content
                    ats_payload = ",".join(valid_at_wxids)
                    logger.info(f"最终@内容: {mention_string}")
                    logger.info(f"最终ats参数: {ats_payload}")
            else:
                logger.error("❌ 因无法获取群成员列表，@功能已跳过。")

    # 构建最终的API请求
    url = f"{config['base_url']}/gewe/v2/api/message/postText"
    headers = {"X-GEWE-TOKEN": config["token"],
               "Content-Type": "application/json"}
    payload = {
        "appId": config["app_id"],
        "toWxid": config["wxid"],
        "content": final_content
    }
    if ats_payload:
        payload["ats"] = ats_payload

    try:
        with httpx.Client() as client:
            response = client.post(url, headers=headers,
                                   json=payload, timeout=10.0)

        # 检查是否因为无权限@所有人而失败 (特征: ret=500, data.code="-2")
        # 并在此情况下自动重试
        is_at_all_permission_error = False
        if is_chatroom and at_list == ["all"] and response.status_code != 200:
            try:
                error_data = response.json()
                if error_data.get("ret") == 500 and str(error_data.get("data", {}).get("code")) == "-2":
                    is_at_all_permission_error = True
            except Exception:
                pass  # 响应非JSON或格式不符，按原流程处理

        if is_at_all_permission_error:
            logger.warning("⚠️ 警告: @全体成员失败，无权限。将尝试不@全体成员重试。")
            # 构建不带@的重试请求
            retry_payload = {
                "appId": config["app_id"],
                "toWxid": config["wxid"],
                "content": content  # 使用原始 content
            }
            with httpx.Client() as client_retry:
                response = client_retry.post(
                    url, headers=headers, json=retry_payload, timeout=10.0)

        # --- 通用响应处理 ---
        response_data = None
        try:
            # 尝试解析JSON响应体
            response_data = response.json()
        except Exception:
            pass

        # 检查业务是否完全成功
        if response.status_code == 200 and response_data and \
           response_data.get("ret") == 200 and "失败" not in response_data.get("msg", ""):
            logger.info(f"✅ 通知发送成功: {response_data}")
            return {"status": "success", "response": response_data}
        else:
            # 统一处理所有失败情况
            error_code_map = {
                "-219": "你已不在该群内。",
                "-104": "该群聊不存在。",
            }

            error_message = f"通知发送失败，HTTP状态码: {response.status_code}"
            specific_detail = ""

            if response_data:
                ret = response_data.get("ret")
                msg = response_data.get("msg")
                data_code = str(response_data.get("data", {}).get("code", ""))

                if data_code in error_code_map:
                    specific_detail = error_code_map[data_code]
                elif data_code == "-2":
                    # code -2 有多种含义，根据上下文判断
                    if not is_chatroom:
                        specific_detail = "对方不是你的好友或该微信用户不存在。"
                    else:
                        # 在群聊中，无权限@all的情况已经重试过
                        # 如果还到这里，说明是其他权限问题
                        specific_detail = "操作无权限（如@非好友）或遇到未知群聊错误。"

                error_message = f"API业务逻辑失败 (ret: {ret}, msg: '{msg}', data.code: {data_code or 'N/A'})"

            final_error_msg = f"❌ {error_message}"
            if specific_detail:
                final_error_msg += f" 具体原因: {specific_detail}"

            # 附加原始响应以便调试
            raw_response_text = response.text if not response_data else str(
                response_data)
            final_error_msg += f" 原始响应: {raw_response_text}"

            logger.error(final_error_msg)
            return {"status": "error", "message": final_error_msg, "response": response_data or response.text}

    except httpx.RequestError as e:
        error_msg = f"❌ 发送通知时发生网络错误: {e}"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}
