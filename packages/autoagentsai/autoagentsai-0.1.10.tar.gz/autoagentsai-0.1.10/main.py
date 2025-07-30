import os
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Union
import json
import io

from src.autoagentsai import ChatClient

app = FastAPI(title="AutoAgents AI API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class AskRequest(BaseModel):
    prompt: str
    stream: bool = False
    agent_id: Optional[str] = None
    chat_id: Optional[str] = None
    images: Optional[List[str]] = None
    auth_key: Optional[str] = None
    auth_secret: Optional[str] = None
    jwt_token: Optional[str] = None
    base_url: Optional[str] = "https://uat.agentspro.cn"

# 响应模型
class AskResponse(BaseModel):
    content: str
    chat_id: Optional[str] = None
    success: bool = True
    error: Optional[str] = None

# 默认配置（可以通过环境变量覆盖）
DEFAULT_CONFIG = {
    "agent_id": os.getenv("AUTOAGENTS_AGENT_ID", "fe91cf3348bb419ba907b1e690143006"),
    "auth_key": os.getenv("AUTOAGENTS_AUTH_KEY", "fe91cf3348bb419ba907b1e690143006"),
    "auth_secret": os.getenv("AUTOAGENTS_AUTH_SECRET", "mLin0asZ7YRRRxI6Cpwb8hxqZ2N9Wf4X"),
    "jwt_token": os.getenv("AUTOAGENTS_JWT_TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiL01Nd1ZDYlRZY2dHWUtCOE1NSVo4dVFHN05BYXYrRlR6Szl3bEQ4bWU0UjQzUldVa2JlWC9CS1VkM3N3ck9ZQmMvYnlUMDc1YzhwRVUzbDdwZ3BGc0l5b0p4L3ZRdXdzS0ozMTZqd0V5RTVBTXFBUXFzcjRwWXF3OHk2WU9PY2dpbVhuenJqOWVOV01hc2tqOFc2b2l3RUFza1pxTUlWUVN6NUxsdE14WHMvV0lGaW1zYjF5RTdpdmR0WGszR0svdHBlTXA1cWdGKzErVGFBNkx1ZDZLK2V0UGQwWkRtWE8vMEZJNGtDaC9zST0iLCJleHAiOjE3NTQxMjk1MzR9.96Q5LOMf8Ve4GCxuOeMW7zISnksGKVLI0UduXQ8RbH8"),
    "base_url": os.getenv("AUTOAGENTS_BASE_URL", "https://uat.agentspro.cn")
}

def create_client(config: dict) -> ChatClient:
    """创建ChatClient实例"""
    return ChatClient(
        agent_id=config["agent_id"],
        auth_key=config["auth_key"],
        auth_secret=config["auth_secret"],
        jwt_token=config["jwt_token"],
        base_url=config["base_url"]
    )

@app.get("/")
async def root():
    """健康检查端点"""
    return {"message": "AutoAgents AI API is running", "version": "1.0.0"}

@app.post("/ask")
async def ask_question(
    prompt: str = Form(...),
    stream: bool = Form(False),
    agent_id: Optional[str] = Form(None),
    chat_id: Optional[str] = Form(None),
    images: Optional[str] = Form(None),  # JSON字符串格式的图片URL列表
    auth_key: Optional[str] = Form(None),
    auth_secret: Optional[str] = Form(None),
    jwt_token: Optional[str] = Form(None),
    base_url: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    """
    AI对话端点
    
    参数：
    - prompt: 用户问题（必需）
    - stream: 是否流式返回（默认False）
    - agent_id: Agent ID（可选，使用默认值）
    - chat_id: 会话ID（可选，用于继续对话）
    - images: 图片URL列表，JSON字符串格式（可选）
    - files: 上传的文件列表（可选）
    - auth_key, auth_secret, jwt_token: 认证信息（可选，使用默认值）
    - base_url: API基础URL（可选，使用默认值）
    """
    try:
        # 构建配置
        config = DEFAULT_CONFIG.copy()
        if agent_id:
            config["agent_id"] = agent_id
        if auth_key:
            config["auth_key"] = auth_key
        if auth_secret:
            config["auth_secret"] = auth_secret
        if jwt_token:
            config["jwt_token"] = jwt_token
        if base_url:
            config["base_url"] = base_url

        # 创建客户端
        client = create_client(config)
        
        # 如果有chat_id，设置到客户端
        if chat_id:
            client.chat_id = chat_id

        # 解析图片URL列表
        image_urls = None
        if images:
            try:
                image_urls = json.loads(images)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid images format. Should be JSON array.")

        # 处理上传的文件
        file_objects = []
        if files:
            for file in files:
                if file.filename:
                    # 将UploadFile转换为file-like对象
                    file_content = await file.read()
                    file_obj = io.BytesIO(file_content)
                    file_obj.filename = file.filename  # 添加filename属性
                    file_objects.append(file_obj)

        # 执行对话
        if stream:
            # 流式响应
            def generate_stream():
                try:
                    for chunk in client.invoke(
                        prompt=prompt,
                        images=image_urls,
                        files=file_objects if file_objects else None,
                        stream=True
                    ):
                        if chunk:
                            # 返回Server-Sent Events格式
                            yield f"data: {json.dumps({'content': chunk, 'chat_id': client.chat_id})}\n\n"
                    
                    # 发送结束信号
                    yield f"data: {json.dumps({'content': '[DONE]', 'chat_id': client.chat_id})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

            return StreamingResponse(
                generate_stream(),
                media_type="text/plain",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
            )
        else:
            # 非流式响应
            content = client.invoke(
                prompt=prompt,
                images=image_urls,
                files=file_objects if file_objects else None,
                stream=False
            )
            
            return AskResponse(
                content=content,
                chat_id=client.chat_id,
                success=True
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/ask/json")
async def ask_question_json(request: AskRequest):
    """
    JSON格式的AI对话端点（不支持文件上传）
    """
    try:
        # 构建配置
        config = DEFAULT_CONFIG.copy()
        if request.agent_id:
            config["agent_id"] = request.agent_id
        if request.auth_key:
            config["auth_key"] = request.auth_key
        if request.auth_secret:
            config["auth_secret"] = request.auth_secret
        if request.jwt_token:
            config["jwt_token"] = request.jwt_token
        if request.base_url:
            config["base_url"] = request.base_url

        # 创建客户端
        client = create_client(config)
        
        # 如果有chat_id，设置到客户端
        if request.chat_id:
            client.chat_id = request.chat_id

        # 执行对话
        if request.stream:
            # 流式响应
            def generate_stream():
                try:
                    for chunk in client.invoke(
                        prompt=request.prompt,
                        images=request.images,
                        stream=True
                    ):
                        if chunk:
                            yield f"data: {json.dumps({'content': chunk, 'chat_id': client.chat_id})}\n\n"
                    
                    yield f"data: {json.dumps({'content': '[DONE]', 'chat_id': client.chat_id})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

            return StreamingResponse(
                generate_stream(),
                media_type="text/plain",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
            )
        else:
            # 非流式响应
            content = client.invoke(
                prompt=request.prompt,
                images=request.images,
                stream=False
            )
            
            return AskResponse(
                content=content,
                chat_id=client.chat_id,
                success=True
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/history/{chat_id}")
async def get_chat_history(
    chat_id: str,
    agent_id: Optional[str] = None,
    auth_key: Optional[str] = None,
    auth_secret: Optional[str] = None,
    jwt_token: Optional[str] = None,
    base_url: Optional[str] = None
):
    """获取对话历史"""
    try:
        # 构建配置
        config = DEFAULT_CONFIG.copy()
        if agent_id:
            config["agent_id"] = agent_id
        if auth_key:
            config["auth_key"] = auth_key
        if auth_secret:
            config["auth_secret"] = auth_secret
        if jwt_token:
            config["jwt_token"] = jwt_token
        if base_url:
            config["base_url"] = base_url

        # 创建客户端
        client = create_client(config)
        
        # 获取历史记录
        history = client.get_chat_history(chat_id)
        
        return {"history": history, "chat_id": chat_id, "success": True}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 