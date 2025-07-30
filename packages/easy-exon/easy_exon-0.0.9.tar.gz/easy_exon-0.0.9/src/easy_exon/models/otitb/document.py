from typing import List, Optional
from pydantic import BaseModel


class DocumentModel(BaseModel):
    id: str
    documentType: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    organizationId: Optional[str] = None
    orgShortName: Optional[str] = None
    signDate: Optional[str] = None
    documentNumber: Optional[str] = None
    documentStartDate: Optional[str] = None
    documentEndDate: Optional[str] = None
    startWorkDate: Optional[str] = None
    endWorkDate: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    pageUpdatePeriod: Optional[int] = None
    projectId: Optional[str] = None
    documentFileId: Optional[str] = None
    author: Optional[str] = None
    relevant: Optional[bool] = None
    archived: Optional[bool] = None
    verified: Optional[bool] = None
    createdBy: Optional[str] = None
    createdAt: Optional[str] = None
    participants: Optional[List[dict]] = None
    orgId: Optional[str] = None
    userId: Optional[str] = None
    indicatorForFilter: Optional[bool] = None

    class Config:
        extra = "allow"
