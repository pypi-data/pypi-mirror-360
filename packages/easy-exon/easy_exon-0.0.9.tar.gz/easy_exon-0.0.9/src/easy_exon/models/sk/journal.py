from typing import List, Optional, Any

from pydantic import BaseModel


class JournalModel(BaseModel):
    id: str

    number: Optional[int] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    element: Optional[str] = None
    location: Optional[str] = None
    nameWork: Optional[str] = None
    generalJournalIds: Optional[List[str]] = None
    signatureControl: Optional[Any] = None
    remarkId: Optional[int] = None
    numberRemark: Optional[int] = None
    remarkCreatedDate: Optional[str] = None
    numberPage: Optional[int] = None
    causes: Optional[List[str]] = None
    ciphers: Optional[List[str]] = None
    description: Optional[str] = None
    inspectionId: Optional[str] = None
    removalTerm: Optional[str] = None
    controlId: Optional[str] = None
    fullNameControl: Optional[str] = None
    violationsDate: Optional[str] = None
    executorId: Optional[str] = None
    fullNameExecutor: Optional[str] = None
    signatureCheckViolations: Optional[Any] = None
    projectId: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    class Config:
        extra = "allow"
