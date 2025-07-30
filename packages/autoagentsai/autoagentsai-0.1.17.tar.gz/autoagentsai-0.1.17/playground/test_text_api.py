from autoagentsai.client import ChatClient

client = ChatClient(
    agent_id="90b60436c09b43e5b6d05a31abf8c662",
    personal_auth_key="e7a964a7e754413a9ea4bc1395a38d39",
    personal_auth_secret="r4wBtqVD1qjItzQapJudKQPFozHAS9eb"
)

i = 1
for reply in client.invoke("人工智能的历史"):
    print(f"\n[第{i}个回复]: {reply}")
    i += 1