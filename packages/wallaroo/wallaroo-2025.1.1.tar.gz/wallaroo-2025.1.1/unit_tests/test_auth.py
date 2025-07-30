import pytest
from wallaroo import auth

import requests
import responses

import datetime
import pathlib
import tempfile
import unittest
from unittest import mock

JWT = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJMMVBlNC0tSEo0TjMzelFqcHBfTEJQUUIzbHZ3UUQ4UDc2cUlqcFNHazZZIn0.eyJleHAiOjE2NDM5MDMwNzYsImlhdCI6MTY0MzkwMzAxNiwiYXV0aF90aW1lIjoxNjQzOTAxMDMzLCJqdGkiOiJmZmNlMjIyYS1jOGJjLTQ3M2QtYmNhYS0zYTM2YWQ0ZWJhMjAiLCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjkwOTAvYXV0aC9yZWFsbXMvbWFzdGVyIiwiYXVkIjpbIm1hc3Rlci1yZWFsbSIsImFjY291bnQiXSwic3ViIjoiNTkwNWMxNGYtYzcwZC00YWZiLWExZWMtOGZhNjllOGU1ZjM1IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoic2RrLWNsaWVudCIsInNlc3Npb25fc3RhdGUiOiIxNzA3YjBiMS0xYzAzLTQ2OGQtYTVhNy1hNzZkODBlNjk1YzYiLCJhY3IiOiIwIiwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbImRlZmF1bHQtcm9sZXMtbWFzdGVyIiwib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7Im1hc3Rlci1yZWFsbSI6eyJyb2xlcyI6WyJ2aWV3LXVzZXJzIiwicXVlcnktZ3JvdXBzIiwicXVlcnktdXNlcnMiXX0sImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoiZW1haWwgcHJvZmlsZSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiaHR0cHM6Ly9oYXN1cmEuaW8vand0L2NsYWltcyI6eyJ4LWhhc3VyYS11c2VyLWlkIjoiNTkwNWMxNGYtYzcwZC00YWZiLWExZWMtOGZhNjllOGU1ZjM1IiwieC1oYXN1cmEtZGVmYXVsdC1yb2xlIjoidXNlciIsIngtaGFzdXJhLWFsbG93ZWQtcm9sZXMiOlsidXNlciJdLCJ4LWhhc3VyYS11c2VyLWdyb3VwcyI6Int9In0sIm5hbWUiOiJLZWl0aCBMb2huZXMiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJrcmxvaG5lcyIsImdpdmVuX25hbWUiOiJLZWl0aCIsImZhbWlseV9uYW1lIjoiTG9obmVzIiwiZW1haWwiOiJsb2huZXNrQGdtYWlsLmNvbSJ9.akPI9srL4WIWU8JO1qHg9D14GLGEtv_2DbVChSQ62Zs6dz92-J2HQPxwpBaoMp_gXN21WDBVl4ggVL7CSCRULp3Mcdn3ZnxKgaGr2UQEaM9tS7-fdXmld3eGy16bP0cywqrr78-w5A-Ko-wTJMr5VLPmduIthzkJVPlbR9i3bq3UmcRjoEiguJR_wez5yhaLBrFTVrUWeGyhqhAosZzdhPtWojKou_X9mTB4E2PP1Nmjoi4O3IDgZJ8VEP2fBwHpraWPN_pXbIcu_4CEfJinqanHfkVOtVSTdWxKSp4xXmvYgMApUEPP0PThHERch4uKqsstsaRCh24_AIvEq0bLPA"


def seconds_from_now(n: int) -> datetime.datetime:
    return datetime.datetime.now() + datetime.timedelta(seconds=n)


