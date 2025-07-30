from typing import List, Optional, Any
from pydantic import BaseModel


class WorkDocumentModel(BaseModel):
    fileId: str

    documentName: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    workDocumentId: Optional[str] = None
    workDocumentOriginalFileId: Optional[str] = None
    change: Optional[int] = None
    vprDate: Optional[str] = None
    cipher: Optional[str] = None
    numberList: Optional[str] = None
    absoluteNumberList: Optional[str] = None
    fullDocumentName: Optional[str] = None
    shouldAddTitlePages: Optional[bool] = None
    startPage: Optional[int] = None
    isAllPagesSelected: Optional[bool] = None
    authorWorkDoc: Optional[str] = None
    isCustomPagesList: Optional[bool] = None

    class Config:
        extra = "allow"


class WorkJournalEntryModel(BaseModel):
    id: str

    itdTaskId: Optional[str] = None
    itdSectionId: Optional[str] = None
    workTypeId: Optional[str] = None
    projectDoc: Optional[str] = None
    userId: Optional[str] = None
    description: Optional[str] = None
    workDocuments: Optional[List[WorkDocumentModel]] = None

    number: Optional[int] = None
    startDate: Optional[str] = None
    organisationId: Optional[str] = None
    isActual: Optional[bool] = None
    history: Optional[List[Any]] = None

    class Config:
        extra = "allow"
