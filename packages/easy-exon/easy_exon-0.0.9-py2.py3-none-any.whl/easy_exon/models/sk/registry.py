from typing import List, Optional
from pydantic import BaseModel

from .common import UserPreview, FileAttachment


class RegistryDocumentModel(BaseModel):
    id: int

    projectId: Optional[str] = None
    creationDate: Optional[int] = None
    updateDate: Optional[int] = None
    createdFromBus: Optional[bool] = None

    authorUserId: Optional[str] = None
    authorUserName: Optional[str] = None
    authorUser: Optional[UserPreview] = None

    attachment: Optional[FileAttachment] = None

    group: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    number: Optional[str] = None
    link: Optional[str] = None

    class Config:
        extra = "allow"


class RegistryResponseModel(BaseModel):
    code: Optional[str] = None
    result: Optional[List[RegistryDocumentModel]] = None
    page: Optional[int] = None
    pageSize: Optional[int] = None
    total: Optional[int] = None
    totalPages: Optional[int] = None

    class Config:
        extra = "allow"
