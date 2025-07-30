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