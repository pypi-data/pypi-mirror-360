from typing import List, Dict, Optional
from pydantic import BaseModel


class BaseOrderModel(BaseModel):
    id: str

    fileId: Optional[str] = None
    number: Optional[str] = None
    issueDate: Optional[str] = None
    position: Optional[str] = None
    projectIds: Optional[List[str]] = None
    type: Optional[str] = None
    organizationId: Optional[str] = None
    workTypeIds: Optional[List[str]] = None
    validityPeriods: Optional[List[str]] = None

    class Config:
        extra = "allow"


class SpecialOrderModel(BaseModel):
    id: str

    fileId: Optional[str] = None
    number: Optional[str] = None
    issueDate: Optional[str] = None
    position: Optional[str] = None
    projectIds: Optional[List[str]] = None
    type: Optional[str] = None
    organizationId: Optional[str] = None
    specialJournalOrderTypes: Optional[List[str]] = None

    class Config:
        extra = "allow"


class OrdersPackageModel(BaseModel):
    projects: Dict[str, str]
    baseOrders: List[BaseOrderModel]
    specialOrders: List[SpecialOrderModel]

    class Config:
        extra = "allow"
