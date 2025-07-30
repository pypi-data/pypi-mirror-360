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
            Generator[str, None, None]: 流式回复生成器
                - 每次 yield 返回一个完整的回复字符串
                - 自动处理多次回复：一次输入可能产生多个回复
                - 自动过滤空回复
                - 每个返回的字符串可直接作为独立气泡显示
                - 适合前端单轮对话多气泡场景和后端调试
                
        示例:
            Example 1: 基础文本对话（多气泡）
            .. code-block:: python

                from autoagentsai.client import ChatClient
                client = ChatClient(agent_id="your_agent_id", personal_auth_key="your_key", personal_auth_secret="your_secret")
                
                reply_count = 0
                for reply in client.invoke("你好"):
                    reply_count += 1
                    print(f"第{reply_count}个回复: {reply}")
                    # 每个 reply 可直接作为独立气泡显示
            
            Example 2: 上传本地文件并分析

            .. code-block:: python

                from autoagentsai.uploader import create_file_like
                file_obj = create_file_like("./document.pdf")
                
                for reply in client.invoke("请分析这个文档", files=[file_obj]):
                    print(f"分析结果: {reply}")
                    # 每个回复可以显示为独立的分析结果气泡
            
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
                    responses = []
                    
                    for reply in client.invoke(prompt, files=[file_obj]):
                        responses.append(reply)
                        
                    return JSONResponse(content={
                        "code": 200, 
                        "message": "success", 
                        "data": {
                            "responses": responses  # 返回多个回复
                        }
                    })

                if __name__ == "__main__":
                    import uvicorn
                    uvicorn.run(app, host="0.0.0.0", port=8000)

            Example 4: 多模态输入

            .. code-block:: python

                from autoagentsai.client import ChatClient
                client = ChatClient(agent_id="your_agent_id", personal_auth_key="your_key", personal_auth_secret="your_secret")
                
                reply_count = 0
                for reply in client.invoke(
                    prompt="分析这张图片和文档",
                    images=["https://example.com/chart.png"],
                    files=["./data.xlsx"]
                ):
                    reply_count += 1
                    print(f"第{reply_count}个分析结果: {reply}")
                    # 可以将每个回复发送到前端显示为独立气泡
                
                print(f"共收到 {reply_count} 个分析结果")
            
            Example 5: WebSocket 实时多气泡推送

            .. code-block:: python

                from fastapi import FastAPI, WebSocket
                from autoagentsai.client import ChatClient
                import json
                import asyncio

                app = FastAPI()
                client = ChatClient(agent_id="your_agent_id", personal_auth_key="your_key", personal_auth_secret="your_secret")

                @app.websocket("/chat")
                async def websocket_endpoint(websocket: WebSocket):
                    await websocket.accept()
                    
                    while True:
                        # 接收前端消息
                        data = await websocket.receive_text()
                        message = json.loads(data)
                        user_input = message.get("message", "")
                        
                        # 发送多个回复气泡
                        bubble_count = 0
                        for reply in client.invoke(user_input):
                            bubble_count += 1
                            await websocket.send_text(json.dumps({
                                "type": "new_bubble",
                                "bubble_id": bubble_count,
                                "content": reply,
                                "timestamp": int(time.time() * 1000)
                            }))
                        
                        # 发送会话结束标识
                        await websocket.send_text(json.dumps({
                            "type": "chat_complete",
                            "total_bubbles": bubble_count
                        }))

            Example 6: 前端 JavaScript 多气泡实现

            .. code-block:: html

                <!DOCTYPE html>
                <html>
                <head>
                    <title>AI 多气泡聊天</title>
                    <style>
                        .chat-container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .message { margin: 10px 0; padding: 10px; border-radius: 10px; }
                        .user-message { background: #007bff; color: white; text-align: right; }
                        .ai-bubble { background: #f1f1f1; margin: 5px 0; animation: fadeIn 0.3s; }
                        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
                        .bubble-group { border-left: 3px solid #28a745; padding-left: 10px; margin: 10px 0; }
                        .input-area { position: fixed; bottom: 20px; width: 100%; max-width: 600px; }
                        .loading { color: #666; font-style: italic; }
                    </style>
                </head>
                <body>
                    <div class="chat-container">
                        <div id="messages"></div>
                    </div>
                    
                    <div class="input-area">
                        <input type="text" id="messageInput" placeholder="输入消息..." style="width: 80%;">
                        <button onclick="sendMessage()" style="width: 18%;">发送</button>
                    </div>

                    <script>
                        const ws = new WebSocket('ws://localhost:8000/chat');
                        const messagesDiv = document.getElementById('messages');
                        let currentBubbleGroup = null;

                        ws.onmessage = function(event) {
                            const data = JSON.parse(event.data);
                            
                            if (data.type === 'new_bubble') {
                                // 如果是第一个气泡，创建新的气泡组
                                if (data.bubble_id === 1) {
                                    currentBubbleGroup = document.createElement('div');
                                    currentBubbleGroup.className = 'bubble-group';
                                    messagesDiv.appendChild(currentBubbleGroup);
                                    
                                    // 移除加载提示
                                    const loading = document.querySelector('.loading');
                                    if (loading) loading.remove();
                                }
                                
                                // 创建新的气泡
                                const bubble = document.createElement('div');
                                bubble.className = 'message ai-bubble';
                                bubble.textContent = data.content;
                                currentBubbleGroup.appendChild(bubble);
                                
                                // 滚动到底部
                                messagesDiv.scrollTop = messagesDiv.scrollHeight;
                            }
                            
                            if (data.type === 'chat_complete') {
                                console.log(`收到 ${data.total_bubbles} 个回复气泡`);
                                currentBubbleGroup = null;
                            }
                        };

                        function sendMessage() {
                            const input = document.getElementById('messageInput');
                            const message = input.value.trim();
                            if (!message) return;

                            // 显示用户消息
                            const userMsg = document.createElement('div');
                            userMsg.className = 'message user-message';
                            userMsg.textContent = message;
                            messagesDiv.appendChild(userMsg);
                            
                            // 显示加载提示
                            const loading = document.createElement('div');
                            loading.className = 'loading';
                            loading.textContent = 'AI 正在思考...';
                            messagesDiv.appendChild(loading);

                            // 发送消息到后端
                            ws.send(JSON.stringify({message: message}));
                            
                            // 清空输入框
                            input.value = '';
                            messagesDiv.scrollTop = messagesDiv.scrollHeight;
                        }

                        // 回车发送消息
                        document.getElementById('messageInput').addEventListener('keypress', function(e) {
                            if (e.key === 'Enter') {
                                sendMessage();
                            }
                        });
                    </script>
                </body>
                </html>

            Example 7: Server-Sent Events (SSE) 实现

            .. code-block:: python

                from fastapi import FastAPI
                from fastapi.responses import StreamingResponse
                from autoagentsai.client import ChatClient
                import json

                app = FastAPI()
                client = ChatClient(agent_id="your_agent_id", personal_auth_key="your_key", personal_auth_secret="your_secret")

                @app.get("/chat-stream")
                async def chat_stream(message: str):
                    def generate_response():
                        bubble_count = 0
                        for reply in client.invoke(message):
                            bubble_count += 1
                            # SSE 格式输出
                            yield f"data: {json.dumps({
                                'type': 'new_bubble',
                                'bubble_id': bubble_count,
                                'content': reply
                            })}\n\n"
                        
                        # 结束标识
                        yield f"data: {json.dumps({
                            'type': 'chat_complete',
                            'total_bubbles': bubble_count
                        })}\n\n"

                    return StreamingResponse(
                        generate_response(),
                        media_type="text/plain",
                        headers={
                            "Cache-Control": "no-cache",
                            "Connection": "keep-alive",
                            "Content-Type": "text/event-stream"
                        }
                    )

            对应的前端 SSE 代码:

            .. code-block:: javascript

                function sendMessageSSE(message) {
                    const eventSource = new EventSource(`/chat-stream?message=${encodeURIComponent(message)}`);
                    
                    let currentBubbleGroup = null;
                    
                    eventSource.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        
                        if (data.type === 'new_bubble') {
                            // 创建或使用气泡组
                            if (data.bubble_id === 1) {
                                currentBubbleGroup = document.createElement('div');
                                currentBubbleGroup.className = 'bubble-group';
                                document.getElementById('messages').appendChild(currentBubbleGroup);
                            }
                            
                            // 添加新气泡
                            const bubble = document.createElement('div');
                            bubble.className = 'message ai-bubble';
                            bubble.textContent = data.content;
                            currentBubbleGroup.appendChild(bubble);
                        }
                        
                        if (data.type === 'chat_complete') {
                            eventSource.close();  // 关闭连接
                            console.log(`收到 ${data.total_bubbles} 个回复气泡`);
                        }
                    };
                }

            Example 8: React 组件实现

            .. code-block:: javascript

                import React, { useState, useEffect, useRef } from 'react';

                const MultiBubbleChat = () => {
                    const [messages, setMessages] = useState([]);
                    const [input, setInput] = useState('');
                    const [isLoading, setIsLoading] = useState(false);
                    const messagesEndRef = useRef(null);

                    const scrollToBottom = () => {
                        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
                    };

                    useEffect(() => {
                        scrollToBottom();
                    }, [messages]);

                    const sendMessage = async () => {
                        if (!input.trim()) return;

                        // 添加用户消息
                        const userMessage = { type: 'user', content: input, id: Date.now() };
                        setMessages(prev => [...prev, userMessage]);
                        
                        const currentInput = input;
                        setInput('');
                        setIsLoading(true);

                        // 创建新的气泡组
                        const bubbleGroupId = Date.now();
                        const bubbleGroup = { 
                            type: 'bubble-group', 
                            id: bubbleGroupId, 
                            bubbles: [] 
                        };
                        setMessages(prev => [...prev, bubbleGroup]);

                        try {
                            const response = await fetch(`/chat-stream?message=${encodeURIComponent(currentInput)}`);
                            const reader = response.body.getReader();

                            while (true) {
                                const { done, value } = await reader.read();
                                if (done) break;

                                const chunk = new TextDecoder().decode(value);
                                const lines = chunk.split('\n');

                                for (const line of lines) {
                                    if (line.startsWith('data: ')) {
                                        const data = JSON.parse(line.slice(6));
                                        
                                        if (data.type === 'new_bubble') {
                                            setMessages(prev => prev.map(msg => 
                                                msg.id === bubbleGroupId 
                                                    ? { ...msg, bubbles: [...msg.bubbles, {
                                                        id: data.bubble_id,
                                                        content: data.content
                                                    }]}
                                                    : msg
                                            ));
                                        }
                                    }
                                }
                            }
                        } catch (error) {
                            console.error('聊天错误:', error);
                        } finally {
                            setIsLoading(false);
                        }
                    };

                    return (
                        <div className="chat-container">
                            <div className="messages">
                                {messages.map(msg => {
                                    if (msg.type === 'user') {
                                        return (
                                            <div key={msg.id} className="user-message">
                                                {msg.content}
                                            </div>
                                        );
                                    } else if (msg.type === 'bubble-group') {
                                        return (
                                            <div key={msg.id} className="bubble-group">
                                                {msg.bubbles.map(bubble => (
                                                    <div key={bubble.id} className="ai-bubble">
                                                        {bubble.content}
                                                    </div>
                                                ))}
                                            </div>
                                        );
                                    }
                                })}
                                {isLoading && <div className="loading">AI 正在思考...</div>}
                                <div ref={messagesEndRef} />
                            </div>
                            
                            <div className="input-area">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                                    placeholder="输入消息..."
                                    disabled={isLoading}
                                />
                                <button onClick={sendMessage} disabled={isLoading}>
                                    发送
                                </button>
                            </div>
                        </div>
                    );
                };

                export default MultiBubbleChat;
        """

        current_reply = ""
        for content, chat_id, complete, finish in chat_stream_api(
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
            
            if content:
                current_reply += content
            
            if complete and current_reply.strip():
                # 一个完整回复完成且有内容
                yield current_reply
                current_reply = ""  # 重置为下一个回复
            
            if finish:
                # 会话结束
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
