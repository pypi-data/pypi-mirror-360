#!/usr/bin/env python3
"""
FastAPI 服务器启动脚本
"""
import uvicorn
import os

def main():
    """启动FastAPI服务器"""
    # 从环境变量获取配置，或使用默认值
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"🚀 启动AutoAgents AI API服务器...")
    print(f"📡 地址: http://{host}:{port}")
    print(f"📚 API文档: http://{host}:{port}/docs")
    print(f"🔄 自动重载: {'开启' if reload else '关闭'}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        access_log=True
    )

if __name__ == "__main__":
    main() 