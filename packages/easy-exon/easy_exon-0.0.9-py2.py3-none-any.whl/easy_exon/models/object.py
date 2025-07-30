from typing import List, Optional

from pydantic import BaseModel, Field

class ObjectAddressModel(BaseModel):
    postal_code:         Optional[str] = None
    region:              Optional[str] = None
    region_with_type:    Optional[str] = None
    city_type:           Optional[str] = None
    city:                Optional[str] = None
    city_with_type:      Optional[str] = None
    city_area:           Optional[str] = None
    street:              Optional[str] = None
    house:               Optional[str] = None
    projectAddressValue: Optional[str] = Field(default=None, alias="projectAddressValue")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }


class ObjectModel(BaseModel):
    id:               str
    category:         Optional[str]                 = None
    hashTags:         Optional[List[str]]           = None
    image:            Optional[str]                 = None
    name:             Optional[str]                 = None
    status:           Optional[str]                 = None
    projectAddress:   Optional[ObjectAddressModel]  = None
    integrationType:  Optional[str]                 = None
    dsCode:           Optional[str]                 = None
    gis:              Optional[bool]                = None

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }


class ProjectAddressModel(BaseModel):
    region_with_type: Optional[str] = None
    city: Optional[str] = None
    city_with_type: Optional[str] = None
    city_area: Optional[str] = None
    city_district: Optional[str] = None
    projectAddressValue: Optional[str] = None


class ReferenceModel(BaseModel):
    userId: str


class LocationModel(BaseModel):
    geoLat: float
    geoLon: float


class MemberUserModel(BaseModel):
    userId: str
    projectParticipantRole: str


class SroCertificateModel(BaseModel):
    organizationId: Optional[str] = None
    date: Optional[str] = None
    number: Optional[str] = None


class ContractModel(BaseModel):
    id: str
    name: str
    number: str
    startDate: str
    endDate: str
    customerId: str
    executorIds: List[str] = Field(default_factory=list)


class ProjectOrganizationMemberModel(BaseModel):
    id: str
    organizationId: str
    projectId: str
    organizationRole: str

    userIds: List[str] = Field(default_factory=list)
    memberUsers: List[MemberUserModel] = Field(default_factory=list)

    contracts: List[ContractModel] = Field(default_factory=list)
    sroCertificates: List[SroCertificateModel] = Field(default_factory=list)
    hashTags: List[str] = Field(default_factory=list)

    isDeveloper: bool = False
    isCustomerBuildControl: Optional[bool] = None


class ProjectModel(BaseModel):
    id: str
    name: Optional[str]
    shortName: Optional[str] = None

    projectAddress: Optional[ProjectAddressModel] = None
    image: Optional[str] = None

    dateStart: Optional[str] = None
    dateEnd: Optional[str] = None
    duration: Optional[int] = None

    hashTags: List[str] = Field(default_factory=list)
    category: Optional[str] = None

    location: Optional[LocationModel] = None
    status: Optional[str] = None
    description: Optional[str] = None

    manager: Optional[ReferenceModel] = None
    administrator: Optional[ReferenceModel] = None
    projectInitiator: Optional[ReferenceModel] = None

    organisationId: Optional[str] = None
    createdDate: Optional[str] = None
    dsCode: Optional[str] = None

    projectOrganizationMembers: List[ProjectOrganizationMemberModel] = Field(
        default_factory=list
    )

    cadastralNumber: Optional[str] = None
    grbc: Optional[str] = None
    nationalProject: Optional[str] = None

    integrationType: Optional[str] = None
    gisOgdSyncStatus: Optional[str] = None
    gis: Optional[bool] = None

    model_config = {
        "populate_by_name": True,
        "str_max_length": 5000,
        "arbitrary_types_allowed": True,
    }
