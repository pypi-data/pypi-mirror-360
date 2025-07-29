import requests
import json
import os
from typing import Optional, Dict, Union, IO


class FileUploader:
    def __init__(self, auth_key: str, auth_secret: str, base_url: str = "https://uat.agentspro.cn"):
        self.auth_key = auth_key
        self.auth_secret = auth_secret
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {auth_key}.{auth_secret}"
        }

    def upload(self, file: IO, filename: str = "uploaded_file") -> str:
        """上传文件并返回 file_id"""
        url = f"{self.base_url}/openapi/fs/upload"
        
        files = {
            'file': (filename, file)
        }
        
        try:
            response = requests.post(url, headers=self.headers, files=files, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get('fileId', '')
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
            res = response.json()
            if res.get("code") == 1:
                return res["data"]
            else:
                raise Exception(f"上传失败: {res.get('msg')}")
        finally:
            if close_after:
                f.close()
