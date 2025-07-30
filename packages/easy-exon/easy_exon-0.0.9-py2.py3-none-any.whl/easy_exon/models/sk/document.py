from typing import List, Optional, Any

from pydantic import BaseModel, Field

from .common import UserPreview, FileAttachment


class SignerInfoModel(BaseModel):
    userId: str = Field(..., min_length=1)
    firstName: Optional[str] = None
    middleName: Optional[str] = None
    lastName: Optional[str] = None
    organizationId: Optional[str] = None
    organizationName: Optional[str] = None
    position: Optional[str] = None
    viewedAt: Optional[int] = None
    emailAddress: Optional[str] = None
    attributes: Optional[Any] = None
    status: Optional[str] = None
    organizationMemberId: Optional[str] = None
    changeStatusDate: Optional[int] = None

    class Config:
        extra = "allow"


class ActActionModel(BaseModel):
    documentId: int
    actionType: str
    user: UserPreview
    targetUser: Optional[Any] = None
    actionDate: int
    type: Optional[str] = None
    displayText: Optional[str] = None

    class Config:
        extra = "allow"


class ActDocumentModel(BaseModel):
    id: int

    projectId: Optional[str] = None
    registryId: Optional[str] = None
    executorId: Optional[str] = None
    executorUser: Optional[UserPreview] = None

    documentType: Optional[str] = None
    actNumber: Optional[str] = None
    actDate: Optional[int] = None
    creationDate: Optional[int] = None
    status: Optional[str] = None

    authorUserId: Optional[str] = None
    authorUser: Optional[UserPreview] = None

    signerIds: Optional[List[str]] = None
    signers: Optional[List[SignerInfoModel]] = None
    actActions: Optional[List[ActActionModel]] = None

    documentTemplate: Optional[str] = None
    fileAttachment: Optional[FileAttachment] = None

    createdFromBus: Optional[bool] = None
    attentionIndicator: Optional[Any] = None
    remarkIds: Optional[List[int]] = None
    remarkNumbers: Optional[List[str]] = None

    class Config:
        extra = "allow"
