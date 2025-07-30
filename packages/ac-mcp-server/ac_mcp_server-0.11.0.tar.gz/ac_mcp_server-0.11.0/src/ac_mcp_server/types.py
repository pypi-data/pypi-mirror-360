from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import List, Literal, Optional, Any, Dict, Union
from enum import Enum
from datetime import date, datetime


# Enums and Literals
class ContactStatus(Enum):
    ANY = -1
    UNCONFIRMED = 0
    ACTIVE = 1
    UNSUBSCRIBED = 2
    BOUNCED = 3


ContactCustomFieldType = Literal[
    "text",
    "textarea",
    "dropdown",
    "checkbox",
    "radio",
    "date",
    "datetime",
    "hidden",
    "listbox",
]

ContactSortField = Literal[
    "id", "cdate", "email", "first_name", "last_name", "name", "score"
]

ContactFilterField = Literal[
    "created_before", "created_after", "updated_before", "updated_after"
]

TagSearchOperator = Literal[
    "eq", "neq", "lt", "lte", "gt", "gte", "contains", "starts_with"
]

TagOrderMethod = Literal["weight", "asc", "desc"]

EmailActivityFilterField = Literal["subscriberid", "fieldid"]

EmailActivitySortField = Literal["subscriberid", "fieldid", "tstamp", "id"]

CampaignType = Literal[
    "single",
    "recurring",
    "split",
    "responder",
    "reminder",
    "special",
    "activerss",
    "text",
]

CampaignSortField = Literal["sdate", "mdate", "ldate", "status"]

CampaignStatus = Literal[
    "drafts",  # 0
    "scheduled",  # 1
    "currently-sending",  # 2
    "paused",  # 3
    "stopped",  # 4
    "complete",  # 5
    "disabled",  # 6
    "pending-review",  # 7
    "determining-winner",  # special case
]

AutomationSortField = Literal[
    "name",
    "status",
    "entered",
    "cdate",
    "mdate",
    "revisions",
]

ContactAutomationSortField = Literal[
    "seriesid",
    "adddate",
    "status",
    "lastblock",
    "subscriberid",
    "name",
    "first_name",
    "last_name",
    "email",
    "cdate",
    "score",
    "goal_completion",
]

ContactAutomationDateOperator = Literal["eq", "gt", "gte", "lt", "lte"]


ListFilterChannelType = Literal["email", "sms", "all"]
ListSortDirection = Literal["ASC", "DESC"]
ListNameOrderSetting = Literal["ASC", "DESC", "weight"]


# Supporting Parameter Classes
class ContactCreateFieldValues(BaseModel):
    field: int
    value: str


class ContactAutomationDateFilter(BaseModel):
    eq: Optional[Union[str, date, datetime]] = None
    gt: Optional[Union[str, date, datetime]] = None
    gte: Optional[Union[str, date, datetime]] = None
    lt: Optional[Union[str, date, datetime]] = None
    lte: Optional[Union[str, date, datetime]] = None


class ContactAutomationFilters(BaseModel):
    seriesid: Optional[Union[str, int]] = None
    adddate: Optional[Union[str, ContactAutomationDateFilter]] = None
    status: Optional[Union[str, int]] = None
    lastblock: Optional[Union[str, int]] = None
    subscriberid: Optional[Union[str, int]] = None


class CampaignFilterField(BaseModel):
    type: Optional[CampaignType] = None
    list_id: Optional[int] = None
    automation: Optional[bool] = None
    willrecur: Optional[bool] = None
    seriesid: Optional[str] = None
    label_name: Optional[str] = None
    name: Optional[str] = None
    id: Optional[int] = None
    status: Optional[str] = None


class AutomationFilterField(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    ids: Optional[str] = None
    tag: Optional[int] = None
    triggers: Optional[str] = None
    actions: Optional[str] = None
    label_name: Optional[str] = None


class ListFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    name: Optional[str] = None
    list_id: Optional[str] = Field(None, alias="id")
    channel: Optional[ListFilterChannelType] = None
    userid_single: Optional[int] = Field(None, alias="userid")
    userid_array: Optional[List[int]] = Field(None, alias="userid[]")
    created_timestamp: Optional[Union[str, date, datetime]] = None
    active_subscribers: Optional[int] = None

    @model_validator(mode="after")
    def check_userid_fields(self) -> "ListFilters":
        if self.userid_single is not None and self.userid_array is not None:
            raise ValueError(
                "Cannot set both 'userid' (single) and 'userid[]' (array) filters."
            )
        return self


class ListOrders(BaseModel):
    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    name: Optional[ListNameOrderSetting] = None
    id: Optional[ListSortDirection] = None
    channel: Optional[ListSortDirection] = None
    userid: Optional[ListSortDirection] = None
    created_timestamp: Optional[ListSortDirection] = None
    active_subscribers: Optional[ListSortDirection] = None


class FieldOptionCreateParams(BaseModel):
    orderid: int
    value: str
    label: str
    isdefault: bool = False
    field: str


# Main Parameter Classes
class ContactCreateParams(BaseModel):
    email: str
    firstName: str
    lastName: str
    phone: str
    fieldValues: Optional[List[ContactCreateFieldValues]] = None


class ContactTagParams(BaseModel):
    contact: int
    tag: int


class TagCreateParams(BaseModel):
    tag: str
    description: str = ""
    tagType: str = "contact"


class ContactCustomFieldCreateParams(BaseModel):
    title: str
    type: ContactCustomFieldType
    perstag: Optional[str] = None
    descript: Optional[str] = None
    defval: Optional[str] = None
    visible: Optional[Literal[0, 1]] = None
    ordernum: Optional[int] = None


class FieldOptionBulkCreateParams(BaseModel):
    fieldOptions: List[FieldOptionCreateParams]


class ContactFieldRelCreateParams(BaseModel):
    relid: int
    field: str


class ContactListParams(BaseModel):
    segmentid: Optional[int] = None
    formid: Optional[int] = None
    listid: Optional[int] = None
    tagid: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    search: Optional[str] = None
    orders: Optional[Dict[ContactSortField, Literal["ASC", "DESC"]]] = None
    filters: Optional[Dict[ContactFilterField, Union[str, datetime, date]]] = None
    id_greater: Optional[int] = None
    seriesid: Optional[int] = None
    waitid: Optional[int] = None
    status: Optional[ContactStatus] = None


class TagListParams(BaseModel):
    search_filters: Optional[Dict[TagSearchOperator, str]] = Field(
        None, alias="filters[search]"
    )
    order_method: Optional[TagOrderMethod] = Field(None, alias="orders[search]")
    limit: Optional[int] = None
    offset: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True, populate_by_alias=True)


