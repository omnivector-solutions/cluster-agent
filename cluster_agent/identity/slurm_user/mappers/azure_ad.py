import httpx
import typing

from loguru import logger
from pydantic import BaseModel, EmailStr, Extra

from cluster_agent.utils.logging import log_error

from cluster_agent.identity.slurm_user.exceptions import AzureADError
from cluster_agent.identity.slurm_user.mappers.mapper_base import SlurmUserMapper
from cluster_agent.identity.cluster_api import backend_client


class MemberIdentity(BaseModel, extra=Extra.ignore):
    provider: str
    access_token: str
    user_id: str


class MemberDetail(BaseModel, extra=Extra.ignore):
    email: EmailStr
    identities: typing.List[MemberIdentity]
    user_id: str


class Member(BaseModel, extra=Extra.ignore):
    user_id: str
    email: EmailStr
    name: str


class MemberList(BaseModel, extra=Extra.ignore):
    members: typing.List[Member]


class AzureResponse(BaseModel, extra=Extra.ignore):
    mailNickName: str


class AzureADMapper(SlurmUserMapper):
    """
    Provide a class to interface with the Azure AD for slurm user mapping.
    """

    async def find_username(self, email: str) -> str:
        """
        Find an Azure AD username given a user email.
        """

        with AzureADError.handle_errors(
            "Failed to fetch username from Azure AD",
            do_except=log_error,
        ):
            logger.debug(f"Searching for email {email} on Admin API")
            response = await backend_client.get(
                "/admin/management/organizations/members",
                params=dict(search=email),
            )
            response.raise_for_status()

            member_list = MemberList.parse_raw(response.content)
            AzureADError.require_condition(
                len(member_list.members) > 0,
                f"Did not find any matches for email {email}",
            )
            AzureADError.require_condition(
                len(member_list.members) < 2,
                f"Found more than one match for email {email}: {member_list}",
            )
            member = member_list.members.pop()

            logger.debug("Getting azure access token for user")
            response = await backend_client.get(
                f"/admin/management/organizations/members/{member.user_id}",
            )
            response.raise_for_status()

            member_detail = MemberDetail.parse_raw(response.content)
            AzureADError.require_condition(
                len(member_detail.identities) > 0,
                "Did not find any embedded identities for the user",
            )
            AzureADError.require_condition(
                len(member_detail.identities) < 2,
                "Found more than one embedded identity: {member_detail.identities}",
            )
            identity = member_detail.identities.pop()

            logger.debug("Requesting username from Azure AD")
            response = httpx.get(
                "https://graph.microsoft.com/v1.0/me?$select=mailNickName",
                headers=dict(Authorization=f"Bearer {identity.access_token}"),
            )
            response.raise_for_status()
            azure_details = AzureResponse.parse_raw(response.content)

            return azure_details.mailNickName.lower()
