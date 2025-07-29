from autoagentsai import AutoAgentsClient

client = AutoAgentsClient(
    agent_id="3eea63c71173463580e223e0d565340e",
    auth_key="3eea63c71173463580e223e0d565340e",
    auth_secret="rTjIkV3OjJIfwtp7j0Fa2m6YmCsLvyXr",
)

print(client.invoke("你好"))
print(client.invoke("请重复我刚才说的"))
print(client.invoke("请告诉我之前都说过什么"))
print(client.history())