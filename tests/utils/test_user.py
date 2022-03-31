"""
Define tests for the user utils.
"""

import json

import pytest

from cluster_agent.utils import user
from cluster_agent.utils.exception import LDAPError, UIDError
from cluster_agent.settings import SETTINGS


def test_connect__success(mocker, tweak_settings):
    """
    Test that an LDAP instance will ``connect()`` if settings are correct.
    """
    mock_server_obj = mocker.MagicMock()
    mock_server = mocker.patch.object(user, "Server", return_value=mock_server_obj)
    mock_connection = mocker.patch.object(user, "Connection")
    ldap = user.LDAP()

    with tweak_settings(
        LDAP_DOMAIN="dummy.domain.com",
        LDAP_USERNAME="dummyUser",
        LDAP_PASSWORD="dummy-password",
    ):
        ldap.connect()
        mock_server.assert_called_once_with(SETTINGS.LDAP_DOMAIN, get_info=user.ALL)
        mock_connection.assert_called_once_with(
            mock_server_obj,
            user=f"{SETTINGS.LDAP_DOMAIN}\\{SETTINGS.LDAP_USERNAME}",
            password=SETTINGS.LDAP_PASSWORD,
            authentication=user.NTLM,
            auto_bind=True,
        )
    assert ldap.search_base == "DC=dummy,DC=domain,DC=com"


def test_connect__raises_LDAPError_if_settings_are_missing(tweak_settings):
    """
    Test that the ``connect()`` method will fail if settings are not correct.

    If any of ``LDAP_DOMAIN``, ``LDAP_USERNAME``, or ``LDAP_PASSWORD`` are not set,
    raise an LDAPError.
    """
    ldap = user.LDAP()

    with tweak_settings(
        LDAP_DOMAIN=None,
        LDAP_USERNAME="dummyUser",
        LDAP_PASSWORD="dummy-password",
    ):
        with pytest.raises(LDAPError, match="Agent is not configured for LDAP"):
            ldap.connect()

    with tweak_settings(
        LDAP_DOMAIN="dummy.domain.com",
        LDAP_USERNAME=None,
        LDAP_PASSWORD="dummy-password",
    ):
        with pytest.raises(LDAPError, match="Agent is not configured for LDAP"):
            ldap.connect()

    with tweak_settings(
        LDAP_DOMAIN="dummy.domain.com",
        LDAP_USERNAME="dummyUser",
        LDAP_PASSWORD=None,
    ):
        with pytest.raises(LDAPError, match="Agent is not configured for LDAP"):
            ldap.connect()


def test_find_username__success(mocker, tweak_settings):
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

    mocker.patch.object(user, "Server")
    mocker.patch.object(
        user,
        "Connection",
        return_value=mock_connection_obj,
    )

    ldap = user.LDAP()

    with tweak_settings(
        LDAP_DOMAIN="dummy.domain.com",
        LDAP_USERNAME="dummyUser",
        LDAP_PASSWORD="dummy-password",
    ):
        username = ldap.find_username("dummy_user@dummy.domain.com")
    assert username == "xxx00x"


def test_find_username__fails_if_server_does_not_return_1_entry(mocker, tweak_settings):
    """
    Test that the ``find_username()`` fails if server does not return exactly 1 entry.

    Mock the connection object to return first an empty list and then a list of 2.
    In both cases, assert that an LDAPError is raised.
    """
    mocker.patch.object(user, "Server")
    mock_connection_obj = mocker.MagicMock()
    mocker.patch.object(
        user,
        "Connection",
        return_value=mock_connection_obj,
    )

    ldap = user.LDAP()

    with tweak_settings(
        LDAP_DOMAIN="dummy.domain.com",
        LDAP_USERNAME="dummyUser",
        LDAP_PASSWORD="dummy-password",
    ):

        mock_connection_obj.entries = []
        with pytest.raises(LDAPError, match="Did not find exactly one"):
            ldap.find_username("dummy_user@dummy.domain.com")

        mock_connection_obj.entries = [1, 2]
        with pytest.raises(LDAPError, match="Did not find exactly one"):
            ldap.find_username("dummy_user@dummy.domain.com")


