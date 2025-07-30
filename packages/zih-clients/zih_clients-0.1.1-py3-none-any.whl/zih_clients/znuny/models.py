# SPDX-License-Identifier: MIT

"""Models for Znuny API calls"""

from enum import IntEnum, StrEnum
from logging import getLogger
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

logger = getLogger(__name__)


class ServiceID(IntEnum):
    """Enum for Service_IDs"""

    FIREWALL = 264
    SHAREPOINT = 112
    VIRTUAL_SERVER = 69
    GROUP_MANAGEMENT = 86
    POOL_RESERVATION = 98
    EXCHANGE_MAIL = 63
    INTRANET = 115


class Boolean(IntEnum):
    """Enum for int values used as bool in Znuny"""

    TRUE = 1
    FALSE = 0


class CommunicationChannel(IntEnum):
    """Enum for article communication channels"""

    EMAIL = 1
    PHONE = 2
    INTERNAL = 3
    CHAT = 4


class QueueID(IntEnum):
    """Enum for queue IDs"""

    CIDS_IT_BETRIEB_WINDOWS = 1047
    CIDS_SERVICEDESK = 1038
    CIDS = 1037
    CIDS_IT_BETRIEB_LINUX = 1046
    INFORMATIONSSICHERHEIT = 124
    CIDS_DIENSTEENTWICKLUNG_SOFTWAREENTWICKLUNG = 1052
    AUTOMAT_SSP = 1074
    CIDS_IT_BETRIEB_NETZ = 1048
    CIDS_IT_BETRIEB_BASISDIENSTE = 1045
    INTRANET = 1024


class TicketType(IntEnum):
    """Enum for ticket types"""

    UNCLASSIFIED = 1
    INCIDENT = 2
    SERVICE_REQUEST = 4
    PROBLEM = 5
    CHANGE_REQUEST = 6
    CONSULTING_SERVICE = 7


class TicketState(IntEnum):
    """Enum ticket states"""

    NEW = 1
    CONFIRM_ANSWER = 2
    IN_PROCESS = 3
    RESOLVED = 4
    REMOVED = 5
    WAITING_FOR_INFORMATION = 6
    CLOSED_WITHOUT_RESOLUTION = 7
    WAITING_FOR_EXTERNAL_SERVICE_PROVIDER = 8
    MERGED = 9
    CONFIRM_SOLUTION = 10
    IN_TEST = 11
    WAITING_FOR_RESUBMISSION = 12


class TicketPriority(IntEnum):
    """Enum for Znuny ticket priorities"""

    URGENT = 5
    HIGH = 4
    NORMAL = 3
    LOW = 1


class SenderType(IntEnum):
    "SenderType for Znuny article"

    AGENT = 1
    CUSTOMER = 3
    SYSTEM = 2


class DynamicFieldName(StrEnum):
    """names of dynamic fields"""

    REASON_FREETEXT = "ReasonFreetext"
    REASON_SELECTOR = "ReasonSelector"  # Anfragegrund


class ServiceName(StrEnum):
    """values of dynamic Category fields"""

    FIREWALL = "Firewall"
    SHAREPOINT = "Kollaborationstools::SharePoint"
    VIRTUAL_SERVER = "Virtualisierung"


class DynamicFieldValueReasonSelector(StrEnum):
    """values of dynamic ReasonSelector fields"""

    PROVISIONING = "04_Provisioning"


class PendingTime(BaseModel):
    """Pending time"""

    diff: Annotated[int, Field(alias="Diff")]


