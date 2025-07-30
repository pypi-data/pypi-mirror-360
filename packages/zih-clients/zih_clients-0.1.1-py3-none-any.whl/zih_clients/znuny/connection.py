# SPDX-License-Identifier: MIT

"""Connection interface for the Znuny ticket system"""

from typing import Any, cast

from httpx import Client, HTTPError, Response

from .types import ZnunyException


def _raise_for_status(response: Response) -> None:
    try:
        response.raise_for_status()
    except HTTPError as e:
        if (
            resp := getattr(e, "response", None)
        ) is not None and resp.status_code == 500:
            raise ZnunyException(
                "Internal Server Error when talking to Znuny; "
                "note that this might also be lacking permissions "
                "when a new queue was configured."
            ) from e
        raise


class Connection:
    """Connection interface for the Znuny ticket system"""

    def __init__(
        self,
        base_url: str,
        user: str,
        password: str,
        *,
        client: Client | None = None,
    ):
        if client is None:
            client = Client()

        self._base_url = base_url
        self._user = user
        self._password = password
        self._client = client
        self._client.headers.update(
            {
                "X-OTRS-Header-UserLogin": self._user,
                "X-OTRS-Header-Password": self._password,
            }
        )

    def create_ticket(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new ticket

        Args:
            data: a dict containing the needed ticket and article data

        Returns:
            the decoded backend response

        """
        webservice_url = f"{self._base_url}/Ticket/"
        response = self._client.post(webservice_url, json=data)
        _raise_for_status(response)
        return cast(dict[str, Any], response.json())

    def update_ticket(
        self, ticket_id: int, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update an existing ticket

        Args:
            data: a dict containing the needed ticket data

        Returns:
            the decoded backend response

        """
        webservice_url = f"{self._base_url}/Ticket/{ticket_id}/"
        response = self._client.patch(webservice_url, json=data)
        _raise_for_status(response)
        return cast(dict[str, Any], response.json())
