import json
import requests
from typing import Generator, Optional, List, Dict, Union, IO
from ..models import ChatRequest, ImageInput, FileInput, ChatHistoryRequest
from ..uploader import FileUploader


class ChatClient:
    def __init__(self, agent_id: str, auth_key: str, auth_secret: str, base_url: str = "https://uat.agentspro.cn", jwt_token: str = ""):
        """用于调用对话的客户端"""
        self.agent_id = agent_id
        self.auth_key = auth_key
        self.auth_secret = auth_secret
        self.jwt_token = jwt_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {auth_key}.{auth_secret}",
            "Content-Type": "application/json"
        }
        self.headers_v2 = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        self.chat_id = None
        self.uploader = FileUploader(jwt_token=self.jwt_token, base_url=base_url)



    def chat(
        self,
        prompt: str,
        chat_id: Optional[str] = None,
        images: Optional[List[str]] = None,
        files: Optional[List[Union[str, IO]]] = None,
        state: Optional[Dict[str, str]] = None,
        button_key: Optional[str] = None,
        debug: bool = False
    ):
        file_inputs = self.uploader.ensure_file_inputs(files)

        req = ChatRequest(
            agentId=self.agent_id,
            chatId=chat_id,
            userChatInput=prompt,
            images=[ImageInput(url=u) for u in images] if images else [],
            files=file_inputs,
            state=state or {},
            buttonKey=button_key or "",
            debug=debug
        )
        url = f"{self.base_url}/openapi/agents/chat/completions/v1"

        try:
            response = requests.post(url, headers=self.headers, json=req.model_dump(), timeout=30)
            if response.status_code == 200:
                return response.json(), response.json().get('chatId')
            return f"Error {response.status_code}: {response.text}", None
        except Exception as e:
            return f"Exception: {str(e)}", None

    def chat_stream(
        self,
        prompt: str,
        chat_id: Optional[str] = None,
        images: Optional[List[str]] = None,
        files: Optional[List[Union[str, IO]]] = None,
        state: Optional[Dict[str, str]] = None,
        button_key: Optional[str] = None,
        debug: bool = False
    ) -> Generator[tuple, None, None]:
        file_inputs = self.uploader.ensure_file_inputs(files)

        req = ChatRequest(
            agentId=self.agent_id,
            chatId=chat_id,
            userChatInput=prompt,
            images=[ImageInput(url=u) for u in images] if images else [],
            files=file_inputs,
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
                            content = data["content"].encode('latin-1').decode('utf-8')
                            yield (content, None)
                        if data.get("complete") or data.get("finish"):
                            yield (None, current_chat_id)
                            return
                    except Exception:
                        continue
        except Exception as e:
            yield (f"Stream error: {str(e)}", None)

    def invoke(
        self,
        prompt: str,
        images: Optional[List[str]] = None,
        files: Optional[List[Union[str, IO]]] = None,
        state: Optional[Dict[str, str]] = None,
        button_key: Optional[str] = None,
        debug: bool = False,
        stream: bool = False,
    ) -> Union[str, Generator[str, None, None]]:
        if stream:
            return self.invoke_stream_generator(
                prompt=prompt,
                images=images,
                files=files,
                state=state,
                button_key=button_key,
                debug=debug
            )
        else:
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
            if isinstance(result, dict):
                return result["choices"][0]["content"]
            else:
                return str(result)

    def invoke_stream_generator(
        self,
        prompt: str,
        images: Optional[List[str]] = None,
        files: Optional[List[Union[str, IO]]] = None,
        state: Optional[Dict[str, str]] = None,
        button_key: Optional[str] = None,
        debug: bool = False,
    ) -> Generator[str, None, None]:
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
                self.chat_id = chat_id
            elif content is not None:
                yield content

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
    print("=== Testing first invoke with stream=True ===")
    for chunk in client.invoke("你好", stream=True):
        print(chunk, end="", flush=True)
    print("\n")

    # 测试第二次流式调用
    print("=== Testing second invoke with stream=True ===")
    for chunk in client.invoke("请重复我刚才说的", stream=True):
        print(chunk, end="", flush=True)
    print("\n")

    # 测试第三次流式调用
    print("\n=== Testing third invoke with stream=True ===")
    for chunk in client.invoke("请告诉我之前都说过什么", stream=True):
        print(chunk, end="", flush=True)
    print("\n")

    # 测试非流式调用
    print("=== Testing non-stream invoke ===")
    result = client.invoke("你好吗？", stream=False)
    print(result)
    print("\n")
    
    # 测试历史记录
    print("=== Testing history ===")
    history = client.history()
    print(history)