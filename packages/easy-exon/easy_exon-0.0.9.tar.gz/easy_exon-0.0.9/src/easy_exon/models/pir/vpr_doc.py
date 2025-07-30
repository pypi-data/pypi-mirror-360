from datetime import datetime, date
from typing import List, Optional

from pydantic import BaseModel, Field


class VPRDocModel(BaseModel):
    id: str

    change: Optional[int] = None
    version: Optional[int] = None
    status: Optional[str] = None

    createdAt: datetime
    updatedAt: Optional[datetime] = None
    actionDate: Optional[date] = None
    expectedApprovalDate: Optional[date] = None
    approvalDate: Optional[date] = None
    sendToWorkContractorDate: Optional[date] = None
    transferToClientDate: Optional[date] = None
    transferForReworkDate: Optional[date] = None
    vprExactDate: Optional[date] = None

    name: Optional[str] = None
    cipher: Optional[str] = None
    documentFileId: Optional[str] = None
    vprForPrintFileId: Optional[str] = None
    editableDocumentFileIds: List[str] = Field(default_factory=list)
    supportDocumentFileIds: List[str] = Field(default_factory=list)

    firstPageNumber: Optional[int] = None
    numberPages: Optional[int] = None
    delay: Optional[int] = 0
    isAddedAsVpr: bool = False
    designerRemarks: bool = False
    sendGenContractor: bool = False

    organizationId: Optional[str] = None
    initiatorOrganizationId: Optional[str] = None
    responsibleEmployeeUserId: Optional[str] = None
    initiatorUserId: Optional[str] = None
    authorMemberId: Optional[str] = None
    projectId: Optional[str] = None
    sectionId: Optional[str] = None

    sectionName: Optional[str] = None
    subsectionName: Optional[str] = None
    qrFileId: Optional[str] = None
    qrHash: Optional[str] = None
    note: str = ""

    class Config:
        from_attributes = True
        alias_generator = lambda s: s
        validate_by_name = True
