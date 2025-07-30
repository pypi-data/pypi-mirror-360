from autoagentsai.client import ChatClient

client = ChatClient(
    agent_id="fe91cf3348bb419ba907b1e690143006",
    auth_key="fe91cf3348bb419ba907b1e690143006",
    auth_secret="mLin0asZ7YRRRxI6Cpwb8hxqZ2N9Wf4X",
    jwt_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiL01Nd1ZDYlRZY2dHWUtCOE1NSVo4dVFHN05BYXYrRlR6Szl3bEQ4bWU0UjQzUldVa2JlWC9CS1VkM3N3ck9ZQmMvYnlUMDc1YzhwRVUzbDdwZ3BGc0l5b0p4L3ZRdXdzS0ozMTZqd0V5RTVBTXFBUXFzcjRwWXF3OHk2WU9PY2dpbVhuenJqOWVOV01hc2tqOFc2b2l3RUFza1pxTUlWUVN6NUxsdE14WHMvV0lGaW1zYjF5RTdpdmR0WGszR0svdHBlTXA1cWdGKzErVGFBNkx1ZDZLK2V0UGQwWkRtWE8vMEZJNGtDaC9zST0iLCJleHAiOjE3NTQxMjk1MzR9.96Q5LOMf8Ve4GCxuOeMW7zISnksGKVLI0UduXQ8RbH8"
)

# 测试非流式调用
print("=== Testing non-stream response ===")
result = client.invoke("你好", stream=False)
print(f"Non-stream result: {result}")
print(f"Non-stream result type: {type(result)}")
print()

# 测试流式调用
print("=== Testing stream response ===")
stream_result = ""
for chunk in client.invoke("你好", stream=True):
    stream_result += chunk
    print(chunk, end="", flush=True)
print()
print(f"Stream result: {stream_result}")
print(f"Stream result type: {type(stream_result)}")
print()

print("=== History ===")
print(client.history())