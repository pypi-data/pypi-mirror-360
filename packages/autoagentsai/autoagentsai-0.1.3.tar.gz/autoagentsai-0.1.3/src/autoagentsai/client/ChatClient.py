# src/autoagentsai/client.py
import json
import requests
from typing import Generator, Optional, List, Dict
from autoagentsai.models import ChatRequest, ImageInput, ChatHistoryRequest

class ChatClient:
    def __init__(self, agent_id: str, auth_key: str, auth_secret: str, platform: str = "uat", jwt_token: Optional[str] = None):
        AUTOAGENTS_HOST = {
            "uat": "https://uat.agentspro.cn",
            "test": "https://test.agentspro.cn",
            "lingda": "https://lingda.agentspro.cn"
        }

        if platform not in AUTOAGENTS_HOST:
            raise ValueError(f"Unsupported platform: {platform}")
        self.agent_id = agent_id
        self.auth_key = auth_key
        self.auth_secret = auth_secret
        self.base_url = AUTOAGENTS_HOST[platform]
        self.headers = {
            "Authorization": f"Bearer {auth_key}.{auth_secret}",
            "Content-Type": "application/json"
        }
        self.headers_v2 = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        self.chat_id = None

    def chat(
        self,
        prompt: str,
        chat_id: Optional[str] = None,
        images: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        state: Optional[Dict[str, str]] = None,
        button_key: Optional[str] = None,
        debug: bool = False
    ):
        """非流式调用"""
        req = ChatRequest(
            agentId=self.agent_id,
            chatId=chat_id,
            userChatInput=prompt,
            images=[ImageInput(url=u) for u in images] if images else [],
            files=files or [],
            state=state or {},
            buttonKey=button_key or "",
            debug=debug
        )
        url = f"{self.base_url}/openapi/agents/chat/completions/v1"

        try:
            response = requests.post(url, headers=self.headers, json=req.model_dump(), timeout=30)
            if response.status_code == 200:
                # return response.json()["choices"][0]["content"]
                return response.json(), response.json()['chatId']
            return f"Error {response.status_code}: {response.text}"
        except Exception as e:
            return f"Exception: {str(e)}"

    def get_chat_history(self, chat_id: str, page_size: int = 100, page_number: int = 1) -> List[Dict[str, str]]:
        req = ChatHistoryRequest(
            agentId=self.agent_id,
            agentUUid=self.agent_id,
            chatId=chat_id,
            pageSize=page_size,
            pageNumber=page_number
        )

        url = f"{self.base_url}/api/chat/detail"
        response = requests.post(url, headers=self.headers_v2, json=req.model_dump(), timeout=30)

        if response.status_code == 200:
            raw_data = response.json().get("data", [])
            return self.extract_chat_history(raw_data)

        return []

    def extract_chat_history(self, data: List[dict]) -> List[dict]:
        history = []
        for item in data:
            role = item.get("role")
            content = item.get("content", "").strip()

            if role == "user":
                history.append({"role": "user", "content": content})
            elif role == "ai":
                history.append({"role": "assistant", "content": content})
        return history[::-1]

    def invoke(
        self,
        prompt: str,
        images: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        state: Optional[Dict[str, str]] = None,
        button_key: Optional[str] = None,
        debug: bool = False,
    ) -> str:
        """支持更丰富参数的对话调用"""
        result, chat_id = self.chat(
            prompt=prompt,
            chat_id=self.chat_id,
            images=images,
            files=files,
            state=state,
            button_key=button_key,
            debug=debug
        )
        self.chat_id = chat_id
        # 确保result是字典类型
        if isinstance(result, dict):
            return result["choices"][0]["content"]
        else:
            return str(result)

    def chat_stream(
        self,
        prompt: str,
        chat_id: Optional[str] = None,
        images: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        state: Optional[Dict[str, str]] = None,
        button_key: Optional[str] = None,
        debug: bool = False
    ) -> Generator[tuple, None, None]:
        """流式调用，返回(content, chat_id)元组生成器，chat_id只在最后返回"""
        req = ChatRequest(
            agentId=self.agent_id,
            chatId=chat_id,
            userChatInput=prompt,
            images=[ImageInput(url=u) for u in images] if images else [],
            files=files or [],
            state=state or {},
            buttonKey=button_key or "",
            debug=debug
        )
        url = f"{self.base_url}/openapi/agents/chat/stream/v1"

        try:
            response = requests.post(url, headers=self.headers, json=req.model_dump(), stream=True, timeout=30)
            if response.status_code != 200:
                yield (f"Error {response.status_code}: {response.text}", None)
                return

            buffer = ""
            current_chat_id = None
            for chunk in response.iter_content(chunk_size=512, decode_unicode=True):
                if not chunk:
                    continue
                buffer += chunk

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
                        
                        # 提取chat_id（如果存在）
                        if "chatId" in data:
                            current_chat_id = data["chatId"]
                        
                        if "content" in data and data["content"]:
                            try:
                                content = data["content"].encode("latin1").decode("utf-8")
                            except Exception:
                                content = data["content"]
                            yield (content, None)
                        
                        if data.get("complete") or data.get("finish"):
                            # 在完成时返回chat_id
                            yield (None, current_chat_id)
                            return
                    except Exception:
                        continue
        except Exception as e:
            yield (f"Stream error: {str(e)}", None)

    def invoke_stream(
        self,
        prompt: str,
        images: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        state: Optional[Dict[str, str]] = None,
        button_key: Optional[str] = None,
        debug: bool = False,
    ) -> Generator[str, None, None]:
        """支持更丰富参数的流式对话调用"""
        for content, chat_id in self.chat_stream(
            prompt=prompt,
            chat_id=self.chat_id,
            images=images,
            files=files,
            state=state,
            button_key=button_key,
            debug=debug
        ):
            if chat_id is not None:
                # 更新chat_id状态
                self.chat_id = chat_id
            elif content is not None:
                # 只yield内容，不yield None内容
                yield content

    def history(self):
        if self.chat_id:
            return self.get_chat_history(chat_id=self.chat_id)
        return []




