from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class OrgUserLink(BaseModel):
    userId: str
    department: Optional[str] = None
    position: Optional[str] = None


class AddressData(BaseModel):
    source: Optional[str] = None
    postalCode: Optional[str] = None
    regionKladrId: Optional[str] = None
    region: Optional[str] = None
    area: Optional[str] = None
    cityType: Optional[str] = None
    city: Optional[str] = None
    settlementType: Optional[str] = None
    settlement: Optional[str] = None
    cityArea: Optional[str] = None
    cityDistrict: Optional[str] = None
    street: Optional[str] = None
    house: Optional[str] = None
    blockType: Optional[str] = None
    block: Optional[str] = None
    floor: Optional[str] = None
    flatType: Optional[str] = None
    flat: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class OrganizationSnapshot(BaseModel):
    id: str
    name: str
    shortName: Optional[str] = None
    inn: Optional[str] = None
    ogrn: Optional[str] = None
    ogrnDate: Optional[str] = None
    kpp: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    pictureId: Optional[str] = None
    ceo: Optional[str] = None
    address: Optional[str] = None
    postalCode: Optional[str] = None

    users: Optional[List[OrgUserLink]] = None
    addressData: Optional[AddressData] = None
    sroOrganizations: Optional[List[dict]] = None
    organisationChanges: Optional[dict] = None

    type: Optional[str] = None
    branchType: Optional[str] = None
    isGis: Optional[bool] = None
    isUpdated: Optional[bool] = None
    updatedAt: Optional[str] = None
    dadataHid: Optional[str] = None
    codeCountry: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class OrganizationModel(BaseModel):
    id: str
    name: str
    shortName: Optional[str] = None

    inn: Optional[str] = None
    ogrn: Optional[str] = None
    ogrnDate: Optional[str] = None
    kpp: Optional[str] = None

    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    pictureId: Optional[str] = None
    ceo: Optional[str] = None

    address: Optional[str] = None
    postalCode: Optional[str] = None
    addressData: Optional[AddressData] = None

    users: List[OrgUserLink] = Field(default_factory=list)
    sroOrganizations: List[dict] = Field(default_factory=list)
    organisationChanges: Optional[dict] = None

    history: List[OrganizationSnapshot] = Field(default_factory=list)

    type: Optional[str] = None
    branchType: Optional[str] = None
    isGis: Optional[bool] = None
    isUpdated: Optional[bool] = None
    updatedAt: Optional[str] = None
    dadataHid: Optional[str] = None
    codeCountry: Optional[str] = None

    model_config = ConfigDict(extra="allow", str_strip_whitespace=True, from_attributes=True)