def test_find_username__fails_if_entries_cannot_be_extracted(mocker, tweak_settings):
    """
    Test that the ``find_username()`` fails if entries are invalid.

    Mock the connection object to return a list of entries with one and only one
    json blob that is malformed. Assert that an LDAPError is raised.
    """
    mock_entry = mocker.MagicMock()
    mock_entry.entry_to_json = lambda: "BAD DATA"
    mock_connection_obj = mocker.MagicMock()
    mock_connection_obj.entries = [mock_entry]

    mocker.patch.object(user, "Server")
    mocker.patch.object(
        user,
        "Connection",
        return_value=mock_connection_obj,
    )

    ldap = user.LDAP()

    with tweak_settings(
        LDAP_DOMAIN="dummy.domain.com",
        LDAP_USERNAME="dummyUser",
        LDAP_PASSWORD="dummy-password",
    ):
        with pytest.raises(LDAPError, match="Failed to extract data"):
            ldap.find_username("dummy_user@dummy.domain.com")


def test_find_username__fails_if_user_has_more_than_one_CN(mocker, tweak_settings):
    """
    Test that the ``find_username()`` fails if a user has more than one username.

    Mock the connection object to return a list of entries with one and only one
    json blob first including no usernames and then multiple test username. Assert that
    in both cases a LDAPError is raised.
    """
    mock_entry = mocker.MagicMock()
    mock_connection_obj = mocker.MagicMock()
    mock_connection_obj.entries = [mock_entry]

    mocker.patch.object(user, "Server")
    mocker.patch.object(
        user,
        "Connection",
        return_value=mock_connection_obj,
    )

    ldap = user.LDAP()

    with tweak_settings(
        LDAP_DOMAIN="dummy.domain.com",
        LDAP_USERNAME="dummyUser",
        LDAP_PASSWORD="dummy-password",
    ):
        mock_entry.entry_to_json = lambda: json.dumps(dict(attributes=dict(cn=[])))
        with pytest.raises(LDAPError, match="User did not have exactly one CN"):
            ldap.find_username("dummy_user@dummy.domain.com")

        mock_entry.entry_to_json = lambda: json.dumps(dict(attributes=dict(cn=[1, 2])))
        with pytest.raises(LDAPError, match="User did not have exactly one CN"):
            ldap.find_username("dummy_user@dummy.domain.com")


def test_find_uid_gid__success(mocker, tweak_settings):
    """
    Test that the ``find_uid_gid()`` gets uid and gid for the given user email.

    Mock ``pwd.getpwnam`` to return a valid passwd entry with a uid and guid for the
    user. Assert that the returned value is a 2-tuple of integers.
    """

    mock_pwd_entry = mocker.MagicMock()
    mock_pwd_entry.pw_uid = 1111
    mock_pwd_entry.pw_gid = 9999
    mock_pwd = mocker.patch.object(user, "pwd")
    mock_pwd.getpwnam.return_value = mock_pwd_entry

    ldap = user.LDAP()
    mocker.patch.object(ldap, "find_username")

    with tweak_settings(
        LDAP_DOMAIN="dummy.domain.com",
        LDAP_USERNAME="dummyUser",
        LDAP_PASSWORD="dummy-password",
    ):
        (uid, gid) = ldap.find_uid_gid("dummy_user@dummy.domain.com")

    assert uid == 1111
    assert gid == 9999


def test_find_uid_gid__fails_if_getpwnam_finds_no_matches(mocker, tweak_settings):
    """
    Test that the ``find_uid_gid()`` fails if the getpwnam finds no matches.

    Mock ``pwd.getpwnam`` to raise a ``KeyError`` if the supplied email has no uid.
    Assert that a UIDError is raised.
    """

    mock_pwd = mocker.patch.object(user, "pwd")
    mock_pwd.getpwnam.side_effect = KeyError("name not found")

    ldap = user.LDAP()
    mocker.patch.object(ldap, "find_username")

    with tweak_settings(
        LDAP_DOMAIN="dummy.domain.com",
        LDAP_USERNAME="dummyUser",
        LDAP_PASSWORD="dummy-password",
    ):
        with pytest.raises(UIDError, match="Couldn't find uid/gid info"):
            ldap.find_uid_gid("dummy_user@dummy.domain.com")
