from pydantic import BaseModel, field_validator, HttpUrl, validator, conint
from typing import Optional
from utils import SetMobileRedirectEnum

class ShortenUrl(BaseModel):
    short: HttpUrl

    @field_validator("short")
    def convert_edit_to_str(cls, v):
        return str(v)

class CustomAliasForm(BaseModel):
    short = str
    name = str

class CustomDomainForm(BaseModel):
    short = str
    userDomain = str

class CustomAliasCustomDomainForm(BaseModel):
    short = str
    name = str
    userDomain = str

class CustomAliasNoTitleParameter(BaseModel):
    short = str
    noTitle = int

class CustomAliasPublicParameter(BaseModel):
    short = str
    public = int

class TraiSMSDomain(BaseModel):
    short = str
    userDomain = int

class TraiSMSDomainCustomAlias(BaseModel):
    short = str
    userDomain = int
    name = str

class LinkEditAddTagRequest(BaseModel):
    edit: HttpUrl
    tag: Optional[str] = None

    @field_validator("edit")
    def convert_edit_to_str(cls, v):
        return str(v)

    @field_validator("tag", mode="before")
    def convert_tag_to_str(cls, v):
        if v is None:
            return ""
        return str(v)

class LinkEditChangeAlias(BaseModel):
    edit: HttpUrl
    name: Optional[str] = None

    @field_validator("edit")
    def convert_edit_to_str(cls, v):
        return str(v)

    @field_validator("name", mode="before")
    def convert_tag_to_str(cls, v):
        if v is None:
            return ""
        return str(v)

class LinkEditChangeSourceURL(BaseModel):
    edit: HttpUrl
    source: HttpUrl

    @field_validator("edit")
    def convert_edit_to_str(cls, v):
        return str(v)

    @field_validator("source")
    def convert_source_to_str(cls, v):
        return str(v)

class LinkEditSetUniqueClicks(BaseModel):
    edit: HttpUrl
    unique: conint(ge=0, le=1)

    @field_validator("edit")
    def convert_edit_to_str(cls, v):
        return str(v)

class LinkEditSetUniqueClick1440Minutes(BaseModel):
    edit: HttpUrl
    unique: conint(ge=15, le=1440)

    @field_validator("edit")
    def convert_edit_to_str(cls, v):
        return str(v)

class LinkEditRemoveUniqueClick(BaseModel):
    edit: HttpUrl
    unique: conint(ge=0, le=1)

    @field_validator("edit")
    def convert_edit_to_str(cls, v):
        return str(v)

class LinkEditSetTitle(BaseModel):
    edit: HttpUrl
    title: str

    @field_validator("edit")
    def convert_edit_to_str(cls, v):
        return str(v)

    @field_validator("title")
    def convert_title_to_str(cls, v):
        return str(v)

class LinkEditSetMobileRedirect(BaseModel):
    edit: HttpUrl
    mobile: SetMobileRedirectEnum
    destination: str

    @field_validator("edit")
    def convert_edit_to_str(cls, v):
        return str(v)

    @field_validator("mobile")
    def convert_mobile_to_str(cls, v):
        return str(v)

class LinkEditRemoveMobileRedirect(BaseModel):
    edit: HttpUrl
    mobile: SetMobileRedirectEnum

    @field_validator("edit")
    def convert_edit_to_str(cls, v):
        return str(v)

    @field_validator("mobile")
    def convert_mobile_to_str(cls, v):
        return str(v)

class LinkEditDeleteShortenedLinkSpecificEdit(BaseModel):
    edit: HttpUrl
    delete: conint(ge=0, le=1)

    @field_validator("edit")
    def convert_edit_to_str(cls, v):
        return str(v)

class LinkEditSetExpirationClick(BaseModel):
    edit: HttpUrl
    expire: int
    expireCond: str
    expireRedirect: str
    expireUnique: int

    @field_validator("edit")
    def convert_edit_to_str(cls, v):
        return str(v)

    @field_validator("expire")
    def convert_expire_to_str(cls, v):
        return str(v)


class LinkEditSetExpirationDate(BaseModel):
    edit: HttpUrl
    expire: int
    expireCond: str
    expireRedirect: str
    expireUnique: int

    @field_validator("edit")
    def convert_edit_to_str(cls, v):
        return str(v)

    @field_validator("expire")
    def convert_expire_to_str(cls, v):
        return str(v)


class LinkEditRemoveExpiration(BaseModel):
    edit: HttpUrl
    expire: int
    expireCond: str

    @field_validator("edit")
    def convert_edit_to_str(cls, v):
        return str(v)

    @field_validator("expire")
    def convert_expire_to_str(cls, v):
        return str(v)


class LinkEditSetPassword(BaseModel):
    edit: HttpUrl
    password: int

    @field_validator("edit")
    def convert_edit_to_str(cls, v):
        return str(v)

    @field_validator("password")
    def convert_password_to_int(cls, v):
        return int(v)


class LinkEditSetAbTest(BaseModel):
    edit: HttpUrl
    abtest: conint(ge=0, le=2)
    abtest_b: conint(ge=0, le=100)
    abtest_bvariation: str

    @field_validator("edit")
    def convert_edit_to_str(cls, v):
        return str(v)


class LinkEditSetAbcTest(BaseModel):
    edit: HttpUrl
    abtest: conint(ge=0, le=2)
    abtest_b: conint(ge=0, le=100)
    abtest_bvariation: str
    abtest_c = int,
    abtest_cvariation = str

    @field_validator("edit")
    def convert_edit_to_str(cls, v):
        return str(v)


class LinkEditTestRemove(BaseModel):
    edit: HttpUrl
    abtest = int,

    @field_validator("edit")
    def convert_edit_to_str(cls, v):
        return str(v)


class LinkAnalyticsForm(BaseModel):
    edit: HttpUrl
    date_from = str
    date_to = str

    @field_validator("edit")
    def convert_edit_to_str(cls, v):
        return str(v)

class LinkAnalyticsStatisticsForm(BaseModel):
    edit: HttpUrl
    stats = str

    @field_validator("edit")
    def convert_edit_to_str(cls, v):
        return str(v)

class LinkAnalyticsDateRangeForm(BaseModel):
    stats = str
    date_from = str
    date_to = str
