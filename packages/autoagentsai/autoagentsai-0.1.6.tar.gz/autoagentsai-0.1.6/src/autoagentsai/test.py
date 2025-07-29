from autoagentsai.client import ChatClient

if __name__ == "__main__":
    client = ChatClient(
        agent_id="fe91cf3348bb419ba907b1e690143006",
        auth_key="fe91cf3348bb419ba907b1e690143006",
        auth_secret="mLin0asZ7YRRRxI6Cpwb8hxqZ2N9Wf4X",
        jwt_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )

    # 测试文件 + 非流式调用
    print("=== Testing file + non-stream invoke ===")
    try:
        with open("example.pdf", "rb") as f:  # 👈 替换为你的实际测试文件路径
            result = client.invoke(
                prompt="请帮我分析这份文件内容",
                files=[f],  # 自动上传为 fileId
                stream=False
            )
            print("智能体回复:", result)
    except FileNotFoundError:
        print("❌ 未找到测试文件 example.pdf，请将测试文件放在项目根目录。")

    print("\n=== Testing normal invoke with stream=True ===")
    for chunk in client.invoke("你好", stream=True):
        print(chunk, end="", flush=True)

    print("\n=== Testing follow-up ===")
    for chunk in client.invoke("请重复我刚才说的", stream=True):
        print(chunk, end="", flush=True)

    print("\n=== Testing history ===")
    history = client.history()
    print(history)
