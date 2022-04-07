"""
Define tests for the ldap mapper.
"""

import json

import pytest

from cluster_agent.identity.local_user.exceptions import LDAPError
from cluster_agent.identity.local_user.mappers import ldap
from cluster_agent.identity.local_user.settings import LOCAL_USER_SETTINGS


def test_configure__success(mocker, tweak_local_user_settings):
    """
    Test that an LDAP instance will ``configure()`` if settings are correct.
    """
    mock_server_obj = mocker.MagicMock()
    mock_server = mocker.patch.object(ldap, "Server", return_value=mock_server_obj)
    mock_connection = mocker.patch.object(ldap, "Connection")
    mapper = ldap.LDAPMapper()

    with tweak_local_user_settings(
        LDAP_DOMAIN="dummy.domain.com",
        LDAP_HOST="dummy.domain.com",
        LDAP_USERNAME="dummyUser",
        LDAP_PASSWORD="dummy-password",
    ):
        mapper.configure(LOCAL_USER_SETTINGS)
        mock_server.assert_called_once_with(LOCAL_USER_SETTINGS.LDAP_DOMAIN, get_info=ldap.ALL)
        mock_connection.assert_called_once_with(
            mock_server_obj,
            user=LOCAL_USER_SETTINGS.LDAP_USERNAME,
            password=LOCAL_USER_SETTINGS.LDAP_PASSWORD,
            authentication=ldap.SIMPLE,
            auto_bind=True,
        )
    assert mapper.search_base == "DC=dummy,DC=domain,DC=com"


def test_configure__sets_up_ntlm_auth_type_correctly(mocker, tweak_local_user_settings):
    """
    Test that an LDAP instance will ``configure()`` NTLM auth correctly.
    """
    mock_server_obj = mocker.MagicMock()
    mock_server = mocker.patch.object(ldap, "Server", return_value=mock_server_obj)
    mock_connection = mocker.patch.object(ldap, "Connection")
    mapper = ldap.LDAPMapper()

    with tweak_local_user_settings(
        LDAP_DOMAIN="dummy.domain.com",
        LDAP_HOST="dummy.domain.com",
        LDAP_USERNAME="dummyUser",
        LDAP_PASSWORD="dummy-password",
        LDAP_AUTH_TYPE="NTLM",
    ):
        mapper.configure(LOCAL_USER_SETTINGS)
        mock_server.assert_called_once_with(LOCAL_USER_SETTINGS.LDAP_DOMAIN, get_info=ldap.ALL)
        mock_connection.assert_called_once_with(
            mock_server_obj,
            user=f"{LOCAL_USER_SETTINGS.LDAP_DOMAIN}\\{LOCAL_USER_SETTINGS.LDAP_USERNAME}",
            password=LOCAL_USER_SETTINGS.LDAP_PASSWORD,
            authentication=ldap.NTLM,
            auto_bind=True,
        )
    assert mapper.search_base == "DC=dummy,DC=domain,DC=com"


def test_configure__raises_LDAPError_if_settings_are_missing(tweak_local_user_settings):
    """
    Test that the ``configure()`` method will fail if settings are not correct.

    If any of ``LDAP_DOMAIN``, ``LDAP_USERNAME``, or ``LDAP_PASSWORD`` are not set,
    raise an LDAPError.
    """
    mapper = ldap.LDAPMapper()

    with tweak_local_user_settings(
        LDAP_DOMAIN=None,
        LDAP_HOST="dummy.domain.com",
        LDAP_USERNAME="dummyUser",
        LDAP_PASSWORD="dummy-password",
    ):
        with pytest.raises(LDAPError, match="LDAP is not configured"):
            mapper.configure(LOCAL_USER_SETTINGS)

    with tweak_local_user_settings(
        LDAP_DOMAIN="dummy.domain.com",
        LDAP_HOST=None,
        LDAP_USERNAME="dummyUser",
        LDAP_PASSWORD="dummy-password",
    ):
        with pytest.raises(LDAPError, match="LDAP is not configured"):
            mapper.configure(LOCAL_USER_SETTINGS)

    with tweak_local_user_settings(
        LDAP_DOMAIN="dummy.domain.com",
        LDAP_HOST="dummy.domain.com",
        LDAP_USERNAME=None,
        LDAP_PASSWORD="dummy-password",
    ):
        with pytest.raises(LDAPError, match="LDAP is not configured"):
            mapper.configure(LOCAL_USER_SETTINGS)

    with tweak_local_user_settings(
        LDAP_DOMAIN="dummy.domain.com",
        LDAP_HOST="dummy.domain.com",
        LDAP_USERNAME="dummyUser",
        LDAP_PASSWORD=None,
    ):
        with pytest.raises(LDAPError, match="LDAP is not configured"):
            mapper.configure(LOCAL_USER_SETTINGS)


