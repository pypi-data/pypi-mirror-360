from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict

from .common import UserPreview, PirCipher, FileAttachment


class RemarkModel(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        str_strip_whitespace=True,
        from_attributes=True,
    )

    id: int
    projectId: Optional[str] = None

    creationDate: Optional[int] = None
    removalTerm: Optional[int] = None
    removalDate: Optional[int] = None
    removeResponsibleDate: Optional[int] = None

    authorUserId: Optional[str] = None
    responsibleUserId: Optional[str] = None
    creatorUserId: Optional[str] = None
    notifyUserIds: List[str] = Field(default_factory=list)

    authorUser: Optional[UserPreview] = None
    responsibleUser: Optional[UserPreview] = None
    creatorUser: Optional[UserPreview] = None
    notifyUsers: List[UserPreview] = Field(default_factory=list)

    number: Optional[str] = None
    buildingObject: Optional[str] = None
    location: Optional[str] = None
    workType: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priorityType: Optional[str] = None

    causes: List[str] = Field(default_factory=list)

    pirCiphers: List[PirCipher] = Field(default_factory=list)
    descriptionAttachments: List[FileAttachment] = Field(default_factory=list)
    responsibleForCorrectingAttachments: List[FileAttachment] = Field(default_factory=list)

    generalJournalIds: List[str] = Field(default_factory=list)
    inspectionIds: List[int] = Field(default_factory=list)
    inspectionNumbers: List[str] = Field(default_factory=list)
    inspectionCount: Optional[str] = None

    isSigned: Optional[bool] = None
    isSend: Optional[bool] = None
    createdFromBus: Optional[bool] = None
    attentionIndicator: Optional[str] = None
    hasComments: Optional[bool] = None

    structureElement: Optional[str] = None
    requestRemovalRemark: Optional[str] = None
    refuseReason: Optional[str] = None
