from typing import List, Optional
from pydantic import BaseModel


class ParticipantModel(BaseModel):
    id: str
    organizationId: Optional[str] = None
    userId: Optional[str] = None
    position: Optional[str] = None

    class Config:
        extra = "allow"


class ApproverModel(BaseModel):
    userId: str
    status: Optional[str] = None

    class Config:
        extra = "allow"


class CheckingActModel(BaseModel):
    id: str
    originalActId: Optional[str] = None
    projectId: Optional[str] = None
    actNumber: Optional[str] = None
    inspectionDate: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    contractId: Optional[str] = None
    peopleCount: Optional[int] = None
    checkingActId: Optional[str] = None
    actApplicationId: Optional[str] = None
    deadlineTotal: Optional[bool] = None
    deadlineDays: Optional[int] = None
    checkingActDate: Optional[str] = None
    typeAct: Optional[str] = None
    parentActId: Optional[str] = None
    createdAt: Optional[str] = None
    path: Optional[List[str]] = None
    participants: Optional[List[ParticipantModel]] = None
    approvers: Optional[List[ApproverModel]] = None

    class Config:
        extra = "allow"
