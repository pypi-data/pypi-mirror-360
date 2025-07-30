# src/autoagentsai/types.py
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class ImageInput(BaseModel):
    url: str


class FileInput(BaseModel):
    groupName: str = ""
    dsId: int = 0
    fileId: str
    fileName: str
    fileUrl: str = ""
    fileType: str = ""


class ChatRequest(BaseModel):
    agentId: str
    chatId: Optional[str] = None
    userChatInput: str
    images: Optional[List[ImageInput]] = Field(default_factory=list)
    files: Optional[List[FileInput]] = Field(default_factory=list)
    state: Optional[Dict[str, str]] = Field(default_factory=dict)
    buttonKey: Optional[str] = ""
    debug: Optional[bool] = False

class ChatHistoryRequest(BaseModel):
    agentId: Optional[str] = None
    agentUUid: str
    chatId: str
    pageSize: int = 100
    pageNumber: int = 1