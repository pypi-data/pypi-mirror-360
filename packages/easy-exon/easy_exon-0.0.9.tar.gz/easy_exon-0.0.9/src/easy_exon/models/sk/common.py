from typing import Optional

from pydantic import BaseModel


class UserPreview(BaseModel):
    id: str
    firstName: Optional[str] = None
    middleName: Optional[str] = None
    lastName: Optional[str] = None
    organizationId: Optional[str] = None
    organizationName: Optional[str] = None
    position: Optional[str] = None
    viewedAt: Optional[str] = None

    class Config:
        extra = "allow"


class PirCipher(BaseModel):
    cipher: str
    cipherType: Optional[str] = None
    sectionName: Optional[str] = None
    name: Optional[str] = None
    fileId: Optional[str] = None
    change: Optional[int] = None
    status: Optional[str] = None
    initiatorOrganizationId: Optional[str] = None
    initiatorUserId: Optional[str] = None
    documentId: Optional[str] = None

    class Config:
        extra = "allow"


class FileAttachment(BaseModel):
    type: str
    name: str
    link: str
    qrFileId: Optional[str] = None
    version: Optional[str] = None
    change: Optional[str] = None
    signed: Optional[bool] = None

    class Config:
        extra = "allow"