if __name__ == "__main__":
    client = ChatClient(
        agent_id="fe91cf3348bb419ba907b1e690143006",
        auth_key="fe91cf3348bb419ba907b1e690143006",
        auth_secret="mLin0asZ7YRRRxI6Cpwb8hxqZ2N9Wf4X",
        jwt_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiL01Nd1ZDYlRZY2dHWUtCOE1NSVo4dVFHN05BYXYrRlR6Szl3bEQ4bWU0UjQzUldVa2JlWC9CS1VkM3N3ck9ZQmMvYnlUMDc1YzhwRVUzbDdwZ3BGc0l5b0p4L3ZRdXdzS0ozMTZqd0V5RTVBTXFBUXFzcjRwWXF3OHk2WU9PY2dpbVhuenJqOWVOV01hc2tqOFc2b2l3RUFza1pxTUlWUVN6NUxsdE14WHMvV0lGaW1zYjF5RTdpdmR0WGszR0svdHBlTXA1cWdGKzErVGFBNkx1ZDZLK2V0UGQwWkRtWE8vMEZJNGtDaC9zST0iLCJleHAiOjE3NTQxMjk1MzR9.96Q5LOMf8Ve4GCxuOeMW7zISnksGKVLI0UduXQ8RbH8"
    )   

    # 测试第一次流式调用
    print("=== Testing first invoke_stream ===")
    for chunk in client.invoke_stream("你好"):
        print(chunk, end="", flush=True)
    print("\n")

    # 测试第二次流式调用
    print("=== Testing second invoke_stream ===")
    for chunk in client.invoke_stream("请重复我刚才说的"):
        print(chunk, end="", flush=True)
    print("\n")

    # 测试第三次流式调用
    print("\n=== Testing third invoke_stream ===")
    for chunk in client.invoke_stream("请告诉我之前都说过什么"):
        print(chunk, end="", flush=True)
    print("\n")
    
    # 测试历史记录
    print("=== Testing history ===")
    history = client.history()
    print(history)