class TestKeycloakTokenFetcher:
    @responses.activate
    def test_fetch_tokenfetcherror_on_device_code_post_failure(self):
        # Request to Keycloak for device code fails with 404
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/auth/device",
            status=404,
        )

        token_fetcher = auth._KeycloakTokenFetcher(
            address="http://keycloak.wallaroo", realm="master", client_id="unit-tests"
        )
        with pytest.raises(auth.TokenFetchError):
            access_token = token_fetcher.Fetch()
            del access_token

        assert 1 == len(responses.calls)

    @responses.activate
    def test_fetch(self):
        # Request to Keycloak for device code succeeds
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/auth/device",
            status=200,
            json={
                "device_code": "H4NYOYjN8Ut9axie2c7jXte5qAWv7uO3Wlyraz1IhwQ",
                "user_code": "HEUR-GINT",
                "verification_uri": "http://keycloak.wallaroo/auth/realms/master/device",
                "verification_uri_complete": "http://keycloak.wallaroo/auth/realms/master/device?user_code=HEUR-GINT",
                "expires_in": 5,
                "interval": 0,
            },
        )
        # Poll for access_token for the corresponding device code succeeds immediately
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/token",
            status=200,
            json={
                "access_token": JWT,
                "expires_in": 60,
                "refresh_token": "refresh_token_data",
                "refresh_expires_in": 1800,
            },
        )

        token_fetcher = auth._KeycloakTokenFetcher(
            address="http://keycloak.wallaroo", realm="master", client_id="unit-tests"
        )
        access_token = token_fetcher.Fetch()

        assert JWT == access_token.token
        assert "refresh_token_data" == access_token.refresh_token
        assert 2 == len(responses.calls)

    @responses.activate
    def test_fetch_poll(self):
        # Request to Keycloak for device code succeeds
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/auth/device",
            status=200,
            json={
                "device_code": "H4NYOYjN8Ut9axie2c7jXte5qAWv7uO3Wlyraz1IhwQ",
                "user_code": "HEUR-GINT",
                "verification_uri": "http://keycloak.wallaroo/auth/realms/master/device",
                "verification_uri_complete": "http://keycloak.wallaroo/auth/realms/master/device?user_code=HEUR-GINT",
                "expires_in": 5,
                "interval": 0,
            },
        )
        # Multiple polls that report the user hasn't finished the auth flow yet
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/token",
            status=400,
            json={
                "error": "authorization_pending",
                "error_description": "The authorization request is still pending",
            },
        )
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/token",
            status=400,
            json={
                "error": "authorization_pending",
                "error_description": "The authorization request is still pending",
            },
        )
        # User finishes auth flow, and poll succeeds
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/token",
            status=200,
            json={
                "access_token": JWT,
                "expires_in": 60,
                "refresh_token": "refresh_token_data",
                "refresh_expires_in": 1800,
            },
        )

        token_fetcher = auth._KeycloakTokenFetcher(
            address="http://keycloak.wallaroo", realm="master", client_id="unit-tests"
        )
        access_token = token_fetcher.Fetch()
        assert JWT == access_token.token
        assert "refresh_token_data" == access_token.refresh_token
        assert 4 == len(responses.calls)

    @responses.activate
    def test_fetch_poll_slowdown(self):
        # Request to Keycloak for device code succeeds
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/auth/device",
            status=200,
            json={
                "device_code": "H4NYOYjN8Ut9axie2c7jXte5qAWv7uO3Wlyraz1IhwQ",
                "user_code": "HEUR-GINT",
                "verification_uri": "http://keycloak.wallaroo/auth/realms/master/device",
                "verification_uri_complete": "http://keycloak.wallaroo/auth/realms/master/device?user_code=HEUR-GINT",
                "expires_in": 5,
                "interval": 0,
            },
        )
        # Poll reports the user hasn't finished the auth flow yet
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/token",
            status=400,
            json={
                "error": "authorization_pending",
                "error_description": "The authorization request is still pending",
            },
        )
        # Client polls too quickly and receives a "slow_down", which it should tolerate
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/token",
            status=400,
            json={
                "error": "slow_down",
                "error_description": "Slow down",
            },
        )
        # User finishes auth flow, and poll succeeds
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/token",
            status=200,
            json={
                "access_token": JWT,
                "expires_in": 60,
                "refresh_token": "refresh_token_data",
                "refresh_expires_in": 1800,
            },
        )

        token_fetcher = auth._KeycloakTokenFetcher(
            address="http://keycloak.wallaroo", realm="master", client_id="unit-tests"
        )
        access_token = token_fetcher.Fetch()
        assert JWT == access_token.token
        assert "refresh_token_data" == access_token.refresh_token
        assert 4 == len(responses.calls)

    @responses.activate
    def test_refresh_token_not_expired(self):
        token = auth._AccessToken(
            token=JWT,
            expiry=seconds_from_now(15),
            refresh_token="refresh_token_1_data",
            refresh_token_expiry=seconds_from_now(30),
            user_id="some_user_id",
            user_email="meynard@tool.com",
        )
        token_fetcher = auth._KeycloakTokenFetcher(
            address="http://keycloak.wallaroo", realm="master", client_id="unit-tests"
        )

        new_token = token_fetcher.Refresh(token)

        assert token == new_token

    @responses.activate
    def test_refresh_token_expired(self):
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/token",
            status=200,
            json={
                "access_token": JWT,
                "expires_in": 60,
                "refresh_token": "new_refresh_token_data",
                "refresh_expires_in": 1800,
            },
        )
        token = auth._AccessToken(
            token=JWT,
            expiry=seconds_from_now(-1),
            refresh_token="refresh_token_1_data",
            refresh_token_expiry=seconds_from_now(10),
            user_id="some_user_id",
            user_email="mao@ccp.cn",
        )
        token_fetcher = auth._KeycloakTokenFetcher(
            address="http://keycloak.wallaroo", realm="master", client_id="unit-tests"
        )

        new_token = token_fetcher.Refresh(token)

        assert JWT == new_token.token
        assert "new_refresh_token_data" == new_token.refresh_token
        assert 1 == len(responses.calls)

    @responses.activate
    def test_refresh_token_error(self):
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/token",
            status=400,
            json={
                "error": "some_error",
                "error_description": "unknown error",
            },
        )
        token = auth._AccessToken(
            token=JWT,
            expiry=seconds_from_now(-1),
            refresh_token="refresh_token_1_data",
            refresh_token_expiry=seconds_from_now(10),
            user_id="some_user_id",
            user_email="rms@fsf.org",
        )
        token_fetcher = auth._KeycloakTokenFetcher(
            address="http://keycloak.wallaroo", realm="master", client_id="unit-tests"
        )

        with pytest.raises(auth.TokenRefreshError):
            new_token = token_fetcher.Refresh(token)
            del new_token


