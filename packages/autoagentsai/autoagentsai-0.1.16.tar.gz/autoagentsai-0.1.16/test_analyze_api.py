import requests
import time

def test_analyze_api():
    """测试 FastAPI analyze 接口"""
    
    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(3)
    
    # 检查服务器是否运行
    try:
        response = requests.get("http://localhost:8000/docs")
        print(f"✅ 服务器启动成功，状态码: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ 服务器未启动，请检查 FastAPI 应用是否正在运行")
        return
    
    # 创建一个测试文件
    test_content = """
    这是一个测试文档。
    
    主要内容包括：
    1. 文档分析测试
    2. 人工智能处理能力验证
    3. SDK 功能测试
    
    测试目标：验证文件上传和分析功能是否正常工作。
    """
    
    # 准备文件上传
    files = {
        'file': ('test_document.txt', test_content.encode('utf-8'), 'text/plain')
    }
    
    print("\n🚀 开始测试文件分析接口...")
    print(f"📄 测试文件: test_document.txt")
    print(f"📏 文件大小: {len(test_content.encode('utf-8'))} 字节")
    
    try:
        # 发送请求到 analyze 接口
        response = requests.post(
            "http://localhost:8000/analyze",
            files=files,
            timeout=60  # 增加超时时间，因为 AI 分析可能需要时间
        )
        
        print(f"\n📡 请求状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 请求成功！")
            print(f"📄 AI 分析结果:")
            print("-" * 50)
            print(result.get('response', '无响应内容'))
            print("-" * 50)
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print(f"📄 错误信息: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ 请求超时，AI 分析可能需要更长时间")
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {str(e)}")
    except Exception as e:
        print(f"❌ 其他错误: {str(e)}")

def test_with_pdf_file():
    """使用 PDF 文件测试（如果存在）"""
    import os
    
    # 检查是否有 PDF 文件可以测试
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    if not pdf_files:
        print("\n📄 没有找到 PDF 文件进行测试")
        return
    
    pdf_file = pdf_files[0]
    print(f"\n🔍 使用 PDF 文件进行测试: {pdf_file}")
    
    try:
        with open(pdf_file, 'rb') as f:
            files = {
                'file': (pdf_file, f.read(), 'application/pdf')
            }
            
        response = requests.post(
            "http://localhost:8000/analyze",
            files=files,
            timeout=120  # PDF 分析可能需要更长时间
        )
        
        print(f"📡 PDF 测试状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ PDF 分析成功！")
            print(f"📄 分析结果:")
            print("-" * 50)
            print(result.get('response', '无响应内容'))
            print("-" * 50)
        else:
            print(f"❌ PDF 分析失败: {response.text}")
            
    except Exception as e:
        print(f"❌ PDF 测试错误: {str(e)}")

if __name__ == "__main__":
    print("🧪 开始测试 AutoAgents AI FastAPI 接口")
    print("=" * 60)
    
    # 测试文本文件
    test_analyze_api()
    
    # 测试 PDF 文件（如果有）
    test_with_pdf_file()
    
    print("\n" + "=" * 60)
    print("🏁 测试完成") 