def test_find_username__success(mocker, tweak_local_user_settings):
    """
    Test that the ``find_username()`` gets username from ldap server given email.

    Mock the connection object to return a list of entries with one and only one
    json blob including a test username. Assert that the returned username is a lower-
    case version of the test username.
    """
    mock_entry = mocker.MagicMock()
    mock_entry.entry_to_json = lambda: json.dumps(dict(attributes=dict(cn=["XXX00X"])))
    mock_connection_obj = mocker.MagicMock()
    mock_connection_obj.entries = [mock_entry]

    mocker.patch.object(ldap, "Server")
    mocker.patch.object(
        ldap,
        "Connection",
        return_value=mock_connection_obj,
    )

    mapper = ldap.LDAPMapper()

    with tweak_local_user_settings(
        LDAP_HOST="dummy.domain.com",
        LDAP_DOMAIN="dummy.domain.com",
        LDAP_USERNAME="dummyUser",
        LDAP_PASSWORD="dummy-password",
    ):
        mapper.configure(LOCAL_USER_SETTINGS)
        username = mapper.find_username("dummy_user@dummy.domain.com")
    assert username == "xxx00x"


def test_find_username__fails_if_server_does_not_return_1_entry(mocker, tweak_local_user_settings):
    """
    Test that the ``find_username()`` fails if server does not return exactly 1 entry.

    Mock the connection object to return first an empty list and then a list of 2.
    In both cases, assert that an LDAPError is raised.
    """
    mocker.patch.object(ldap, "Server")
    mock_connection_obj = mocker.MagicMock()
    mocker.patch.object(
        ldap,
        "Connection",
        return_value=mock_connection_obj,
    )

    mapper = ldap.LDAPMapper()

    with tweak_local_user_settings(
        LDAP_HOST="dummy.domain.com",
        LDAP_DOMAIN="dummy.domain.com",
        LDAP_USERNAME="dummyUser",
        LDAP_PASSWORD="dummy-password",
    ):
        mapper.configure(LOCAL_USER_SETTINGS)

        mock_connection_obj.entries = []
        with pytest.raises(LDAPError, match="Did not find exactly one"):
            mapper.find_username("dummy_user@dummy.domain.com")

        mock_connection_obj.entries = [1, 2]
        with pytest.raises(LDAPError, match="Did not find exactly one"):
            mapper.find_username("dummy_user@dummy.domain.com")


def test_find_username__fails_if_entries_cannot_be_extracted(mocker, tweak_local_user_settings):
    """
    Test that the ``find_username()`` fails if entries are invalid.

    Mock the connection object to return a list of entries with one and only one
    json blob that is malformed. Assert that an LDAPError is raised.
    """
    mock_entry = mocker.MagicMock()
    mock_entry.entry_to_json = lambda: "BAD DATA"
    mock_connection_obj = mocker.MagicMock()
    mock_connection_obj.entries = [mock_entry]

    mocker.patch.object(ldap, "Server")
    mocker.patch.object(
        ldap,
        "Connection",
        return_value=mock_connection_obj,
    )

    mapper = ldap.LDAPMapper()

    with tweak_local_user_settings(
        LDAP_DOMAIN="dummy.domain.com",
        LDAP_HOST="dummy.domain.com",
        LDAP_USERNAME="dummyUser",
        LDAP_PASSWORD="dummy-password",
    ):
        mapper.configure(LOCAL_USER_SETTINGS)
        with pytest.raises(LDAPError, match="Failed to extract data"):
            mapper.find_username("dummy_user@dummy.domain.com")


def test_find_username__fails_if_user_has_more_than_one_CN(mocker, tweak_local_user_settings):
    """
    Test that the ``find_username()`` fails if a user has more than one username.

    Mock the connection object to return a list of entries with one and only one
    json blob first including no usernames and then multiple test username. Assert that
    in both cases a LDAPError is raised.
    """
    mock_entry = mocker.MagicMock()
    mock_connection_obj = mocker.MagicMock()
    mock_connection_obj.entries = [mock_entry]

    mocker.patch.object(ldap, "Server")
    mocker.patch.object(
        ldap,
        "Connection",
        return_value=mock_connection_obj,
    )

    mapper = ldap.LDAPMapper()

    with tweak_local_user_settings(
        LDAP_DOMAIN="dummy.domain.com",
        LDAP_HOST="dummy.domain.com",
        LDAP_USERNAME="dummyUser",
        LDAP_PASSWORD="dummy-password",
    ):
        mapper.configure(LOCAL_USER_SETTINGS)
        mock_entry.entry_to_json = lambda: json.dumps(dict(attributes=dict(cn=[])))
        with pytest.raises(LDAPError, match="User did not have exactly one CN"):
            mapper.find_username("dummy_user@dummy.domain.com")

        mock_entry.entry_to_json = lambda: json.dumps(dict(attributes=dict(cn=[1, 2])))
        with pytest.raises(LDAPError, match="User did not have exactly one CN"):
            mapper.find_username("dummy_user@dummy.domain.com")
