#!/usr/bin/env python3
"""
测试PDF文件上传和对话功能
"""

import sys
import os
# 确保使用本地版本而不是安装版本
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from autoagentsai.client import ChatClient

def test_pdf_upload_and_chat():
    """测试PDF文件上传和对话功能"""
    
    # 初始化客户端
    client = ChatClient(
        agent_id="fe91cf3348bb419ba907b1e690143006",
        auth_key="fe91cf3348bb419ba907b1e690143006",
        auth_secret="mLin0asZ7YRRRxI6Cpwb8hxqZ2N9Wf4X",
        jwt_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiL01Nd1ZDYlRZY2dHWUtCOE1NSVo4dVFHN05BYXYrRlR6Szl3bEQ4bWU0UjQzUldVa2JlWC9CS1VkM3N3ck9ZQmMvYnlUMDc1YzhwRVUzbDdwZ3BGc0l5b0p4L3ZRdXdzS0ozMTZqd0V5RTVBTXFBUXFzcjRwWXF3OHk2WU9PY2dpbVhuenJqOWVOV01hc2tqOFc2b2l3RUFza1pxTUlWUVN6NUxsdE14WHMvV0lGaW1zYjF5RTdpdmR0WGszR0svdHBlTXA1cWdGKzErVGFBNkx1ZDZLK2V0UGQwWkRtWE8vMEZJNGtDaC9zST0iLCJleHAiOjE3NTQxMjk1MzR9.96Q5LOMf8Ve4GCxuOeMW7zISnksGKVLI0UduXQ8RbH8"
    )
    
    pdf_path = "每周AI信息Vol. 20250704.pdf"
    
    # 检查PDF文件是否存在
    if not os.path.exists(pdf_path):
        print(f"❌ PDF文件不存在: {pdf_path}")
        return
    
    print(f"📁 找到PDF文件: {pdf_path}")
    print(f"📊 文件大小: {os.path.getsize(pdf_path) / 1024 / 1024:.2f} MB")
    print()
    
    try:
        # 测试1: 非流式PDF上传对话
        print("🧪 测试1: 非流式PDF上传对话")
        print("=" * 50)
        
        with open(pdf_path, "rb") as f:
            result = client.invoke(
                prompt="请分析这个PDF文件的内容，简要总结主要信息",
                files=[f],
                stream=False
            )
            print(f"✅ 非流式结果: {result}")
        print()
        
        # 测试2: 流式PDF上传对话
        print("🧪 测试2: 流式PDF上传对话")
        print("=" * 50)
        print("💬 AI回复: ", end="", flush=True)
        
        with open(pdf_path, "rb") as f:
            for chunk in client.invoke(
                prompt="请详细分析这个PDF中提到的AI技术趋势",
                files=[f],
                stream=True
            ):
                print(chunk, end="", flush=True)
        print("\n")
        
        # 测试3: 基于上下文的流式对话（不上传文件）
        print("🧪 测试3: 基于上下文的流式对话")
        print("=" * 50)
        print("💬 AI回复: ", end="", flush=True)
        
        for chunk in client.invoke(
            prompt="刚才PDF中最有趣的技术是什么？",
            stream=True
        ):
            print(chunk, end="", flush=True)
        print("\n")
        
        # 测试4: 非流式上下文对话
        print("🧪 测试4: 非流式上下文对话")
        print("=" * 50)
        
        result = client.invoke(
            prompt="请总结一下我们刚才讨论的内容",
            stream=False
        )
        print(f"✅ 总结结果: {result}")
        print()
        
        # 测试5: 历史记录查看
        print("🧪 测试5: 对话历史记录")
        print("=" * 50)
        
        history = client.history()
        if history:
            print(f"📜 共有 {len(history)} 条历史记录:")
            for i, msg in enumerate(history[-3:], 1):  # 只显示最后3条
                role = "🧑‍💻 用户" if msg["role"] == "user" else "🤖 助手"
                content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                print(f"{i}. {role}: {content}")
        else:
            print("❌ 没有找到历史记录")
        print()
        
        print("🎉 所有测试完成!")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 开始PDF文件上传和对话测试")
    print("=" * 60)
    test_pdf_upload_and_chat() 