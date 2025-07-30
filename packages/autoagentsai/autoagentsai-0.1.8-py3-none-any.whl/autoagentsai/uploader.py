import requests
import json
import os
from typing import Optional, Dict, Union, IO


class FileUploader:
    def __init__(self, jwt_token: str, base_url: str = "https://uat.agentspro.cn"):
        self.jwt_token = jwt_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {jwt_token}"
        }

    def upload(self, file: IO, filename: str = "uploaded_file") -> str:
        """上传文件并返回 file_id"""
        url = f"{self.base_url}/api/fs/upload"
        
        files = [
            ('file', (filename, file, 'application/octet-stream'))
        ]
        
        payload = {}
        
        try:
            response = requests.post(url, headers=self.headers, data=payload, files=files, timeout=30)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('code') == 1:  # 成功
                        file_id = result["data"]
                        return file_id
                    else:  # 失败
                        error_msg = result.get('msg', '未知错误')
                        raise Exception(f"API返回错误: {error_msg}")
                        
                except Exception as e:
                    # 如果不是JSON响应，直接返回文本
                    print(f"Debug: 非JSON响应，返回原始文本: {response.text}")
                    return response.text.strip()
            else:
                raise Exception(f"Upload failed: {response.status_code} - {response.text}")
        except Exception as e:
            raise Exception(f"File upload error: {str(e)}")

    def upload_with_metadata(
        self,
        file: Union[str, IO],
        filename: Optional[str] = None,
        return_type: str = "id",
        metadata: Optional[Union[str, Dict]] = None
    ) -> str:
        """
        上传文件并返回 fileId 或 URL

        :param file: 本地文件路径(str) 或 file-like 对象（如 Flask 的 request.files["file"]）
        :param filename: 文件名（file 为文件对象时建议传）
        :param return_type: "id" 或 "url"，默认返回 fileId
        :param metadata: 附加的文件元数据（可以是 dict 或 JSON 字符串）
        :return: 平台返回的 fileId 或 URL 字符串
        """
        close_after = False

        # 判断是路径还是 file-like
        if isinstance(file, str):
            if not os.path.isfile(file):
                raise FileNotFoundError(f"文件不存在: {file}")
            f = open(file, "rb")
            _filename = filename or os.path.basename(file)
            close_after = True
        else:
            f = file
            _filename = filename or getattr(file, "filename", "uploaded_file")

        # 构建请求体
        files = {
            "file": (_filename, f)
        }
        data = {
            "returnType": return_type
        }
        if metadata:
            data["metadata"] = json.dumps(metadata) if isinstance(metadata, dict) else metadata

        try:
            response = requests.post(
                self.base_url + "/openapi/fs/upload",
                headers=self.headers,
                files=files,
                data=data,
                timeout=30
            )
            print(f"Debug: upload_with_metadata 响应状态码: {response.status_code}")
            print(f"Debug: upload_with_metadata 响应内容: {response.text}")
            
            if response.status_code == 200:
                res = response.json()
                print(f"Debug: upload_with_metadata 解析后的响应: {res}")
                
                if res.get("code") == 1:  # 成功
                    file_result = res.get("data", "")
                    print(f"Debug: upload_with_metadata 上传成功，返回: {file_result}")
                    return file_result
                else:  # 失败
                    error_msg = res.get('msg', '未知错误')
                    raise Exception(f"API返回错误: {error_msg}")
            else:
                raise Exception(f"HTTP错误: {response.status_code} - {response.text}")
        finally:
            if close_after:
                f.close()
