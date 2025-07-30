from typing import List, Optional

from pydantic import BaseModel, Field

from .common import UserPreview, PirCipher, FileAttachment


class RemarkLink(BaseModel):
    id: str
    isDeletable: Optional[bool] = None
    deletionRefuseReason: Optional[str] = None

    class Config:
        extra = "allow"


class InspectionModel(BaseModel):
    id: int

    projectId: Optional[str] = None
    number: Optional[str] = None
    buildingObject: Optional[str] = None
    location: Optional[str] = None
    workType: Optional[str] = None
    workTypes: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    status: Optional[str] = None
    result: Optional[str] = None

    creationDate: Optional[int] = None
    startDate: Optional[int] = None
    endDate: Optional[int] = None
    removalTerm: Optional[str] = None
    removalDate: Optional[str] = None
    removeResponsibleDate: Optional[str] = None

    authorUserId: Optional[str] = None
    responsibleUserId: Optional[str] = None
    responsibleBuilderUserId: Optional[str] = None
    creatorUserId: Optional[str] = None

    notifyUserIds: List[str] = Field(default_factory=list)
    participantUserIds: List[str] = Field(default_factory=list)

    authorUser: Optional[UserPreview] = None
    responsibleUser: Optional[UserPreview] = None
    responsibleBuilder: Optional[UserPreview] = None
    creatorUser: Optional[UserPreview] = None
    notifyUsers: List[UserPreview] = Field(default_factory=list)
    participantUsers: List[UserPreview] = Field(default_factory=list)

    priorityType: Optional[str] = None
    attentionIndicator: Optional[str] = None
    hasComments: Optional[bool] = None
    isSigned: Optional[bool] = None
    isSend: Optional[bool] = None
    createdFromBus: Optional[bool] = None

    pirCiphers: List[PirCipher] = Field(default_factory=list)
    descriptionAttachments: List[FileAttachment] = Field(default_factory=list)
    responsibleForCorrectingAttachments: List[FileAttachment] = Field(default_factory=list)

    generalJournalIds: List[str] = Field(default_factory=list)
    inspectionIds: List[int] = Field(default_factory=list)
    inspectionNumbers: List[str] = Field(default_factory=list)
    inspectionCount: Optional[str] = None

    remarks: List[RemarkLink] = Field(default_factory=list)
    remarkNumbers: List[str] = Field(default_factory=list)
    remarkCount: Optional[str] = None

    causes: List[str] = Field(default_factory=list)
    structureElement: Optional[str] = None
    requestRemovalRemark: Optional[str] = None
    refuseReason: Optional[str] = None

    class Config:
        extra = "allow"
        str_strip_whitespace = True
        from_attributes = True