class ContactCustomFieldListParams(BaseModel):
    limit: Optional[int] = None
    offset: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True, populate_by_alias=True)


class ContactFieldValueCreateParams(BaseModel):
    contact: int
    field: int
    value: str
    useDefaults: Optional[bool] = None


class ContactFieldValueUpdateParams(BaseModel):
    value: str
    useDefaults: Optional[bool] = None


class ContactFieldValueListParams(BaseModel):
    filters: Optional[Dict[Literal["fieldid"], int]] = None
    limit: Optional[int] = None
    offset: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True, populate_by_alias=True)


class EmailActivityListParams(BaseModel):
    limit: Optional[int] = None
    offset: Optional[int] = None
    orders: Optional[Dict[EmailActivitySortField, Literal["ASC", "DESC"]]] = None
    filters: Optional[Dict[EmailActivityFilterField, str]] = None

    model_config = ConfigDict(populate_by_name=True, populate_by_alias=True)


class CampaignListParams(BaseModel):
    limit: Optional[int] = None
    offset: Optional[int] = None
    orders: Optional[Dict[CampaignSortField, Literal["ASC", "DESC"]]] = None
    filters: Optional[CampaignFilterField] = None

    has_message: Optional[bool] = None
    has_message_content: Optional[bool] = None
    has_form: Optional[bool] = None
    campaignListing: Optional[int] = None
    status: Optional[CampaignStatus] = None
    excludeTypes: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True, populate_by_alias=True)


class AutomationListParams(BaseModel):
    limit: Optional[int] = None
    offset: Optional[int] = None

    filters: Optional[AutomationFilterField] = None
    orders: Optional[Dict[AutomationSortField, Literal["ASC", "DESC"]]] = None

    label: Optional[int] = None
    search: Optional[str] = None
    active: Optional[bool] = None
    has_message: Optional[bool] = None

    enhance: Optional[bool] = None

    model_config = ConfigDict(populate_by_name=True, populate_by_alias=True)


class ContactAutomationListParams(BaseModel):
    limit: Optional[int] = None
    offset: Optional[int] = None

    filters: Optional[ContactAutomationFilters] = None

    orders: Optional[Dict[ContactAutomationSortField, Literal["ASC", "DESC"]]] = None

    q: Optional[str] = None

    min_time: Optional[int] = None
    max_time: Optional[int] = None

    tags: Optional[List[int]] = Field(None, alias="tags[]")
    g_tagid: Optional[int] = None
    g_tags: Optional[List[int]] = Field(None, alias="g_tags[]")

    lists: Optional[List[int]] = Field(None, alias="lists[]")
    g_listid: Optional[int] = None
    g_lists: Optional[List[int]] = Field(None, alias="g_lists[]")

    g_id: Optional[int] = None
    g_status: Optional[Literal[0, 1]] = None
    g_min_time: Optional[int] = None
    g_max_time: Optional[int] = None

    scoreid: Optional[int] = None

    include: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True, populate_by_alias=True)


class ContactAutomationCreateParams(BaseModel):
    contact: int
    automation: int


class GroupListParams(BaseModel):
    limit: Optional[int] = None
    offset: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True, populate_by_alias=True)


class ListListParams(BaseModel):
    limit: Optional[int] = None
    offset: Optional[int] = None
    filters: Optional[ListFilters] = None
    orders: Optional[ListOrders] = None

    model_config = ConfigDict(populate_by_name=True, populate_by_alias=True)


class ListGroupPermissionParams(BaseModel):
    listid: int
    groupid: int


class ContactListUpdateParams(BaseModel):
    contact: int
    list: int
    status: int


class ListCreateParams(BaseModel):
    name: str
    channel: Optional[Literal["email", "sms"]] = "email"
    sender_url: str = None
    sender_reminder: str = None
    send_last_broadcast: Optional[int] = 0
    carboncopy: Optional[str] = ""
    subscription_notify: Optional[str] = ""
    unsubscription_notify: Optional[str] = ""


class ListUpdateParams(BaseModel):
    name: str = None
    sender_url: str = None
    sender_reminder: str = None
    send_last_broadcast: Optional[int] = 0
    carboncopy: Optional[str] = ""
    subscription_notify: Optional[str] = ""
    unsubscription_notify: Optional[str] = ""
