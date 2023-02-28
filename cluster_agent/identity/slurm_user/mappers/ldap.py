import json

from ldap3 import ALL, NTLM, RESTARTABLE, SIMPLE, Connection, Server
from ldap3.utils.log import ERROR, set_library_log_detail_level
from loguru import logger
from timeoutcontext import timeout

from cluster_agent.identity.slurm_user.constants import LDAPAuthType
from cluster_agent.identity.slurm_user.exceptions import LDAPError
from cluster_agent.identity.slurm_user.mappers.mapper_base import SlurmUserMapper
from cluster_agent.settings import Settings
from cluster_agent.utils.logging import log_error

set_library_log_detail_level(ERROR)


class LDAPMapper(SlurmUserMapper):
    """
    Provide a class to interface with the LDAP server
    """

    connection = None
    _timeout_seconds = 30

    async def configure(self, settings: Settings):
        """
        Connect to the the LDAP server.
        """
        logger.debug("Attempting to connect to LDAP server")
        LDAPError.require_condition(
            all(
                [
                    settings.LDAP_HOST is not None,
                    settings.LDAP_DOMAIN is not None,
                    settings.LDAP_USERNAME is not None,
                    settings.LDAP_PASSWORD is not None,
                ]
            ),
            "LDAP is not configured in the settings. Cannot use LDAP user-mapper.",
        )

        host = settings.LDAP_HOST
        domain = settings.LDAP_DOMAIN

        # Make static type checkers happy
        assert domain is not None

        self.search_base = ",".join([f"DC={dc}" for dc in domain.split(".")])

        if settings.LDAP_AUTH_TYPE == LDAPAuthType.NTLM:
            username = f"{settings.LDAP_DOMAIN}\\{settings.LDAP_USERNAME}"
            auth_type = NTLM
        else:
            username = settings.LDAP_USERNAME
            auth_type = SIMPLE

        password = settings.LDAP_PASSWORD

        logger.debug(f"Connecting to LDAP at {host} ({domain}) with {username}")
        with LDAPError.handle_errors("Couldn't connect to LDAP", do_except=log_error):
            with timeout(self._timeout_seconds):
                logger.debug("Creating server object")
                server = Server(host, get_info=ALL)
                logger.debug("Creating connection object")
                self.connection = Connection(
                    server,
                    user=username,
                    password=password,
                    authentication=auth_type,
                    client_strategy=RESTARTABLE,
                )
                logger.debug("Starting TLS")
                self.connection.start_tls()
                logger.debug("Binding to LDAP")
                self.connection.bind()
        logger.debug("Connection established to LDAP")

    async def find_username(self, email: str) -> str:
        """
        Find an active diretory username given a user email.

        Lazily connect to the LDAP server if not already connected.
        """
        LDAPError.require_condition(
            self.connection is not None,
            "Not connected to an LDAP server yet!",
        )
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
