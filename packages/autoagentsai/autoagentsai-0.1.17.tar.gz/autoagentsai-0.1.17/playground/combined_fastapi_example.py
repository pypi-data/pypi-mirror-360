from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from autoagentsai.client import ChatClient
from autoagentsai.uploader import create_file_like
import json
import uvicorn
from typing import Optional

app = FastAPI()

# --- 配置您的认证信息 ---
client = ChatClient(
    agent_id="your_agent_id",
    personal_auth_key="your_auth_key", 
    personal_auth_secret="your_auth_secret"
)
# --------------------

@app.post("/combined-chat")
async def combined_chat_stream(prompt: str = Form(...), file: Optional[UploadFile] = File(None)):
    """
    结合了多气泡和打字机效果的终极流式接口
    """
    
    files = None
    if file:
        content = await file.read()
        file_obj = create_file_like(file_input=content, filename=file.filename)
        files = [file_obj]
    
    def generate():
        # invoke 方法现在默认就是事件模式，无需指定 stream_mode
        for event in client.invoke(prompt, files=files):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

# 挂载 static 目录，用于提供前端 HTML 文件
app.mount("/static", StaticFiles(directory="playground/static"), name="static")

@app.get("/")
async def index():
    return {
        "message": "AutoAgents AI - 组合流式演示",
        "demo_url": "http://localhost:8000/static/combined_frontend.html"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 