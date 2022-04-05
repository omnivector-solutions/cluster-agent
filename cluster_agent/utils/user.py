import json

from ldap3 import Server, Connection, ALL, SIMPLE
from loguru import logger

from cluster_agent.utils.exception import LDAPError
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
        logger.debug("Attempting to connect to LDAP server")
        LDAPError.require_condition(
            all(
                [
                    SETTINGS.LDAP_HOST is not None,
                    SETTINGS.LDAP_DOMAIN is not None,
                    SETTINGS.LDAP_USERNAME is not None,
                    SETTINGS.LDAP_PASSWORD is not None,
                ]
            ),
            "Agent is not configured for LDAP",
        )

        host = SETTINGS.LDAP_HOST
        domain = SETTINGS.LDAP_DOMAIN

        # Make static type checkers happy
        assert domain is not None

        self.search_base = ",".join([f"DC={dc}" for dc in domain.split(".")])

        username = SETTINGS.LDAP_USERNAME
        password = SETTINGS.LDAP_PASSWORD

        logger.debug(f"Connecting to LDAP at {host} ({domain}) with {username}")
        with LDAPError.handle_errors(
            "Couldn't connect to LDAP",
            do_except=log_error,
        ):
            server = Server(host, get_info=ALL)
            self.connection = Connection(
                server,
                user=username,
                password=password,
                authentication=SIMPLE,
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

        logger.debug(f"Searching for email {email} in LDAP")

        with LDAPError.handle_errors(
            "LDAP search failed",
            do_except=log_error,
        ):
            self.connection.search(
                self.search_base,
                f"(mail={email})",
                attributes=["cn"],
            )

        entries = self.connection.entries
        logger.debug(f"Found {len(entries)} entries")

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

        username = cns.pop().lower()
        return username


ldap = None
with LDAPError.handle_errors("Could not create LDAP connection", do_except=log_error):
    ldap = LDAP()
