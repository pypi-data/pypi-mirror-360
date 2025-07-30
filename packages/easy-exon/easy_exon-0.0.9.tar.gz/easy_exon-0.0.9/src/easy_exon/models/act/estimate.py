from typing import Optional
from pydantic import BaseModel


class EstimateModel(BaseModel):
    id: str

    projectId: Optional[str] = None
    contractId: Optional[str] = None
    parentEstimateId: Optional[str] = None
    version: Optional[int] = None
    additionalAgreement: Optional[str] = None
    newVersionExist: Optional[bool] = None
    documentName: Optional[str] = None
    status: Optional[str] = None
    constructorId: Optional[str] = None

    class Config:
        extra = "allow"
