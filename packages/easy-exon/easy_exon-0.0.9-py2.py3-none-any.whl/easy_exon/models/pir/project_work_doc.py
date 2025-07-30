from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class ProjectDocContentModel(BaseModel):
    id: str
    sectionId: Optional[str] = None
    changeSetId: Optional[str] = None
    createdAt: datetime
    status: Optional[str] = None
    cipher: Optional[str] = None
    change: Optional[int] = None
    version: Optional[int] = None

    documentFileId: Optional[str] = None
    name: Optional[str] = None
    sectionName: Optional[str] = None
    labelName: Optional[str] = None

    approvalDate: Optional[date] = None
    expectedApprovalDate: Optional[date] = None
    transferToClientDate: Optional[date] = None
    sendToWorkContractorDate: Optional[date] = None

    expertiseConclusionNumber: Optional[str] = None
    expertiseDate: Optional[date] = None
    expertOpinionId: Optional[str] = None

    projectId: Optional[str] = None
    qrFileId: Optional[str] = None
    xsdDocumentType: Optional[str] = None
    extension: Optional[str] = None

    remarkCount: Optional[int] = 0
    hasRequestChangeIndicator: bool = False
    needActionIndicator: bool = False
    needQrCodeIndicator: bool = False
    noteActionIndicator: bool = False
    toDelegateIndicator: bool = False

    responsibleEmployeeUserId: Optional[str] = None
    organizationId: Optional[str] = None
    initiatorUserId: Optional[str] = None
    initiatorOrganizationId: Optional[str] = None
    authorMemberId: Optional[str] = None
    authorMemberName: Optional[str] = None

    note: Optional[str] = ""
    exploItStatus: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        populate_by_name=True,
    )


class ProjectDocModel(BaseModel):
    content: List[ProjectDocContentModel]
    pageNum: Optional[int] = None
    pageCount: Optional[int] = None
    pageSize: Optional[int] = None
    totalSize: Optional[int] = None
