import requests
import json
import os
import mimetypes
from typing import Optional, Dict, Union, IO, List
from io import BytesIO
from .models import FileInput


class FileUploader:
    def __init__(self, jwt_token: str, base_url: str = "https://uat.agentspro.cn"):
        """
        AutoAgents AI 文件上传器
        
        负责将本地文件上传到 AutoAgents 平台，并获取文件 ID 用于后续的对话引用。
        支持多种文件类型的自动识别和上传。
        
        Args:
            jwt_token (str): JWT 认证令牌
                
            base_url (str, optional): API 服务基础地址
                - 可选参数，默认为 "https://uat.agentspro.cn"  
                - 测试环境: "https://uat.agentspro.cn"
                - 生产环境: "https://agentspro.cn"
                - 私有部署时可指定自定义地址
        """
        self.jwt_token = jwt_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {jwt_token}"
        }

    def upload(self, file: IO, filename: str = "uploaded_file") -> Dict:
        url = f"{self.base_url}/api/fs/upload"
        
        # 根据文件扩展名自动检测MIME类型
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type is None:
            mime_type = 'application/octet-stream'  # 默认类型
        
        print(f"Debug: 上传文件 {filename}, 检测到MIME类型: {mime_type}")
        
        files = [
            ('file', (filename, file, mime_type))
        ]
        
        payload = {}
        
        try:
            response = requests.post(url, headers=self.headers, data=payload, files=files, timeout=30)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('code') == 1:  # 成功
                        file_id = result["data"]
                        return {
                            "fileId": file_id,
                            "fileName": filename,
                            "fileType": mime_type,
                            "fileUrl": "",  # 当前API不返回URL
                            "success": True
                        }
                    else:  # 失败
                        error_msg = result.get('msg', '未知错误')
                        raise Exception(f"API返回错误: {error_msg}")
                        
                except Exception as e:
                    # 如果不是JSON响应，返回错误信息字典
                    print(f"Debug: 非JSON响应，返回原始文本: {response.text}")
                    return {
                        "fileId": "",
                        "fileName": filename,
                        "fileType": mime_type,
                        "fileUrl": "",
                        "success": False,
                        "error": response.text.strip()
                    }
            else:
                raise Exception(f"Upload failed: {response.status_code} - {response.text}")
        except Exception as e:
            raise Exception(f"File upload error: {str(e)}")

    def ensure_file_inputs(self, files: Optional[List[Union[str, IO]]] = None) -> List[FileInput]:
        file_inputs = []
        if not files:
            return file_inputs

        for f in files:
            if isinstance(f, str):
                # 如果是字符串，假设它是 fileId，创建一个基本的 FileInput
                file_inputs.append(FileInput(
                    fileId=f,
                    fileName="",  # 无法从 fileId 推断文件名
                    fileType="",
                    fileUrl=""
                ))
            else:
                # 尝试获取文件名，优先使用 filename 属性，然后是 name 属性
                filename = getattr(f, "filename", None)
                if filename is None:
                    filename = getattr(f, "name", "uploaded_file")
                    if filename != "uploaded_file":
                        # 从完整路径中提取文件名
                        filename = os.path.basename(filename)
                
                upload_result = self.upload(f, filename=filename)
                print(f"Debug: 上传文件 {filename}, 结果: {upload_result}")
                
                if upload_result.get("success", False):
                    file_inputs.append(FileInput(
                        fileId=upload_result["fileId"],
                        fileName=upload_result["fileName"],
                        fileType=upload_result["fileType"],
                        fileUrl=upload_result["fileUrl"]
                    ))
                else:
                    # 上传失败，但仍创建一个 FileInput 对象以保持一致性
                    print(f"Warning: 文件上传失败: {upload_result.get('error', '未知错误')}")

        return file_inputs


def create_file_like(file_input, filename: Optional[str] = None):
    # 处理不同类型的输入
    if isinstance(file_input, str):
        # 文件路径
        with open(file_input, "rb") as f:
            file_content = f.read()
        
        file_like = BytesIO(file_content)
        file_like.name = file_input.split("/")[-1]
        return file_like
        
    elif isinstance(file_input, bytes):
        # 原始字节数据
        file_like = BytesIO(file_input)
        file_like.name = filename or "uploaded_file"
        return file_like
        
    elif isinstance(file_input, BytesIO):
        # 已经是 BytesIO 对象
        if not hasattr(file_input, 'name') or not file_input.name:
            file_input.name = filename or "uploaded_file"
        return file_input
        
    elif hasattr(file_input, 'read'):
        # 文件对象或类文件对象（包括前端上传的文件）
        try:
            # 尝试读取内容
            content = file_input.read()
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            file_like = BytesIO(content)
            
            # 确定文件名的优先级
            if filename:
                file_like.name = filename
            elif hasattr(file_input, 'filename') and file_input.filename:
                file_like.name = file_input.filename
            elif hasattr(file_input, 'name') and file_input.name:
                file_like.name = os.path.basename(file_input.name)
            else:
                file_like.name = "uploaded_file"
                
            return file_like
            
        except Exception as e:
            raise ValueError(f"无法读取文件对象: {str(e)}")
            
    else:
        raise TypeError(f"不支持的文件输入类型: {type(file_input)}")
