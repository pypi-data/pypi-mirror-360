from typing import List, Optional
from pydantic import BaseModel


class TaskModel(BaseModel):
    id: str

    name: Optional[str] = None
    pdSection: Optional[str] = None
    normativeDocumentNames: Optional[List[str]] = None
    workTypeId: Optional[str] = None
    userId: Optional[str] = None

    class Config:
        extra = "allow"
