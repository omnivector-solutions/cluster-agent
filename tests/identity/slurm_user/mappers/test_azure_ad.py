"""
Define tests for the Azure AD mapper.
"""

import httpx
import pytest
import respx

from cluster_agent.settings import SETTINGS
from cluster_agent.identity.slurm_user.exceptions import AzureADError
from cluster_agent.identity.slurm_user.mappers import azure_ad
from cluster_agent.identity.slurm_user.settings import SLURM_USER_SETTINGS


async def test_find_username__success():
    """
    Test that an AzureADMapper can fetch a username given an email.
    """
    async with respx.mock:
        respx.post(f"https://{SETTINGS.AUTH0_DOMAIN}/oauth/token").mock(
            return_value=httpx.Response(
                status_code=200,
                json=dict(access_token="dummy-token"),
            )
        )

        members_route = respx.get(
            f"{SETTINGS.BASE_API_URL}/admin/management/organizations/members"
        )
        members_route.mock(
            return_value=httpx.Response(
                status_code=200,
                json=dict(
                    members=[
                        dict(
                            user_id="dummy-id",
                            email="dummy_user@dummy.domain.com",
                            name="Dummy Dummerson",
                        ),
                    ],
                ),
            )
        )

        details_route = respx.get(
            f"{SETTINGS.BASE_API_URL}/admin/management/organizations/members/dummy-id"
        )
        details_route.mock(
            return_value=httpx.Response(
                status_code=200,
                json=dict(
                    email="dummy_user@dummy.domain.com",
                    identities=[
                        dict(
                            provider="dummy provider",
                            access_token="dummy-azure-token",
                            user_id="dummy-id",
                        ),
                    ],
                    user_id="dummy-id",
                ),
            )
        )

        azure_route = respx.get(
             "https://graph.microsoft.com/v1.0/me?$select=mailNickName"
        )
        azure_route.mock(
            return_value=httpx.Response(
                status_code=200,
                json=dict(
                    mailNickName="DDU00D",
                ),
            )
        )

        mapper = azure_ad.AzureADMapper()

        username = await mapper.find_username("dummy_user@dummy.domain.com")
        assert username == "ddu00d"


async def test_find_username__fails_if_email_search_fails():
    """
    Test that an AzureADMapper raises an exception if no user is found for the email.
    """
    async with respx.mock:
        respx.post(f"https://{SETTINGS.AUTH0_DOMAIN}/oauth/token").mock(
            return_value=httpx.Response(
                status_code=200,
                json=dict(access_token="dummy-token"),
            )
        )

        members_route = respx.get(
            f"{SETTINGS.BASE_API_URL}/admin/management/organizations/members"
        )
        members_route.mock(
            return_value=httpx.Response(
                status_code=404,
            )
        )

        with pytest.raises(AzureADError, match="Failed to fetch username from Azure AD"):
            mapper = azure_ad.AzureADMapper()
            await mapper.find_username("dummy_user@dummy.domain.com")


async def test_find_username__fails_if_email_search_has_multiple_hits():
    """
    Test that an AzureADMapper raises an exception if multiple users are found.
    """
    async with respx.mock:
        respx.post(f"https://{SETTINGS.AUTH0_DOMAIN}/oauth/token").mock(
            return_value=httpx.Response(
                status_code=200,
                json=dict(access_token="dummy-token"),
            )
        )

        members_route = respx.get(
            f"{SETTINGS.BASE_API_URL}/admin/management/organizations/members"
        )
        members_route.mock(
            return_value=httpx.Response(
                status_code=200,
                json=dict(
                    members=[
                        dict(
                            user_id="dummy-id",
                            email="dummy_user@dummy.domain.com",
                            name="Dummy Dummerson",
                        ),
                        dict(
                            user_id="stupid-id",
                            email="dummy_user@dummy.domain.com",
                            name="Stupid Vanderstupid",
                        ),
                    ],
                ),
            )
        )

        with pytest.raises(
            AzureADError,
            match="Failed to fetch username from Azure AD.*Did not find exactly one",
        ):
            mapper = azure_ad.AzureADMapper()
            await mapper.find_username("dummy_user@dummy.domain.com")


