from typing import Generator, Optional, List, Dict, Union, IO
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
    ) -> Generator[str, None, None]:
        """
        发起对话请求并获取流式响应
        
        向 AI Agent 发送消息并获取实时的流式回复。支持文本、图片、文件等多种输入类型。
        
        Args:
            prompt (str): 用户输入的对话内容
                - 必填参数，用户要发送给 AI 的文本消息
                
            images (List[str], optional): 图片 URL 列表
                - 可选参数，默认为 None
                - 每个元素为图片的 HTTP/HTTPS URL 地址
                - 支持常见图片格式：JPEG, PNG, GIF, WebP 等
                - 示例: ["https://example.com/image1.jpg", "https://example.com/image2.png"]
                
            files (List[Union[str, IO]], optional): 文件列表
                - 可选参数，默认为 None
                - 支持两种类型：
                  1. 文件路径字符串：如 "/path/to/document.pdf"
                  2. 文件对象：如 open("file.txt", "rb") 或 BytesIO 对象
                - 支持文件类型：PDF, TXT, DOC, DOCX, XLS, XLSX, PPT, PPTX 等
                - 文件会自动上传并在对话中引用
                - 示例: ["./report.pdf", open("data.xlsx", "rb")]
                
            state (Dict[str, str], optional): 对话状态参数
                - 可选参数，默认为 None
                - 用于传递额外的上下文信息或配置参数
                - 键值对格式，所有值都必须是字符串类型
                - 示例: {"language": "zh-CN", "format": "markdown"}
                
            button_key (str, optional): 按钮键值
                - 可选参数，默认为 None  
                - 用于触发特定的按钮操作或工作流
                - 通常在 Agent 配置了交互按钮时使用
                - 示例: "analyze_button", "summarize_action"
                
            debug (bool, optional): 调试模式
                - 可选参数，默认为 False
                - 启用时会返回更详细的调试信息
                - 用于开发和故障排查
                
        Returns:
            Generator[str, None, None]: 流式响应生成器
                - 生成器对象，逐步产出 AI 的回复内容
                - 每次 yield 返回一个字符串片段
                - 可通过 for 循环实时获取响应内容
                
        示例:
            Example 1: 基础文本对话
            .. code-block:: python

                from autoagentsai.client import ChatClient
                client = ChatClient(agent_id="your_agent_id", personal_auth_key="your_personal_auth_key", personal_auth_secret="your_personal_auth_secret")
                for chunk in client.invoke("你好"):
                    print(chunk, end="", flush=True)
            
            Example 2: 上传本地文件并分析

            .. code-block:: python

                from autoagentsai.uploader import create_file_like
                file_obj = create_file_like("./document.pdf")
                for chunk in client.invoke("请分析这个文档", files=[file_obj]):
                    print(chunk, end="", flush=True)
            
            Example 3: 处理前端上传的文件并分析

            .. code-block:: python

                from fastapi import FastAPI, UploadFile, File
                from fastapi.responses import JSONResponse
                from autoagentsai.client import ChatClient
                from autoagentsai.uploader import create_file_like

                app = FastAPI()
                client = ChatClient(
                    agent_id="fe91cf3348bb419ba907b1e690143006",
                    personal_auth_key="e7a964a7e754413a9ea4bc1395a38d39",
                    personal_auth_secret="r4wBtqVD1qjItzQapJudKQPFozHAS9eb"
                )

                @app.post("/analyze")
                async def analyze_file(prompt: str, file: UploadFile = File(...)):
                    # 读取前端上传的文件
                    content = await file.read()
                    file_obj = create_file_like(content, filename=file.filename)
                    
                    # 调用 AI 分析
                    response = ""
                    for chunk in client.invoke(prompt, files=[file_obj]):
                        response += chunk
                        
                    return JSONResponse(content={
                        "code": 200, 
                        "message": "success", 
                        "data": {
                            "response": response
                        }
                    })

                if __name__ == "__main__":
                    import uvicorn
                    uvicorn.run(app, host="0.0.0.0", port=8000)

            Example 4: 多模态输入

            .. code-block:: python

                from autoagentsai.client import ChatClient
                client = ChatClient(agent_id="your_agent_id", personal_auth_key="your_personal_auth_key", personal_auth_secret="your_personal_auth_secret")
                for chunk in client.invoke(
                    prompt="分析这张图片和文档",
                    images=["https://example.com/chart.png"],
                    files=["./data.xlsx"]
                ):
                    print(chunk, end="", flush=True)
        """
        for content, chat_id in chat_stream_api(
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
        ):
            if chat_id is not None:
                self.chat_id = chat_id
            elif content is not None:
                yield content

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
