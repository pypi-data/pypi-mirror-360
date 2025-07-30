from datetime import date as Date
from typing import Optional
from pydantic import BaseModel


class ExpertiseModel(BaseModel):
    id: str
    number: Optional[str] = None
    date: Optional[Date] = None
    projectId: Optional[str] = None
    fileId: Optional[str] = None
    extension: Optional[str] = None
    expertiseForm: Optional[str] = None
    organizationId: Optional[str] = None
    result: bool
    isExternal: bool

    class Config:
        from_attributes = True
        alias_generator = lambda s: s
        validate_by_name = True