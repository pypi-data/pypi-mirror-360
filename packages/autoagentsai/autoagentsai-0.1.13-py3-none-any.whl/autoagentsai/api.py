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
) -> Generator[tuple[Optional[str], Optional[str]], None, None]:
    """
    核心的流式聊天 API
    
    返回: Generator[tuple[content, chat_id], None, None]
    - content: 聊天内容，为 None 时表示流结束
    - chat_id: 对话 ID，只在流结束时返回
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
            yield (f"Error {response.status_code}: {response.text}", None)
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
                    if "content" in data and data["content"]:
                        content = data["content"]
                        yield (content, None)
                    if data.get("complete") or data.get("finish"):
                        yield (None, current_chat_id)
                        return
                except Exception:
                    continue
    except Exception as e:
        yield (f"Stream error: {str(e)}", None)

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
    auth_key: str,
    auth_secret: str,
    base_url: str,
) -> str:
    """
    获取 AutoAgents AI 平台的 JWT 认证令牌
    
    使用认证密钥对向 AutoAgents 平台请求 JWT token，用于后续的 API 调用认证。
    JWT token 具有时效性，过期后需要重新获取。
    
    Args:
        auth_key (str): 认证密钥
            - 必填参数，在 AutoAgents 平台账户设置中获取
            - 格式：32位十六进制字符串
            - 示例: "5c03ac3c9d5447f5994e8426d39b7dfe"
            - 用于标识 API 调用方身份
            
        auth_secret (str): 认证密钥
            - 必填参数，在 AutoAgents 平台账户设置中获取
            - 格式：32位字母数字混合字符串
            - 示例: "rrRkpQDcMv77G9BYGJPJrMZy66l1ZRCS"
            - 与 auth_key 配合完成身份验证
            
        base_url (str): API 服务基础地址
            - 必填参数，指定 AutoAgents 平台的服务地址
            - 测试环境: "https://uat.agentspro.cn"
            - 生产环境: "https://agentspro.cn" 
            - 私有部署环境: 根据实际部署地址填写
            
    Returns:
        str: JWT 认证令牌
            - JWT 标准格式的字符串
            - 包含三部分：header.payload.signature
            - 用于后续 API 调用的身份认证
            - 示例: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiLi4uIn0.signature"
            
    认证密钥获取方式:
        1. 登录 AutoAgents 平台 (https://agentspro.cn)
        2. 进入账户设置或开发者设置页面
        3. 生成或查看 API 密钥对 (auth_key & auth_secret)
        4. 妥善保存密钥信息，避免泄露
        
    示例:
        >>> # 获取 JWT token
        >>> token = get_jwt_token_api(
        ...     auth_key="5c03ac3c9d5447f5994e8426d39b7dfe",
        ...     auth_secret="rrRkpQDcMv77G9BYGJPJrMZy66l1ZRCS", 
        ...     base_url="https://uat.agentspro.cn"
        ... )
        >>> print(f"获取到 token: {token[:50]}...")
        
        >>> # 在 ChatClient 中自动调用
        >>> client = ChatClient(
        ...     agent_id="fe91cf3348bb419ba907b1e690143006",
        ...     auth_key="5c03ac3c9d5447f5994e8426d39b7dfe",
        ...     auth_secret="rrRkpQDcMv77G9BYGJPJrMZy66l1ZRCS"
        ... )  # 内部自动调用 get_jwt_token_api
        
    异常情况:
        - KeyError: 当 API 响应格式不正确时
        - requests.RequestException: 当网络请求失败时  
        - 认证失败: 当密钥无效时 API 返回错误状态码
        
    注意事项:
        - JWT token 有过期时间，建议缓存并在过期前重新获取
        - 认证密钥应当保密，不要在代码中硬编码或提交到版本控制
        - 建议从环境变量或配置文件中读取认证信息
    """
    
    headers = {
        "Authorization": f"Bearer {auth_key}.{auth_secret}",
        "Content-Type": "application/json"
    }

    url = f"{base_url}/openapi/user/auth"
    response = requests.get(url, headers=headers)
    return response.json()["data"]["token"]