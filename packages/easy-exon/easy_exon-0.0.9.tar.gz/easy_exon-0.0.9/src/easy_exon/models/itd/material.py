from typing import List, Dict, Optional
from pydantic import BaseModel


class SodExchangeInfoModel(BaseModel):
    sendingStatus: Optional[str] = None

    class Config:
        extra = "allow"


class MaterialModel(BaseModel):
    id: str

    typeOfControls: Optional[List[str]] = None
    name: Optional[str] = None
    amount: Optional[float] = None
    remainingAmount: Optional[float] = None
    dpkList: Optional[List[str]] = None
    deviations: Optional[bool] = None
    number: Optional[int] = None
    providerOrgId: Optional[str] = None
    receiveDate: Optional[str] = None
    userId: Optional[str] = None
    userOrganizationId: Optional[str] = None
    permittedOrgIds: Optional[List[str]] = None
    signed: Optional[bool] = None
    sodExchangeInfo: Optional[SodExchangeInfoModel] = None
    orgId: Optional[str] = None

    class Config:
        extra = "allow"


class ConnectionEntryModel(BaseModel):
    unitMeasureId: Optional[str] = None
    itdSectionIds: Optional[List[str]] = None

    class Config:
        extra = "allow"


class MaterialsPackageModel(BaseModel):
    materials: List[MaterialModel]
    connectionInfo: Optional[Dict[str, ConnectionEntryModel]] = None
    itdSections: Optional[Dict[str, str]] = None

    class Config:
        extra = "allow"
