from typing import List, Optional, Any
from pydantic import BaseModel


class SodExchangeInfo(BaseModel):
    sendingStatus: Optional[str] = None

    class Config:
        extra = "allow"


class DateInterval(BaseModel):
    dateStart: Optional[str] = None
    dateEnd: Optional[str] = None

    class Config:
        extra = "allow"


class SROInfo(BaseModel):
    orgId: Optional[str] = None
    address: Optional[str] = None
    name: Optional[str] = None
    ogrn: Optional[str] = None
    inn: Optional[str] = None
    kpp: Optional[str] = None

    class Config:
        extra = "allow"


class Participant(BaseModel):
    orgId: Optional[str] = None
    shortName: Optional[str] = None
    address: Optional[str] = None
    name: Optional[str] = None
    ogrn: Optional[str] = None
    inn: Optional[str] = None
    kpp: Optional[str] = None
    sro: Optional[SROInfo] = None
    participantId: Optional[str] = None

    class Config:
        extra = "allow"


class ParticipantsBlock(BaseModel):
    participants: Optional[List[Participant]] = None
    users: Optional[List[Any]] = None
    hasRemarks: Optional[bool] = None
    stateExpertise: Optional[Any] = None

    class Config:
        extra = "allow"


class RegistryInfo(BaseModel):
    registryType: Optional[str] = None
    numberInRegistry: Optional[str] = None
    entryDate: Optional[str] = None

    class Config:
        extra = "allow"


class SkUser(BaseModel):
    id: str
    userId: Optional[str] = None
    orgId: Optional[str] = None
    fullName: Optional[str] = None
    position: Optional[str] = None
    order: Optional[str] = None
    orderId: Optional[str] = None
    orderNumber: Optional[str] = None
    orderDate: Optional[str] = None
    participantId: Optional[str] = None
    orgShortName: Optional[str] = None
    workStartDate: Optional[str] = None
    workEndDate: Optional[str] = None
    completedWorks: Optional[str] = None
    typeOfWorks: Optional[str] = None
    status: Optional[str] = None
    isAutomaticCreated: Optional[bool] = None
    registry: Optional[RegistryInfo] = None

    class Config:
        extra = "allow"


class SkParticipantInfo(BaseModel):
    customerSkUsers: Optional[List[SkUser]] = None
    generalContractorSkUsers: Optional[List[SkUser]] = None
    hasRemarks: Optional[bool] = None

    class Config:
        extra = "allow"


class GeneralInformation(BaseModel):
    buildingType: Optional[str] = None
    objectName: Optional[str] = None
    dateInterval: Optional[DateInterval] = None
    constructionLicense: Optional[str] = None
    hasRemarks: Optional[bool] = None
    titlePageNumber: Optional[int] = None

    class Config:
        extra = "allow"


class BuildingInfo(BaseModel):
    id: Optional[str] = None
    user: Optional[Any] = None
    organization: Optional[Any] = None
    number: Optional[str] = None
    name: Optional[str] = None
    signed: Optional[bool] = None
    hasRemarks: Optional[bool] = None
    registrationDate: Optional[str] = None
    sodExchangeInfo: Optional[SodExchangeInfo] = None

    class Config:
        extra = "allow"


class TitlePage(BaseModel):
    id: Optional[str] = None

    generalInformation: Optional[GeneralInformation] = None
    developerInfo: Optional[ParticipantsBlock] = None
    customerInfo: Optional[ParticipantsBlock] = None
    generalContractorInfo: Optional[ParticipantsBlock] = None
    skParticipantInfo: Optional[SkParticipantInfo] = None
    designerParticipantInfo: Optional[ParticipantsBlock] = None
    contractorAndSubcontractorParticipantInfo: Optional[ParticipantsBlock] = None
    buildingInfo: Optional[BuildingInfo] = None

    hasRemarks: Optional[bool] = None
    sodExchangeInfo: Optional[SodExchangeInfo] = None

    class Config:
        extra = "allow"


class SectionOne(BaseModel):
    sectionOneUsers: Optional[List[Any]] = None

    class Config:
        extra = "allow"


class SectionTwoUser(BaseModel):
    id: str
    specialJournalOrderType: Optional[str] = None
    userId: Optional[str] = None
    orgId: Optional[str] = None
    journalNumber: Optional[str] = None
    userName: Optional[str] = None
    dateOfJournal: Optional[str] = None
    generalInfoUserId: Optional[str] = None

    class Config:
        extra = "allow"


class SectionTwo(BaseModel):
    sectionTwoUsers: Optional[List[SectionTwoUser]] = None

    class Config:
        extra = "allow"


class ExecutingWork(BaseModel):
    generalJournalId: Optional[str] = None
    itdTaskId: Optional[str] = None
    number: Optional[int] = None
    startDate: Optional[str] = None
    description: Optional[str] = None
    sectionsInfo: Optional[str] = None
    userId: Optional[str] = None
    actual: Optional[bool] = None
    version: Optional[int] = None
    sodExchangeInfo: Optional[SodExchangeInfo] = None

    class Config:
        extra = "allow"


class ExecutingWorksInformation(BaseModel):
    executingWorks: Optional[List[ExecutingWork]] = None

    class Config:
        extra = "allow"


class CustomerRemark(BaseModel):
    id: str
    projectId: Optional[str] = None
    number: Optional[int] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    element: Optional[str] = None
    location: Optional[str] = None
    nameWork: Optional[str] = None
    generalJournalIds: Optional[List[str]] = None
    signatureControl: Optional[Any] = None
    remarkId: Optional[int] = None
    numberRemark: Optional[int] = None
    remarkCreatedDate: Optional[str] = None
    numberPage: Optional[int] = None
    cause: Optional[str] = None
    cipher: Optional[str] = None
    description: Optional[str] = None
    inspectionId: Optional[str] = None
    removalTerm: Optional[str] = None
    controlId: Optional[str] = None
    fullNameControl: Optional[str] = None
    violationsDate: Optional[str] = None
    executorId: Optional[str] = None
    fullNameExecutor: Optional[str] = None
    signatureCheckViolations: Optional[Any] = None
    sodExchangeInfo: Optional[SodExchangeInfo] = None

    class Config:
        extra = "allow"


class SignerInfo(BaseModel):
    signerInfoId: Optional[str] = None
    name: Optional[str] = None
    position: Optional[str] = None
    signsDate: Optional[str] = None

    class Config:
        extra = "allow"


class ExecutiveDoc(BaseModel):
    number: Optional[int] = None
    description: Optional[str] = None
    actId: Optional[str] = None
    signersInfo: Optional[List[SignerInfo]] = None

    class Config:
        extra = "allow"


class ExecutiveDocsInformation(BaseModel):
    executiveDocs: Optional[List[ExecutiveDoc]] = None

    class Config:
        extra = "allow"


class GeneralJournalModel(BaseModel):
    id: str

    projectId: Optional[str] = None
    titleStatus: Optional[str] = None
    version: Optional[int] = None
    remarks: Optional[List[Any]] = None

    titlePage: Optional[TitlePage] = None
    sectionOne: Optional[SectionOne] = None
    sectionTwo: Optional[SectionTwo] = None

    executingWorksInformation: Optional[ExecutingWorksInformation] = None
    customer: Optional[List[CustomerRemark]] = None
    generalContractor: Optional[List[Any]] = None

    executiveDocsInformation: Optional[ExecutiveDocsInformation] = None
    sodExchangeInfo: Optional[SodExchangeInfo] = None

    class Config:
        extra = "allow"