class TestNoAuth:
    def test_call(self):
        a = auth._NoAuth()
        req = requests.Request("GET", "http://api-lb.wallaroo/v1/graphql").prepare()

        new_req = a(req)

        assert new_req == req


class TestPlatformAuth:
    @responses.activate
    def test_call(self):
        # Request to Keycloak for device code succeeds
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/auth/device",
            status=200,
            json={
                "device_code": "H4NYOYjN8Ut9axie2c7jXte5qAWv7uO3Wlyraz1IhwQ",
                "user_code": "HEUR-GINT",
                "verification_uri": "http://keycloak.wallaroo/auth/realms/master/device",
                "verification_uri_complete": "http://keycloak.wallaroo/auth/realms/master/device?user_code=HEUR-GINT",
                "expires_in": 5,
                "interval": 0,
            },
        )
        # Poll for access_token for the corresponding device code succeeds immediately
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/token",
            status=200,
            json={
                "access_token": JWT,
                "expires_in": 60,
                "refresh_token": "refresh_token_data",
                "refresh_expires_in": 1800,
            },
        )
        a = auth._PlatformAuth(
            fetcher=auth._KeycloakTokenFetcher(
                address="http://keycloak.wallaroo",
                realm="master",
                client_id="unit-tests",
            )
        )
        # Creation of the above auth object should not trigger any requests.
        assert 0 == len(responses.calls)

        req = requests.Request("GET", "http://api-lb.wallaroo/v1/graphql").prepare()
        new_req = a(req)

        # Fetch triggered
        assert 2 == len(responses.calls)

        assert f"Bearer {JWT}" == new_req.headers["Authorization"]

    @responses.activate
    def test_call_with_refresh(self):
        # Request to Keycloak for device code succeeds
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/auth/device",
            status=200,
            json={
                "device_code": "H4NYOYjN8Ut9axie2c7jXte5qAWv7uO3Wlyraz1IhwQ",
                "user_code": "HEUR-GINT",
                "verification_uri": "http://keycloak.wallaroo/auth/realms/master/device",
                "verification_uri_complete": "http://keycloak.wallaroo/auth/realms/master/device?user_code=HEUR-GINT",
                "expires_in": 5,
                "interval": 0,
            },
        )
        # Poll for access_token for the corresponding device code succeeds
        # immediately, with an old token
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/token",
            status=200,
            json={
                "access_token": JWT,
                "expires_in": -1,
                "refresh_token": "refresh_token_data",
                "refresh_expires_in": 1800,
            },
        )
        # Refresh response for token
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/token",
            status=200,
            json={
                "access_token": JWT,
                "expires_in": 60,
                "refresh_token": "new_refresh_token_data",
                "refresh_expires_in": 1800,
            },
        )
        a = auth._PlatformAuth(
            fetcher=auth._KeycloakTokenFetcher(
                address="http://keycloak.wallaroo",
                realm="master",
                client_id="unit-tests",
            )
        )
        # Creation of the above auth object should not trigger any requests.
        assert 0 == len(responses.calls)

        req = requests.Request("GET", "http://api-lb.wallaroo/v1/graphql").prepare()
        new_req = a(req)

        # Fetch triggered
        assert 3 == len(responses.calls)
        assert f"Bearer {JWT}" == new_req.headers["Authorization"]

    @responses.activate
    def test_call_with_refresh_error(self):
        # Request to Keycloak for device code succeeds
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/auth/device",
            status=200,
            json={
                "device_code": "H4NYOYjN8Ut9axie2c7jXte5qAWv7uO3Wlyraz1IhwQ",
                "user_code": "HEUR-GINT",
                "verification_uri": "http://keycloak.wallaroo/auth/realms/master/device",
                "verification_uri_complete": "http://keycloak.wallaroo/auth/realms/master/device?user_code=HEUR-GINT",
                "expires_in": 5,
                "interval": 0,
            },
        )
        # Poll for access_token for the corresponding device code succeeds
        # immediately, with an old token and old refresh token
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/token",
            status=200,
            json={
                "access_token": JWT,
                "expires_in": -1,
                "refresh_token": "refresh_token_data",
                "refresh_expires_in": -1,
            },
        )
        # Second poll for access_token for the corresponding device code
        # succeeds immediately, with a fresh token
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/token",
            status=200,
            json={
                "access_token": JWT,
                "expires_in": 5,
                "refresh_token": "new_refresh_token_data",
                "refresh_expires_in": 5,
            },
        )

        a = auth._PlatformAuth(
            fetcher=auth._KeycloakTokenFetcher(
                address="http://keycloak.wallaroo",
                realm="master",
                client_id="unit-tests",
            )
        )
        # Creation of the above auth object should not trigger any requests.
        assert 0 == len(responses.calls)

        req = requests.Request("GET", "http://api-lb.wallaroo/v1/graphql").prepare()
        new_req = a(req)

        # Device code fetch, access token fetch (pre-expired), device code
        # fetch, access token fetch
        assert 4 == len(responses.calls)
        assert f"Bearer {JWT}" == new_req.headers["Authorization"]

    @responses.activate
    def test_call_cached(self):
        # Request to Keycloak for device code succeeds
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/auth/device",
            status=200,
            json={
                "device_code": "H4NYOYjN8Ut9axie2c7jXte5qAWv7uO3Wlyraz1IhwQ",
                "user_code": "HEUR-GINT",
                "verification_uri": "http://keycloak.wallaroo/auth/realms/master/device",
                "verification_uri_complete": "http://keycloak.wallaroo/auth/realms/master/device?user_code=HEUR-GINT",
                "expires_in": 5,
                "interval": 0,
            },
        )
        # Poll for access_token for the corresponding device code succeeds immediately
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/token",
            status=200,
            json={
                "access_token": JWT,
                "expires_in": 60,
                "refresh_token": "refresh_token_data",
                "refresh_expires_in": 1800,
            },
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            a = auth._PlatformAuth(
                fetcher=auth._CachedTokenFetcher(
                    path=pathlib.Path(tmpdir) / "auth.json",
                    fetcher=auth._KeycloakTokenFetcher(
                        address="http://keycloak.wallaroo",
                        realm="master",
                        client_id="unit-tests",
                    ),
                )
            )
            # Creation of the above auth object should trigger a fetch
            assert 2 == len(responses.calls)
            responses.reset()

            req = requests.Request("GET", "http://api-lb.wallaroo/v1/graphql").prepare()
            new_req = a(req)

            assert f"Bearer {JWT}" == new_req.headers["Authorization"]
            # Token is cached; no need to perform any fetches
            assert 0 == len(responses.calls)

            a = auth._PlatformAuth(
                fetcher=auth._CachedTokenFetcher(
                    path=pathlib.Path(tmpdir) / "auth.json",
                    fetcher=auth._KeycloakTokenFetcher(
                        address="http://keycloak.wallaroo",
                        realm="master",
                        client_id="unit-tests",
                    ),
                )
            )
            # Token is still cached; no need to perform any fetches
            assert 0 == len(responses.calls)
            req = requests.Request("GET", "http://api-lb.wallaroo/v1/graphql").prepare()
            new_req = a(req)
            assert 0 == len(responses.calls)


