from autoagentsai.client import ChatClient
from io import BytesIO

client = ChatClient(
    agent_id="fe91cf3348bb419ba907b1e690143006",
    personal_auth_key="e7a964a7e754413a9ea4bc1395a38d39",
    personal_auth_secret="r4wBtqVD1qjItzQapJudKQPFozHAS9eb"
)

def local_ask_with_file(prompt: str, file_path: str):
    with open(file_path, "rb") as f:
        file_content = f.read()
    
    file_like = BytesIO(file_content)
    file_like.name = file_path.split("/")[-1]
    
    reply = client.invoke(
        prompt=prompt,
        files=[file_like]
    )
    
    for chunk in reply:
        print(chunk, end="", flush=True)

    print("\n=== History ===\n")
    print(client.history())

# 调用
local_ask_with_file("请总结文件内容", "每周AI信息Vol. 20250704.pdf")