async def test_find_username__fails_if_detail_request_fails():
    """
    Test that an AzureADMapper raises an error if the request for user details fails.
    """
    async with respx.mock:
        respx.post(f"https://{SETTINGS.AUTH0_DOMAIN}/oauth/token").mock(
            return_value=httpx.Response(
                status_code=200,
                json=dict(access_token="dummy-token"),
            )
        )

        members_route = respx.get(
            f"{SETTINGS.BASE_API_URL}/admin/management/organizations/members"
        )
        members_route.mock(
            return_value=httpx.Response(
                status_code=200,
                json=dict(
                    members=[
                        dict(
                            user_id="dummy-id",
                            email="dummy_user@dummy.domain.com",
                            name="Dummy Dummerson",
                        ),
                    ],
                ),
            )
        )

        details_route = respx.get(
            f"{SETTINGS.BASE_API_URL}/admin/management/organizations/members/dummy-id"
        )
        details_route.mock(
            return_value=httpx.Response(
                status_code=400,
            )
        )

        with pytest.raises(AzureADError, match="Failed to fetch username"):
            mapper = azure_ad.AzureADMapper()
            await mapper.find_username("dummy_user@dummy.domain.com")


async def test_find_username__fails_if_multiple_identities_found():
    """
    Test that an AzureADMapper raises an error if multiple identities are found.
    """
    async with respx.mock:
        respx.post(f"https://{SETTINGS.AUTH0_DOMAIN}/oauth/token").mock(
            return_value=httpx.Response(
                status_code=200,
                json=dict(access_token="dummy-token"),
            )
        )

        members_route = respx.get(
            f"{SETTINGS.BASE_API_URL}/admin/management/organizations/members"
        )
        members_route.mock(
            return_value=httpx.Response(
                status_code=200,
                json=dict(
                    members=[
                        dict(
                            user_id="dummy-id",
                            email="dummy_user@dummy.domain.com",
                            name="Dummy Dummerson",
                        ),
                    ],
                ),
            )
        )

        details_route = respx.get(
            f"{SETTINGS.BASE_API_URL}/admin/management/organizations/members/dummy-id"
        )
        details_route.mock(
            return_value=httpx.Response(
                status_code=200,
                json=dict(
                    email="dummy_user@dummy.domain.com",
                    identities=[
                        dict(
                            provider="dummy provider",
                            access_token="dummy-azure-token",
                            user_id="dummy-id",
                        ),
                        dict(
                            provider="stupid provider",
                            access_token="stupid-azure-token",
                            user_id="stupid-id",
                        ),
                    ],
                    user_id="dummy-id",
                ),
            )
        )

        with pytest.raises(
            AzureADError,
            match="Failed to fetch username.*Did not find exactly one embedded",
        ):
            mapper = azure_ad.AzureADMapper()
            await mapper.find_username("dummy_user@dummy.domain.com")


async def test_find_username__fails_if_microsoft_graph_call_fails():
    """
    Test that an AzureADMapper raises an exception if the call to the graph api fails.
    """
    async with respx.mock:
        respx.post(f"https://{SETTINGS.AUTH0_DOMAIN}/oauth/token").mock(
            return_value=httpx.Response(
                status_code=200,
                json=dict(access_token="dummy-token"),
            )
        )

        members_route = respx.get(
            f"{SETTINGS.BASE_API_URL}/admin/management/organizations/members"
        )
        members_route.mock(
            return_value=httpx.Response(
                status_code=200,
                json=dict(
                    members=[
                        dict(
                            user_id="dummy-id",
                            email="dummy_user@dummy.domain.com",
                            name="Dummy Dummerson",
                        ),
                    ],
                ),
            )
        )

        details_route = respx.get(
            f"{SETTINGS.BASE_API_URL}/admin/management/organizations/members/dummy-id"
        )
        details_route.mock(
            return_value=httpx.Response(
                status_code=200,
                json=dict(
                    email="dummy_user@dummy.domain.com",
                    identities=[
                        dict(
                            provider="dummy provider",
                            access_token="dummy-azure-token",
                            user_id="dummy-id",
                        ),
                    ],
                    user_id="dummy-id",
                ),
            )
        )

        azure_route = respx.get(
             "https://graph.microsoft.com/v1.0/me?$select=mailNickName"
        )
        azure_route.mock(
            return_value=httpx.Response(
                status_code=400,
            )
        )

        with pytest.raises(AzureADError, match="Failed to fetch username"):
            mapper = azure_ad.AzureADMapper()
            await mapper.find_username("dummy_user@dummy.domain.com")