class TestCachedTokenFetcher:
    def test_fetch_on_init(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fetcher = mock.MagicMock(spec=auth._TokenFetcher)
            fetcher.Fetch.return_value = auth._AccessToken(
                token=JWT,
                expiry=seconds_from_now(1),
                refresh_token="refresh_token_data",
                refresh_token_expiry=seconds_from_now(1),
                user_id="some_user_id",
                user_email="larry@oracle.com",
            )
            cached_fetcher = auth._CachedTokenFetcher(
                path=pathlib.Path(tmpdir) / "auth.json", fetcher=fetcher
            )

            assert 1 == fetcher.Fetch.call_count


class TestPasswordTokenFetcher:
    @responses.activate
    def test_fetch_success(self):
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/token",
            status=200,
            json={
                "access_token": JWT,
                "expires_in": 5,
                "refresh_token": "refresh_token_data",
                "refresh_expires_in": 5,
            },
        )
        token_fetcher = auth._PasswordTokenFetcher(
            address="http://keycloak.wallaroo",
            realm="master",
            client_id="unit-tests",
            username="some-user",
            password="some-password",
        )

        token = token_fetcher.Fetch()

        assert JWT == token.token
        assert "refresh_token_data" == token.refresh_token
        assert 1 == len(responses.calls)

    @responses.activate
    def test_fetch_fail(self):
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/token",
            status=401,
            json={
                "error": "invalid_grant",
                "error_description": "Invalid user credentials",
            },
        )
        token_fetcher = auth._PasswordTokenFetcher(
            address="http://keycloak.wallaroo",
            realm="master",
            client_id="unit-tests",
            username="some-user",
            password="some-password",
        )

        with pytest.raises(auth.TokenFetchError):
            token = token_fetcher.Fetch()
            del token

    @responses.activate
    def test_refresh_token_not_expired(self):
        token = auth._AccessToken(
            token=JWT,
            expiry=seconds_from_now(15),
            refresh_token="refresh_token_1_data",
            refresh_token_expiry=seconds_from_now(30),
            user_id="some_user_id",
            user_email="billg@msncom",
        )
        token_fetcher = auth._PasswordTokenFetcher(
            address="http://keycloak.wallaroo",
            realm="master",
            client_id="unit-tests",
            username="some-user",
            password="some-password",
        )

        new_token = token_fetcher.Refresh(token)

        assert token == new_token

    @responses.activate
    def test_refresh_token_expired(self):
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/token",
            status=200,
            json={
                "access_token": JWT,
                "expires_in": 60,
                "refresh_token": "new_refresh_token_data",
                "refresh_expires_in": 1800,
            },
        )
        token = auth._AccessToken(
            token="token_1_data",
            expiry=seconds_from_now(-1),
            refresh_token="refresh_token_1_data",
            refresh_token_expiry=seconds_from_now(10),
            user_id="some_user_id",
            user_email="vid@wallaroo.ai",
        )
        token_fetcher = auth._PasswordTokenFetcher(
            address="http://keycloak.wallaroo",
            realm="master",
            client_id="unit-tests",
            username="some-user",
            password="some-password",
        )

        new_token = token_fetcher.Refresh(token)

        assert JWT == new_token.token
        assert "new_refresh_token_data" == new_token.refresh_token
        assert 1 == len(responses.calls)

    @responses.activate
    def test_refresh_token_error(self):
        responses.add(
            responses.POST,
            "http://keycloak.wallaroo/auth/realms/master/protocol/openid-connect/token",
            status=400,
            json={
                "error": "some_error",
                "error_description": "unknown error",
            },
        )
        token = auth._AccessToken(
            token="token_1_data",
            expiry=seconds_from_now(-1),
            refresh_token="refresh_token_1_data",
            refresh_token_expiry=seconds_from_now(10),
            user_id="some_user_id",
            user_email="obama@wh.gov",
        )
        token_fetcher = auth._PasswordTokenFetcher(
            address="http://keycloak.wallaroo",
            realm="master",
            client_id="unit-tests",
            username="some-user",
            password="some-password",
        )

        with pytest.raises(auth.TokenRefreshError):
            new_token = token_fetcher.Refresh(token)
            del new_token


if __name__ == "__main__":
    unittest.main()
