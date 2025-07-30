from jupyter_server.auth.identity import User
from ..identity import SagemakerIdentityProvider
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def handler_mock():
    return MagicMock()


def test_get_user_with_cookie(handler_mock):
    handler_mock.get_cookie.return_value = "UserName"
    sm_provider = SagemakerIdentityProvider()
    user = sm_provider.get_user(handler_mock)
    expected_user = User("UserName", "UserName", "UserName", "U", None, None)
    assert user == expected_user


def test_get_user_without_cookie(handler_mock):
    handler_mock.get_cookie.return_value = None
    sm_provider = SagemakerIdentityProvider()
    user = sm_provider.get_user(handler_mock)
    expected_user = User("User", "User", "User", "U", None, None)
    assert user == expected_user
