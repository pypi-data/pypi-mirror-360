# SPDX-License-Identifier: MIT

from logging import getLogger
from typing import Any, Union

from .connection import Connection
from .models import (
    Article,
    Attachment,
    DynamicFieldName,
    QueueID,
    ServiceID,
    ServiceName,
    Ticket,
    TicketUpdate,
)
from .types import ZnunyException

logger = getLogger(__name__)


def _serialize(
    attachment: Union["Attachment", list["Attachment"], None] = None,
) -> dict[str, Any] | list[dict[str, Any]] | None:
    match attachment:
        case Attachment():
            return attachment.model_dump(by_alias=True)
        case list():
            return [a.model_dump(by_alias=True) for a in attachment]
        case _:
            return None


class TicketManager:
    """Manager for ticket objects"""

    def __init__(
        self,
        connection: Connection,
        *,
        temporary_queue_id: QueueID = QueueID.AUTOMAT_SSP,
    ):
        self._connection = connection
        self._temporary_queue_id = temporary_queue_id

    # pylint: disable=too-many-arguments,too-many-locals
    def create(
        self,
        *,
        queue_id: QueueID | None = None,
        queue_name: str | None = None,
        customer: str,
        title: str,
        body: str,
        to: str,  # pylint: disable=invalid-name
        dynamic_fields: dict[DynamicFieldName | str, Any] | None = None,
        attachment: Union["Attachment", list["Attachment"], None] = None,
        service_id: ServiceID | None = None,
        service_name: ServiceName | None = None,
        **kwargs: Any,
    ) -> "Ticket":
        """Return a newly created ticket

        Exactly one of queue_id and queue_name must be specified.

        Args:
            queue_id: QueueID to position ticket into
            queue_name: Name of queue to position ticket into
            customer: ZIH-Login the ticket will be linked to
            title: title of the new ticket and first article
            body: content of the first ticket article
            to: email address the first article will be sent to
            dynamic_fields: dictionary of dynamic fields to set for the ticket

        Returns:
            the newly created :class:`Ticket`

        Raises:
            :class:`ZnunyException` if there was an error creating the ticket

        """
        if queue_id is None and queue_name is None:
            raise ValueError("Must specify one of queue_id or queue_name")
        if queue_id is not None and queue_name is not None:
            raise ValueError("Cannot specify both queue_id and queue_name")
        if service_id is not None and service_name is not None:
            raise ValueError("Cannot specify both service_id and service_name")

        if queue_id is not None:
            kwargs["QueueID"] = queue_id
        if queue_name is not None:
            kwargs["Queue"] = queue_name

        if service_id is not None:
            kwargs["ServiceID"] = service_id
        if service_name is not None:
            kwargs["Service"] = service_name

        ticket = Ticket.model_construct(
            title=title, customer_user=customer, **kwargs
        )
        article = Article.model_construct(
            subject=title, body=body, to=to, **kwargs
        )
        params: dict[str, Any] = {
            "Ticket": ticket.model_dump(by_alias=True, exclude_none=True),
            "Article": article.model_dump(by_alias=True, exclude_none=True),
        }
        if dynamic_fields:
            params["DynamicField"] = [
                {"Name": key, "Value": value}
                for key, value in dynamic_fields.items()
            ]
        if raw_attachment := _serialize(attachment):
            params["Attachment"] = raw_attachment
        response_dict = self._connection.create_ticket(params)
        if "Error" in response_dict:
            error = response_dict["Error"]
            logger.error("Could not create ticket: %s", error["ErrorMessage"])
            raise ZnunyException(error["ErrorMessage"])
        return Ticket.model_validate(response_dict["Ticket"])

    def update(
        self,
        ticket_id: int,
        *,
        ticket: "TicketUpdate | None" = None,
        article: "Article | None" = None,
        attachment: Union["Attachment", list["Attachment"], None] = None,
    ) -> None:
        """Update existing ticket"""
        kwargs: dict[str, Any] = {}
        if ticket is None and article is None:
            raise ValueError("At least one of ticket and article is required")
        if ticket is not None:
            kwargs["Ticket"] = ticket.model_dump(
                by_alias=True, exclude_none=True
            )
        if article is not None:
            kwargs["Article"] = article.model_dump(
                by_alias=True, exclude_none=True
            )
        if raw_attachment := _serialize(attachment):
            kwargs["Attachment"] = raw_attachment
        response = self._connection.update_ticket(ticket_id, kwargs)
        if (error := response.get("Error")) is not None:
            raise ZnunyException(error["ErrorMessage"])

    def create_and_move(
        self,
        *,
        queue_id: QueueID | None = None,
        queue_name: str | None = None,
        customer: str,
        title: str,
        body: str,
        to: str,  # pylint: disable=invalid-name
        dynamic_fields: dict[DynamicFieldName | str, Any] | None = None,
        service_id: ServiceID | None = None,
        service_name: ServiceName | None = None,
        **kwargs: Any,
    ) -> "Ticket":
        """Return a newly created ticket that is created add `ZIH::Intern::Self Service Portal::Outgoing`
        and than moved to given queue.

        Exactly one of queue_id and queue_name must be specified.

        Args:
            queue_id: QueueID to position ticket into
            queue_name: Name of queue to position ticket into
            customer: ZIH-Login the ticket will be linked to
            title: title of the new ticket and first article
            body: content of the first ticket article
            to: email address the first article will be sent to
            dynamic_fields: dictionary of dynamic fields to set for the ticket

        Returns:
            the newly created :class:`Ticket`

        Raises:
            :class:`ZnunyException` if there was an error creating the ticket

        """
        if queue_id is None and queue_name is None:
            raise ValueError("Must specify one of queue_id or queue_name")
        if queue_id is not None and queue_name is not None:
            raise ValueError("Cannot specify both queue_id and queue_name")
        if service_id is not None and service_name is not None:
            raise ValueError("Cannot specify both service_id and service_name")

        if service_id is not None:
            kwargs["ServiceID"] = service_id
        if service_name is not None:
            kwargs["Service"] = service_name

        ticket = self.create(
            queue_id=self._temporary_queue_id,
            customer=customer,
            title=title,
            body=body,
            to=to,
            dynamic_fields=dynamic_fields,
            **kwargs,
        )
        assert isinstance(ticket.ticket_id, int)
        if queue_id is not None:
            ticket_update = TicketUpdate.model_construct(queue_id=queue_id)
        if queue_name is not None:
            ticket_update = TicketUpdate.model_construct(queue_name=queue_name)
        self.update(ticket_id=ticket.ticket_id, ticket=ticket_update)
        return ticket

    def get_ticket_agent_url(self, ticket_id: int) -> str:
        """get URL to the agent view of the given ticket"""

        return (
            "https://tickets.tu-dresden.de/otrs/index.pl?"
            f"Action=AgentTicketZoom;TicketID={ticket_id}"
        )

    def get_ticket_customer_url(self, ticket_number: str) -> str:
        """get URL to the customer view of the given ticket"""

        return (
            "https://tickets.tu-dresden.de/otrs/customer.pl?"
            f"Action=CustomerTicketZoom;TicketNumber={ticket_number}"
        )
