# SPDX-License-Identifier: MIT

"""Tests for Znuny models"""

from unittest import TestCase
from unittest.mock import Mock, patch

from typing_extensions import override

from .connection import Connection
from .manager import TicketManager
from .models import (
    Article,
    Boolean,
    CommunicationChannel,
    QueueID,
    SenderType,
    Ticket,
    TicketPriority,
    TicketState,
    TicketType,
    TicketUpdate,
)


class TestModels(TestCase):
    """Testcases for Znuny models"""

    test_title = "Testticket"
    test_body = "Dies ist ein Testticket."
    test_queue_id = QueueID.CIDS_DIENSTEENTWICKLUNG_SOFTWAREENTWICKLUNG
    test_customer = "testcustomer"
    test_to = "testcustomer@tu-dresden.de"

    @override
    def setUp(self) -> None:
        """Set up each test"""
        self.test_ticket = Ticket.model_construct(
            ticket_id=42,
            title=self.test_title,
            queue_id=self.test_queue_id,
            customer_user=self.test_customer,
        )
        self.test_article = Article.model_construct(
            subject=self.test_title, body=self.test_body, to=self.test_to
        )

    def test_create_ticket(self) -> None:
        """Create a ticket"""
        client_mock = Mock()
        response_mock = Mock()
        response_mock.json = Mock(
            return_value={"Ticket": self.test_ticket.model_dump(by_alias=True)}
        )
        client_mock.post = Mock(return_value=response_mock)
        connection_mock = Connection(
            "test_url", "test_user", "test_password", client=client_mock
        )
        manager = TicketManager(connection_mock)
        returned_ticket = manager.create(
            queue_id=self.test_queue_id,
            customer=self.test_customer,
            title=self.test_title,
            body=self.test_body,
            to=self.test_to,
        )
        self.assertIsNotNone(returned_ticket)
        self.assertEqual(self.test_ticket, returned_ticket)

    def test_create_and_move_ticket(self) -> None:
        """Create a ticket"""
        connection_mock = Mock()
        connection_mock.create_ticket = Mock(
            return_value={"Ticket": self.test_ticket.model_dump(by_alias=True)}
        )
        connection_mock.update_ticket = Mock(return_value={})
        manager = TicketManager(connection_mock)
        returned_ticket = manager.create_and_move(
            queue_id=self.test_queue_id,
            customer=self.test_customer,
            title=self.test_title,
            body=self.test_body,
            to=self.test_to,
        )
        self.assertEqual(self.test_ticket, returned_ticket)
        connection_mock.update_ticket.assert_called_once_with(
            42,
            {
                "Ticket": {
                    "QueueID": self.test_queue_id,
                },
            },
        )

    def test_update_ticket(self) -> None:
        """Update a ticket"""
        connection = Mock()
        connection.update_ticket = Mock(return_value={})
        manager = TicketManager(connection)
        ticket = TicketUpdate.model_construct(queue_name="Some::Queue")
        manager.update(
            ticket_id=42,
            ticket=ticket,
        )
        connection.update_ticket.assert_called_once_with(
            42,
            {
                "Ticket": {
                    "Queue": "Some::Queue",
                },
            },
        )

    def test_call_model_with_sender_type(self) -> None:
        """Test the new sender type"""
        client_mock = Mock()
        response_mock = Mock()
        response_mock.json = Mock(
            return_value={"Ticket": self.test_ticket.model_dump(by_alias=True)}
        )
        client_mock.post = Mock(return_value=response_mock)
        connection_mock = Connection(
            "test_url", "test_user", "test_password", client=client_mock
        )
        with patch(
            "zih_clients.znuny.connection.Connection.create_ticket",
        ) as create_ticket_mock:
            create_ticket_mock.return_value = {"Ticket": self.test_ticket}

            manager = TicketManager(connection_mock)
            _ = manager.create(
                queue_id=self.test_queue_id,
                customer=self.test_customer,
                title=self.test_title,
                body=self.test_body,
                to=self.test_to,
                sender_type=SenderType.CUSTOMER,
                CommunicationChannelID=CommunicationChannel.PHONE,
            )

            create_ticket_mock.assert_called_once_with(
                {
                    "Ticket": {
                        "Title": "Testticket",
                        "QueueID": QueueID.CIDS_DIENSTEENTWICKLUNG_SOFTWAREENTWICKLUNG,
                        "StateID": TicketState.NEW,
                        "PriorityID": TicketPriority.NORMAL,
                        "TypeID": TicketType.SERVICE_REQUEST,
                        "CustomerUser": "testcustomer",
                    },
                    "Article": {
                        "Subject": "Testticket",
                        "Body": "Dies ist ein Testticket.",
                        "CommunicationChannelID": CommunicationChannel.PHONE,
                        "To": "testcustomer@tu-dresden.de",
                        "ContentType": "text/html; charset=utf-8",
                        "HistoryType": "SystemRequest",
                        "TimeUnit": 0,
                        "ArticleSend": Boolean.TRUE,
                        "IsVisibleForCustomer": Boolean.TRUE,
                        "NoAgentNotify": Boolean.TRUE,
                        "SenderTypeID": SenderType.CUSTOMER,
                        "AutoSign": Boolean.TRUE,
                    },
                }
            )
