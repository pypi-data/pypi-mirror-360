import requests
import json
import os
import mimetypes
from typing import Optional, Dict, Union, IO, List
from .models import FileInput


class FileUploader:
    def __init__(self, jwt_token: str, base_url: str = "https://uat.agentspro.cn"):
        self.jwt_token = jwt_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {jwt_token}"
        }

    def upload(self, file: IO, filename: str = "uploaded_file") -> Dict:
        """上传文件并返回文件信息字典"""
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
        """将 file-like 对象自动上传为 FileInput，字符串作为 fileId 创建 FileInput"""
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
