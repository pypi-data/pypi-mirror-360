import requests
import json
import os
import mimetypes
from typing import Optional, Dict, Union, IO, List
from .models import FileInput


class FileUploader:
    def __init__(self, jwt_token: str, base_url: str = "https://uat.agentspro.cn"):
        """
        AutoAgents AI 文件上传器
        
        负责将本地文件上传到 AutoAgents 平台，并获取文件 ID 用于后续的对话引用。
        支持多种文件类型的自动识别和上传。
        
        Args:
            jwt_token (str): JWT 认证令牌
                - 必填参数，用于 API 认证
                - 通过 get_jwt_token_api() 函数获取
                - 格式：JWT 标准格式的字符串
                - 示例: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                
            base_url (str, optional): API 服务基础地址
                - 可选参数，默认为 "https://uat.agentspro.cn"  
                - 测试环境: "https://uat.agentspro.cn"
                - 生产环境: "https://agentspro.cn"
                - 私有部署时可指定自定义地址
                
        示例:
            >>> uploader = FileUploader(
            ...     jwt_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            ...     base_url="https://uat.agentspro.cn"
            ... )
        """
        self.jwt_token = jwt_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {jwt_token}"
        }

    def upload(self, file: IO, filename: str = "uploaded_file") -> Dict:
        """
        上传单个文件到 AutoAgents 平台
        
        将文件对象上传到平台并获取文件 ID，用于后续在对话中引用该文件。
        自动检测文件类型并设置正确的 MIME 类型。
        
        Args:
            file (IO): 文件对象
                - 必填参数，要上传的文件对象
                - 支持类型：
                  - 文件句柄：open("file.txt", "rb")
                  - 字节流：BytesIO 对象
                  - 任何实现了 read() 方法的类文件对象
                - 文件必须以二进制模式打开（"rb"）
                
            filename (str, optional): 文件名
                - 可选参数，默认为 "uploaded_file"
                - 用于文件类型识别和显示
                - 应包含正确的文件扩展名
                - 示例: "document.pdf", "data.xlsx", "image.png"
                
        Returns:
            Dict: 上传结果字典
                成功时包含:
                - fileId (str): 平台生成的文件唯一标识符
                - fileName (str): 文件名
                - fileType (str): MIME 类型，如 "application/pdf"
                - fileUrl (str): 文件 URL（当前为空字符串）
                - success (bool): True 表示上传成功
                
                失败时包含:
                - fileId (str): 空字符串
                - fileName (str): 原文件名
                - fileType (str): 检测到的 MIME 类型
                - fileUrl (str): 空字符串
                - success (bool): False 表示上传失败
                - error (str): 错误信息
                
        支持的文件类型:
            - 文档类：PDF, DOC, DOCX, TXT, RTF
            - 表格类：XLS, XLSX, CSV
            - 演示类：PPT, PPTX
            - 图片类：JPEG, PNG, GIF, BMP, WebP
            - 其他类型会被识别为 "application/octet-stream"
            
        示例:
            >>> uploader = FileUploader(jwt_token="xxx")
            >>> 
            >>> # 上传本地文件
            >>> with open("report.pdf", "rb") as f:
            ...     result = uploader.upload(f, "report.pdf")
            ...     if result["success"]:
            ...         print(f"文件上传成功，ID: {result['fileId']}")
            ...     else:
            ...         print(f"上传失败: {result['error']}")
            
            >>> # 上传内存中的文件
            >>> from io import BytesIO
            >>> file_content = BytesIO(b"Hello, World!")
            >>> result = uploader.upload(file_content, "hello.txt")
            
        异常:
            Exception: 当上传过程中发生网络错误或 API 错误时抛出
        """
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
        """
        将文件列表转换为 FileInput 对象列表
        
        处理混合类型的文件列表，自动上传文件对象并转换为平台可识别的 FileInput 格式。
        支持文件路径字符串和文件对象的混合输入。
        
        Args:
            files (List[Union[str, IO]], optional): 文件列表
                - 可选参数，默认为 None
                - 支持两种元素类型：
                  1. 字符串 (str): 已存在的文件 ID
                     - 格式：24位十六进制字符串
                     - 示例: "507f1f77bcf86cd799439011"
                     - 用于引用已上传的文件
                  
                  2. 文件对象 (IO): 需要上传的文件
                     - 文件句柄：open("file.txt", "rb") 
                     - 字节流：BytesIO 对象
                     - 其他类文件对象
                     - 必须可读取（支持 read() 方法）
                     
                - 可以混合使用两种类型
                - 示例: ["507f1f77bcf86cd799439011", open("new.pdf", "rb")]
                
        Returns:
            List[FileInput]: FileInput 对象列表
                - 每个 FileInput 包含：
                  - fileId (str): 文件唯一标识符
                  - fileName (str): 文件名
                  - fileType (str): MIME 类型
                  - fileUrl (str): 文件 URL
                  - groupName (str): 文件组名（默认为空）
                  - dsId (int): 数据源 ID（默认为 0）
                
        文件名获取规则:
            1. 优先使用 file.filename 属性
            2. 其次使用 file.name 属性
            3. 如果是路径，提取文件名部分
            4. 默认为 "uploaded_file"
            
        示例:
            >>> uploader = FileUploader(jwt_token="xxx")
            >>> 
            >>> # 混合类型文件列表
            >>> files = [
            ...     "507f1f77bcf86cd799439011",  # 已存在的文件 ID
            ...     open("report.pdf", "rb"),    # 新文件
            ...     BytesIO(b"content")           # 内存文件
            ... ]
            >>> file_inputs = uploader.ensure_file_inputs(files)
            >>> print(f"转换了 {len(file_inputs)} 个文件")
            
            >>> # 空列表处理
            >>> empty_inputs = uploader.ensure_file_inputs([])
            >>> print(empty_inputs)  # []
            
            >>> # None 处理
            >>> none_inputs = uploader.ensure_file_inputs(None)
            >>> print(none_inputs)  # []
            
        注意:
            - 文件上传失败时会打印警告信息但不会中断处理
            - 返回的列表只包含成功处理的文件
            - 对于文件 ID 字符串，不会验证其有效性
        """
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
