from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class SupportDocumentModel(BaseModel):
    fileId: Optional[str] = None

    date: Optional[str] = None
    documentName: Optional[str] = None
    extension: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    executiveSchemeId: Optional[str] = None
    isActual: Optional[bool] = None
    itdDocumentId: Optional[str] = None
    explorerEntityId: Optional[str] = None
    workDocumentId: Optional[str] = None
    workDocumentOriginalFileId: Optional[str] = None
    fileIdWithStamp: Optional[str] = None
    number: Optional[str] = None
    orgName: Optional[str] = None
    createdBy: Optional[str] = None
    successSigned: Optional[bool] = None
    change: Optional[int] = None
    vprDate: Optional[str] = None
    cipher: Optional[str] = None
    numberList: Optional[str] = None
    absoluteNumberList: Optional[str] = None
    inherit: Optional[bool] = None
    generate: Optional[bool] = None
    registryDocsCountMap: Optional[Dict[str, Any]] = None
    actualVolumes: Optional[Any] = None
    fullDocumentName: Optional[str] = None
    shouldAddTitlePages: Optional[bool] = None
    startPage: Optional[int] = None
    isAllPagesSelected: Optional[bool] = None
    gipApproves: Optional[Any] = None
    authorWorkDoc: Optional[str] = None
    isCustomPagesList: Optional[bool] = None
    workDocumentOriginalFileIdOrFileId: Optional[str] = None

    class Config:
        extra = "allow"
