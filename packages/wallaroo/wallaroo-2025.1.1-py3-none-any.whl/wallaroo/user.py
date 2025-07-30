from typing import TYPE_CHECKING, Any, Dict

from wallaroo.http_utils import _get_base_headers, _make_post_request
from wallaroo.utils import _unwrap

from .object import UserLimitError

if TYPE_CHECKING:
    # Imports that happen below in methods to fix circular import dependency
    # issues need to also be specified here to satisfy mypy type checking.
    from .client import Client


class User:
    """A platform User."""

    def __init__(self, client, data: Dict[str, Any]) -> None:
        self.client = client
        self._id = data["id"]
        self._email = data["email"] if "email" in data else "admin@keycloak"
        self._username = data["username"]
        self._enabled = data["enabled"]
        self._createdTimeastamp = data["createdTimestamp"]

    def __repr__(self):
        return f"""User({{"id": "{self.id()}", "email": "{self.email()}", "username": "{self.username()}", "enabled": "{self.enabled()}")"""

    def id(self) -> str:
        return self._id

    def email(self) -> str:
        return self._email

    def username(self) -> str:
        return self._username

    def enabled(self) -> bool:
        return self._enabled

    @staticmethod
    def list_users(
        auth_token,
        api_endpoint: str = "http://api-lb:8080",
    ):
        headers = _get_base_headers(auth_token=auth_token)
        users = _make_post_request(
            api_endpoint=api_endpoint,
            path="v1/api/users/query",
            headers=headers,
            json={},
        )

        if users.status_code > 299:
            raise Exception("Failed to list exiting users.")
        return users.json()["users"].values()

    @staticmethod
    def get_email_by_id(
        client: "Client",
        id: str,
    ):
        from wallaroo.wallaroo_ml_ops_api_client.api.user.users_query import (
            UsersQueryBody,
            sync_detailed,
        )
        from wallaroo.wallaroo_ml_ops_api_client.models.users_query_response_200 import (
            UsersQueryResponse200,
        )

        r = sync_detailed(client=client.mlops(), body=UsersQueryBody([id]))

        if isinstance(r.parsed, UsersQueryResponse200):
            return _unwrap(r.parsed.users[id])["email"]

        raise Exception("Failed to get user information.", r)

    @staticmethod
    def invite_user(
        email,
        password,
        auth,
        api_endpoint: str = "http://api-lb:8080",
    ):
        # TODO: Refactor User.list_users() here when this stabilizes

        headers = _get_base_headers(auth_token=auth._bearer_token_str())
        users = _make_post_request(
            api_endpoint=api_endpoint,
            path="/v1/api/users/query",
            headers=headers,
            json={},
        )
        if users.status_code > 299:
            print(users.content)
            print(users.text)
            raise Exception("Failed to list existing users.")
        existing_users = users.json()["users"].values()
        user_present = [user for user in existing_users if user["username"] == email]
        if len(user_present) == 0:
            data = {"email": email}
            if password:
                data["password"] = password

            response = _make_post_request(
                api_endpoint=api_endpoint,
                path="/v1/api/users/invite",
                headers=headers,
                json=data,
            )
            if response.status_code == 403:
                raise UserLimitError()
            if response.status_code != 200:
                raise Exception("Failed to invite user")

            user = response.json()
            return user
        else:
            return user_present[0]
