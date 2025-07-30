import json
import requests
from typing import Generator, Optional, List, Dict, Union, IO
from .models import ChatRequest, ImageInput, ChatHistoryRequest
from .uploader import FileUploader


def chat_stream_api(
    agent_id: str,
    jwt_token: str,
    base_url: str,
    prompt: str,
    chat_id: Optional[str] = None,
    images: Optional[List[str]] = None,
    files: Optional[List[Union[str, IO]]] = None,
    state: Optional[Dict[str, str]] = None,
    button_key: Optional[str] = None,
    debug: bool = False
) -> Generator[tuple[Optional[str], Optional[str], bool, bool], None, None]:
    """
    核心的流式聊天 API
    
    返回: Generator[tuple[content, chat_id, complete, finish], None, None]
    - content: 聊天内容片段
    - chat_id: 对话 ID
    - complete: 是否完成一次回复（true时表示一个回复气泡完成）
    - finish: 是否完成整个会话（true时表示整个对话结束）
    """
    uploader = FileUploader(jwt_token=jwt_token, base_url=base_url)
    file_inputs = uploader.ensure_file_inputs(files)

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    req = ChatRequest(
        agentId=agent_id,
        chatId=chat_id,
        userChatInput=prompt,
        images=[ImageInput(url=u) for u in images] if images else [],
        files=file_inputs,
        state=state or {},
        buttonKey=button_key or "",
        debug=debug
    )
    url = f"{base_url}/api/chat/stream/input/v2"

    try:
        response = requests.post(url, headers=headers, json=req.model_dump(), stream=True, timeout=30)
        if response.status_code != 200:
            yield (f"Error {response.status_code}: {response.text}", None, False, True)
            return

        buffer = ""
        current_chat_id = chat_id
        for chunk in response.iter_content(chunk_size=512, decode_unicode=False):
            if not chunk:
                continue
            # 直接使用 UTF-8 解码原始字节
            try:
                chunk_str = chunk.decode('utf-8')
                buffer += chunk_str
            except UnicodeDecodeError:
                # 如果解码失败，跳过这个chunk
                continue

            while "\n\ndata:" in buffer or buffer.startswith("data:"):
                if buffer.startswith("data:"):
                    end_pos = buffer.find("\n\n")
                    if end_pos == -1:
                        break
                    message = buffer[5:end_pos]
                    buffer = buffer[end_pos + 2:]
                else:
                    start = buffer.find("\n\ndata:") + 7
                    end = buffer.find("\n\n", start)
                    if end == -1:
                        break
                    message = buffer[start:end]
                    buffer = buffer[end + 2:]

                try:
                    data = json.loads(message)
                    if "chatId" in data:
                        current_chat_id = data["chatId"]
                    
                    is_complete = data.get("complete", False)
                    is_finish = data.get("finish", False)
                    
                    if "content" in data and data["content"]:
                        content = data["content"]
                        yield (content, current_chat_id, is_complete, is_finish)
                    elif is_complete or is_finish:
                        # 即使没有内容，也需要传递 complete/finish 状态
                        yield (None, current_chat_id, is_complete, is_finish)
                    
                    # 只有在 finish 为 true 时才结束流
                    if is_finish:
                        return
                except Exception:
                    continue
    except Exception as e:
        yield (f"Stream error: {str(e)}", None, False, True)

def get_chat_history_api(
    agent_id: str,
    jwt_token: str,
    base_url: str,
    chat_id: str,
    page_size: int = 100,
    page_number: int = 1
) -> List[Dict[str, str]]:
    """获取聊天历史的 API"""
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    req = ChatHistoryRequest(
        agentId=agent_id,
        agentUUid=agent_id,
        chatId=chat_id,
        pageSize=page_size,
        pageNumber=page_number
    )

    url = f"{base_url}/api/chat/detail"
    response = requests.post(url, headers=headers, json=req.model_dump(), timeout=30)

    def extract_chat_history(data: List[dict]) -> List[dict]:
        """提取和格式化聊天历史"""
        history = []
        for item in data:
            role = item.get("role")
            content = item.get("content", "").strip()
            if role == "user":
                history.append({"role": "user", "content": content})
            elif role == "ai":
                history.append({"role": "assistant", "content": content})
        return history[::-1]

    if response.status_code == 200:
        raw_data = response.json().get("data", [])
        return extract_chat_history(raw_data)

    return []


def get_jwt_token_api(
    personal_auth_key: str,
    personal_auth_secret: str,
    base_url: str,
) -> str:
    """
    获取 AutoAgents AI 平台的 JWT 认证令牌，用户级认证，用于后续的 API 调用认证。
    JWT token 具有时效性，30天过期后需要重新获取。
    
    Args:
        agent_id (str): Agent 的唯一标识符，用于调用Agent对话
            - 获取方式：Agent详情页 - 分享 - API
            
        personal_auth_key (str): 认证密钥
            - 获取方式：右上角 - 个人密钥
            
        personal_auth_secret (str): 认证密钥
            - 获取方式：右上角 - 个人密钥

        base_url (str, optional): API 服务基础地址
            - 默认值: "https://uat.agentspro.cn"
            - 测试环境: "https://uat.agentspro.cn"  
            - 生产环境: "https://agentspro.cn"
            - 私有部署时可指定自定义地址
            
    Returns:
        str: JWT 认证令牌            
    """
    
    headers = {
        "Authorization": f"Bearer {personal_auth_key}.{personal_auth_secret}",
        "Content-Type": "application/json"
    }

    url = f"{base_url}/openapi/user/auth"
    response = requests.get(url, headers=headers)
    return response.json()["data"]["token"]