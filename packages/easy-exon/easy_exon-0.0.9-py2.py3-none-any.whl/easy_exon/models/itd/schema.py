from typing import List, Optional, Any
from pydantic import BaseModel

from .common import SupportDocumentModel


class ActualVolumeModel(BaseModel):
    id: str
    name: Optional[str] = None
    value: Optional[str] = None
    unitMeasureName: Optional[str] = None
    source: Optional[str] = None
    isUsed: Optional[bool] = None

    class Config:
        extra = "allow"


class SignerModel(BaseModel):
    id: str
    orgId: Optional[str] = None

    class Config:
        extra = "allow"


class SchemaModel(BaseModel):
    id: str

    schemeName: Optional[str] = None
    fullSchemeName: Optional[str] = None
    sectionId: Optional[str] = None
    sectionName: Optional[str] = None
    userId: Optional[str] = None
    memberOrganizationId: Optional[str] = None
    currentExecutorId: Optional[str] = None
    currentExecutor: Optional[str] = None
    author: Optional[str] = None
    receiptDate: Optional[str] = None
    createdAt: Optional[str] = None
    supportDocuments: Optional[List[SupportDocumentModel]] = None
    projectId: Optional[str] = None
    pdfFileId: Optional[str] = None
    qrFileId: Optional[str] = None
    actualVolumes: Optional[List[ActualVolumeModel]] = None
    documentNumber: Optional[str] = None
    version: Optional[int] = None
    history: Optional[List[Any]] = None
    signers: Optional[List[SignerModel]] = None
    documentStatus: Optional[str] = None
    description: Optional[str] = None
    commentsCount: Optional[int] = None
    actual: Optional[bool] = None
    orgId: Optional[str] = None
    indicatorForFilter: Optional[bool] = None

    class Config:
        extra = "allow"
