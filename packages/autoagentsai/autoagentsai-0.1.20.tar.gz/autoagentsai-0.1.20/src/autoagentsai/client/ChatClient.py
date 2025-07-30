from typing import Generator, Optional, List, Dict, Union, IO, Any
from ..api import chat_stream_api, get_chat_history_api, get_jwt_token_api


class ChatClient:
    def __init__(self, agent_id: str, personal_auth_key: str, personal_auth_secret: str, base_url: str = "https://uat.agentspro.cn"):
        """
        AutoAgents AI 对话客户端
        
        用于与 AutoAgents AI 平台进行对话交互的主要客户端类。
        支持文本对话、图片输入、文件上传等功能。
        
        Args:
            agent_id (str): Agent 的唯一标识符，用于调用Agent对话
                - 获取方式：Agent详情页 - 分享 - API
                
            auth_key (str): 认证密钥
                - 获取方式：右上角 - 个人密钥
                
            auth_secret (str): 认证密钥
                - 获取方式：右上角 - 个人密钥

            base_url (str, optional): API 服务基础地址
                - 默认值: "https://uat.agentspro.cn"
                - 测试环境: "https://uat.agentspro.cn"  
                - 生产环境: "https://agentspro.cn"
                - 私有部署时可指定自定义地址
        """
        self.agent_id = agent_id
        self.jwt_token = get_jwt_token_api(personal_auth_key, personal_auth_secret, base_url) 
        self.base_url = base_url
        self.chat_id = None

    def invoke(
        self,
        prompt: str,
        images: Optional[List[str]] = None,
        files: Optional[List[Union[str, IO]]] = None,
        state: Optional[Dict[str, str]] = None,
        button_key: Optional[str] = None,
        debug: bool = False,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        发起对话，以结构化事件流方式返回响应。

        这是与 Agent 交互的唯一方法，它通过产生结构化事件，使得前端可以同时实现
        多气泡和每个气泡的打字机效果，同时还支持显示 AI 的推理过程。

        Args:
            prompt (str): 用户输入的对话内容。
            images (List[str], optional): 图片 URL 列表。
            files (List[Union[str, IO]], optional): 文件列表。
            state (Dict[str, str], optional): 对话状态参数。
            button_key (str, optional): 按钮键值。
            debug (bool, optional): 调试模式。

        Yields:
            Dict[str, Any]: 一个包含事件类型和数据的字典。
                - `{'type': 'start_bubble', 'bubble_id': int}`: 标志着一个新的回复气泡开始。
                - `{'type': 'token', 'content': str}`: 当前气泡内的一个文本片段（用于打字机效果）。
                - `{'type': 'reasoning_token', 'content': str}`: AI 推理过程的文本片段。
                - `{'type': 'end_bubble'}`: 标志着当前回复气泡结束。
                - `{'type': 'finish'}`: 标志着整个对话回合结束。
        
        示例:
            .. code-block:: python

                for event in client.invoke("写一首关于AI的诗"):
                    if event['type'] == 'start_bubble':
                        print(f"\\n--- 新气泡 {event['bubble_id']} ---")
                    elif event['type'] == 'token':
                        print(event['content'], end="")
                    elif event['type'] == 'reasoning_token':
                        print(f"[推理: {event['content']}]", end="")
                    elif event['type'] == 'end_bubble':
                        print("\\n--- 气泡结束 ---")
                    elif event['type'] == 'finish':
                        print("\\n\\n对话完成。")
        """
        current_reply = ""
        bubble_id_counter = 0

        api_stream = chat_stream_api(
            agent_id=self.agent_id,
            jwt_token=self.jwt_token,
            base_url=self.base_url,
            prompt=prompt,
            chat_id=self.chat_id,
            images=images,
            files=files,
            state=state,
            button_key=button_key,
            debug=debug
        )

        for content, reasoning_content, chat_id, complete, finish in api_stream:
            if chat_id is not None:
                self.chat_id = chat_id

            # 处理推理内容
            if reasoning_content:
                yield {"type": "reasoning_token", "content": reasoning_content}

            if content and not current_reply:
                bubble_id_counter += 1
                yield {"type": "start_bubble", "bubble_id": bubble_id_counter}
            
            if content:
                current_reply += content
                yield {"type": "token", "content": content}

            if complete and current_reply.strip():
                yield {"type": "end_bubble"}
                current_reply = ""

            if finish:
                yield {"type": "finish"}
                break
                
    def history(self):
        """
        获取当前对话的历史记录
        
        返回当前对话会话中的所有历史消息，包括用户消息和 AI 回复。
        只有在已经进行过对话（存在 chat_id）的情况下才能获取历史记录。
        
        Returns:
            List[Dict[str, str]]: 对话历史记录列表
                - 每个元素是一个包含 role 和 content 的字典
                - role 字段值：
                  - "user": 用户发送的消息
                  - "assistant": AI 助手的回复
                - content 字段：消息的具体内容
                - 记录按时间顺序排列（最新的在最后）
                
        示例:
            Example 1: 获取历史记录
            .. code-block:: python

                from autoagentsai.client import ChatClient
                client = ChatClient(agent_id="your_agent_id", personal_auth_key="your_personal_auth_key", personal_auth_secret="your_personal_auth_secret")
                for chunk in client.invoke("你好"):
                    print(chunk, end="", flush=True)
                
                history = client.history()
                for msg in history:
                    print(f"{msg['role']}: {msg['content']}")
            
            输出示例:
            [
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": "您好！我是AI助手，很高兴为您服务。有什么可以帮助您的吗？"}
            ]
            
        注意:
            - 如果还没有进行过对话，返回空列表 []
            - 历史记录会随着对话的进行自动更新
            - 每次调用 invoke() 后都可以通过此方法获取最新的历史记录
        """
        if self.chat_id:
            return get_chat_history_api(
                agent_id=self.agent_id,
                jwt_token=self.jwt_token,
                base_url=self.base_url,
                chat_id=self.chat_id
            )
        return []
