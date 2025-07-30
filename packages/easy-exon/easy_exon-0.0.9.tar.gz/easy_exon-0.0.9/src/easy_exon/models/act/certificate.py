from typing import Optional, List
from pydantic import BaseModel


class FileInfo(BaseModel):
    id: str
    name: Optional[str] = None
    extension: Optional[str] = None
    size: Optional[str] = None
    date: Optional[str] = None
    pagesNumber: Optional[int] = None
    hashMd5: Optional[str] = None

    class Config:
        extra = "allow"


class PersonShort(BaseModel):
    id: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    middleName: Optional[str] = None
    position: Optional[str] = None

    class Config:
        extra = "allow"


class OrganizationShort(BaseModel):
    id: str
    shortName: Optional[str] = None
    inn: Optional[str] = None
    ogrn: Optional[str] = None

    class Config:
        extra = "allow"


class AcceptanceCertificate(BaseModel):
    certificateVersionId: str
    costForReportingPeriodWithoutNDS: Optional[float] = None
    valueAddedTax: Optional[float] = None
    costForReportingPeriod: Optional[float] = None
    pdfFileId: Optional[str] = None
    pdfFile: Optional[FileInfo] = None
    qrFileId: Optional[str] = None
    qrFile: Optional[FileInfo] = None
    xlsFileId: Optional[str] = None
    xmlFileId: Optional[str] = None

    class Config:
        extra = "allow"


class ContractInfo(BaseModel):
    id: str
    contractId: str
    title: Optional[str] = None
    customerOrganizationId: Optional[str] = None
    executorOrganizationId: Optional[str] = None
    currency: Optional[str] = None

    class Config:
        extra = "allow"


class CertificateModel(BaseModel):
    id: str

    projectId: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    version: Optional[int] = None
    number: Optional[str] = None
    beginningDate: Optional[str] = ModuleNotFoundError
    endDate: Optional[str] = None
    formDate: Optional[str] = None
    warning: Optional[str] = None

    executor: Optional[PersonShort] = None
    organization: Optional[OrganizationShort] = None
    executorOrganization: Optional[OrganizationShort] = None

    acceptanceCertificate: Optional[AcceptanceCertificate] = None
    supportDocuments: Optional[List[FileInfo]] = None
    contractInfo: Optional[ContractInfo] = None

    class Config:
        extra = "allow"

class CertificateResponseModel(BaseModel):
    certificates: Optional[List[CertificateModel]] = None
    indicatorsCount: Optional[int] = None
    warning: Optional[str] = None

    class Config:
        extra = "allow"
