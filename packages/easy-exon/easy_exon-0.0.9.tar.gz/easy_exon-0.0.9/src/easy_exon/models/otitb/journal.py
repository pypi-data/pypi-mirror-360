from typing import List, Optional
from pydantic import BaseModel


class JournalElementModel(BaseModel):
    id: str

    name: Optional[str] = None
    documentType: Optional[str] = None
    documentNumber: Optional[str] = None
    organizationId: Optional[str] = None
    projectId: Optional[str] = None
    organizationShortName: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    pageUpdatePeriod: Optional[int] = None
    documentFileId: Optional[str] = None
    verified: Optional[bool] = None
    archived: Optional[bool] = None
    createdBy: Optional[str] = None
    createdAt: Optional[str] = None
    journalElementIds: Optional[List[str]] = None
    orgId: Optional[str] = None
    indicatorForFilter: Optional[bool] = None
    userId: Optional[str] = None

    class Config:
        extra = "allow"
