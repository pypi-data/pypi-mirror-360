from autoagentsai.client import ChatClient

client = ChatClient(
    agent_id="90b60436c09b43e5b6d05a31abf8c662",
    personal_auth_key="e7a964a7e754413a9ea4bc1395a38d39",
    personal_auth_secret="r4wBtqVD1qjItzQapJudKQPFozHAS9eb"
)

for event in client.invoke(prompt="人工智能的历史"):
    if event['type'] == 'start_bubble':
        print(f"\n{'=' * 20} 消息气泡{event['bubble_id']}开始 {'=' * 20}")
    elif event['type'] == 'reasoning_token':
        print(event['content'], end='', flush=True)
    elif event['type'] == 'token':
        print(event['content'], end='', flush=True)
    elif event['type'] == 'end_bubble':
        print(f"\n{'=' * 20} 消息气泡结束 {'=' * 20}")
    elif event['type'] == 'finish':
        print(f"\n{'=' * 20} 对话完成 {'=' * 20}")
        break

print(client.history())