class Ticket(BaseModel):
    """Model for a Znuny ticket"""

    model_config = ConfigDict(populate_by_name=True)

    ticket_id: Annotated[
        int | None,
        Field(alias="TicketID"),
    ] = None
    ticket_number: Annotated[
        str | None,
        Field(alias="TicketNumber"),
    ] = None
    title: Annotated[
        str,
        Field(alias="Title"),
    ]
    queue_name: Annotated[
        str | None,
        Field(alias="Queue"),
    ] = None
    queue_id: Annotated[
        int | None,
        Field(alias="QueueID"),
    ] = None
    state_id: Annotated[
        TicketState,
        Field(alias="StateID"),
    ] = TicketState.NEW
    priority_id: Annotated[
        TicketPriority,
        Field(alias="PriorityID"),
    ] = TicketPriority.NORMAL
    type_id: Annotated[
        TicketType,
        Field(alias="TypeID"),
    ] = TicketType.SERVICE_REQUEST
    customer_user: Annotated[
        str | None,
        Field(alias="CustomerUser"),
    ] = None
    customer_user_id: Annotated[
        str | None,
        Field(alias="CustomerUserID"),
    ] = None
    service: Annotated[
        str | None,
        Field(alias="Service"),
    ] = None
    service_id: Annotated[
        int | None,
        Field(alias="ServiceID"),
    ] = None

    @classmethod
    @model_validator(mode="before")
    def check_queue_or_id_given(cls, values: dict[str, Any]) -> None:
        """Check if either Queue or QueueID is given"""
        if values.get("queue_name") is None and values.get("queue_id") is None:
            raise AssertionError("Either 'Queue' or 'QueueID' must be given.")


class TicketUpdate(BaseModel):
    """Model for update to Znuny ticket"""

    model_config = ConfigDict(populate_by_name=True)

    queue_name: Annotated[
        str | None,
        Field(alias="Queue"),
    ] = None
    queue_id: Annotated[
        int | None,
        Field(alias="QueueID"),
    ] = None
    state_id: Annotated[
        TicketState | None,
        Field(alias="StateID"),
    ] = None
    pending_time: Annotated[
        PendingTime | None,
        Field(alias="PendingTime"),
    ] = None

    @classmethod
    @model_validator(mode="before")
    def check_only_one_of_queue_id_or_name_given(
        cls, values: dict[str, Any]
    ) -> None:
        """Check that at most one of queue_name and queue_id is specified"""
        if "queue_name" in values and "queue_id" in values:
            raise ValueError(
                "At most one of QueueID and Queue can be specified"
            )


class Attachment(BaseModel):
    """Model for a Znuny attachment"""

    model_config = ConfigDict(populate_by_name=True)

    content_b64: Annotated[
        str,
        Field(alias="Content"),
    ]
    content_type: Annotated[
        str,
        Field(alias="ContentType"),
    ]
    filename: Annotated[
        str,
        Field(alias="Filename"),
    ]


class Article(BaseModel):
    """Model for a Znuny article"""

    model_config = ConfigDict(populate_by_name=True)

    article_id: Annotated[
        int | None,
        Field(alias="ArticleID"),
    ] = None
    subject: Annotated[
        str,
        Field(alias="Subject"),
    ]
    body: Annotated[
        str,
        Field(alias="Body"),
    ]
    communication_channel_id: Annotated[
        CommunicationChannel,
        Field(alias="CommunicationChannelID"),
    ] = CommunicationChannel.EMAIL
    to: Annotated[
        str,
        Field(alias="To"),
    ]
    cc: Annotated[
        str | None,
        Field(alias="Cc"),
    ] = None
    bcc: Annotated[
        str | None,
        Field(alias="Bcc"),
    ] = None
    content_type: Annotated[
        str,
        Field(alias="ContentType"),
    ] = "text/html; charset=utf-8"
    history_type: Annotated[
        str | None,
        Field(alias="HistoryType"),
    ] = "SystemRequest"
    time_unit: Annotated[
        int,
        Field(alias="TimeUnit"),
    ] = 0
    send_article: Annotated[
        Boolean,
        Field(alias="ArticleSend"),
    ] = Boolean.TRUE
    visible_for_customer: Annotated[
        Boolean,
        Field(alias="IsVisibleForCustomer"),
    ] = Boolean.TRUE
    no_agent_notify: Annotated[
        Boolean,
        Field(alias="NoAgentNotify"),
    ] = Boolean.TRUE
    sender_type: Annotated[
        SenderType,
        Field(alias="SenderTypeID"),
    ] = SenderType.AGENT
    auto_sign: Annotated[
        Boolean | None,
        Field(alias="AutoSign"),
    ] = Boolean.TRUE
