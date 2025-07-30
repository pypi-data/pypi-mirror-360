# SPDX-License-Identifier: MIT

"""Tests for the Znuny Connection"""

from typing import Any
from unittest import TestCase
from unittest.mock import Mock

from httpx import HTTPError

from .connection import Connection


class TestConnection(TestCase):
    """Simple connection tests by mocking the session"""

    test_ticket_data: dict[str, dict[str, Any]] = {
        "Ticket": {
            "Title": "Testticket",
            "QueueID": 1,
            "CustomerUser": "testuser",
        },
        "Article": {
            "Subject": "Testticket",
            "Body": "Nur ein Testticket.",
            "To": "testuser@tu-dresden.de",
        },
    }

    client_mock = Mock()
    response_mock = Mock()

    def test_create_ticket(self) -> None:
        """create a ticket"""
        self.response_mock.status_code = 200
        self.response_mock.json = Mock(
            return_value={
                "Ticket": {
                    "Title": "Testticket",
                    "TicketID": 123,
                    "QueueID": 1,
                    "CustomerUser": "testuser",
                }
            }
        )
        self.client_mock.post = Mock(return_value=self.response_mock)
        connection = Connection(
            "fake_url", "fake_user", "fake_password", client=self.client_mock
        )
        connection.create_ticket(self.test_ticket_data)
        self.client_mock.post.assert_called_once_with(
            "fake_url/Ticket/", json=self.test_ticket_data
        )

    def test_create_ticket_raises(self) -> None:
        """ticket creation raises an HTTPError"""
        self.response_mock.status_code = 400
        self.response_mock.raise_for_status = Mock(
            side_effect=HTTPError("foo")
        )
        self.client_mock.post = Mock(return_value=self.response_mock)
        connection = Connection(
            "fake_url", "fake_user", "fake_password", client=self.client_mock
        )
        with self.assertRaises(HTTPError):
            connection.create_ticket(self.test_ticket_data)

    def test_update_ticket(self) -> None:
        """update a ticket"""
        self.client_mock.patch = Mock()
        connection = Connection(
            "fake_url", "fake_user", "fake_password", client=self.client_mock
        )
        self.test_ticket_data["Ticket"]["QueueID"] = 2
        connection.update_ticket(123456, self.test_ticket_data)
        self.client_mock.patch.assert_called_once_with(
            "fake_url/Ticket/123456/", json=self.test_ticket_data
        )
