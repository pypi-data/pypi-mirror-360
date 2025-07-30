from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class WorkExtraModel(BaseModel):
    id: str
    
    name: Optional[str] = None
    version: Optional[int] = None

    documentFileId: Optional[str] = None
    editableDocumentFileIds: List[str] = Field(default_factory=list)
    supportDocumentFileIds: List[str] = Field(default_factory=list)

    organizationId: Optional[str] = None
    projectId: Optional[str] = None
    responsibleEmployeeUserId: Optional[str] = None
    createdBy: Optional[str] = None

    sectionId: Optional[str] = None
    sectionName: Optional[str] = ""
    subsectionName: Optional[str] = ""

    cipher: Optional[str] = ""
    note: Optional[str] = ""
    delay: int = 0
    numberPages: int = 0

    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
        alias_generator = lambda s: s
        populate_by_name = True