import pwd
import json
from typing import Tuple

from ldap3 import Server, Connection, ALL, NTLM

from cluster_agent.utils.exception import LDAPError, UIDError
from cluster_agent.utils.logging import log_error
from cluster_agent.settings import SETTINGS


class LDAP:
    """
    Provide a class to interface with the LDAP server
    """

    def __init__(self):
        """
        Initialize the LDAP class.
        """
        self.connection = None

    def connect(self):
        """
        Connec to the the LDAP server.
        """
        LDAPError.require_condition(
            all(
                [
                    SETTINGS.LDAP_DOMAIN is not None,
                    SETTINGS.LDAP_USERNAME is not None,
                    SETTINGS.LDAP_PASSWORD is not None,
                ]
            ),
            "Agent is not configured for LDAP",
        )

        domain = SETTINGS.LDAP_DOMAIN
        username = f"{domain}\\{SETTINGS.LDAP_USERNAME}"
        password = SETTINGS.LDAP_PASSWORD

        # Make static type checkers happy
        assert domain is not None

        self.search_base = ",".join([f"DC={dc}" for dc in domain.split(".")])

        server = Server(domain, get_info=ALL)
        self.connection = Connection(
            server,
            user=username,
            password=password,
            authentication=NTLM,
            auto_bind=True,
        )

    def find_username(self, email: str) -> str:
        """
        Find an active diretory username given a user email.

        Lazily connect to the LDAP server if not already connected.
        """
        if self.connection is None:
            self.connect()

        # Make static type checkers happy
        assert self.connection is not None

        self.connection.search(
            self.search_base,
            f"(mail={email})",
            attributes=["cn"],
        )

        entries = self.connection.entries
        LDAPError.require_condition(
            len(entries) == 1,
            f"Did not find exactly one match for email {email}. Found {len(entries)}",
        )

        with LDAPError.handle_errors(
            "Failed to extract data from match",
            do_except=log_error,
        ):
            match = json.loads(entries[0].entry_to_json())
            cns = match["attributes"]["cn"]

        LDAPError.require_condition(
            len(cns) == 1,
            f"User did not have exactly one CN. Got {cns}.",
        )

        user_id = cns.pop().lower()
        return user_id

    def find_uid_gid(self, email: str) -> Tuple[int, int]:
        """
        Find the uid/gid for a user given their email address.
        """
        username = self.find_username(email)
        with UIDError.handle_errors(
            f"Couldn't find uid/gid info for username {username}",
            do_except=log_error,
        ):
            entry = pwd.getpwnam(username)

        return (entry.pw_uid, entry.pw_gid)


ldap = None
with LDAPError.handle_errors("Could not create LDAP connection", do_except=log_error):
    ldap = LDAP()
