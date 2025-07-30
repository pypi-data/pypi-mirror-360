from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from autoagentsai.client import ChatClient
import json

app = FastAPI()

client = ChatClient(
    agent_id="90b60436c09b43e5b6d05a31abf8c662",
    personal_auth_key="e7a964a7e754413a9ea4bc1395a38d39",
    personal_auth_secret="r4wBtqVD1qjItzQapJudKQPFozHAS9eb"
)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)