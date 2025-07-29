import asyncio
import logging

from async_lru import alru_cache
from sagemaker_jupyterlab_extension_common.clients import (
    get_sagemaker_client,
)

"""
This utlility file provides methods for caching purpose for the GitCloneHandler.  
The current TTL is set to 60 secs.
"""


@alru_cache(maxsize=1, ttl=60)
async def _get_domain_repositories():
    response = await get_sagemaker_client().describe_domain()
    domain_repos = (
        response.get("DefaultUserSettings", {})
        .get("JupyterLabAppSettings", {})
        .get("CodeRepositories", [])
    )
    domain_repo_list = list(repo["RepositoryUrl"] for repo in domain_repos)
    return domain_repo_list


@alru_cache(maxsize=1, ttl=60)
async def _get_user_profile_and_space_repositories():
    """ "
    Since user-profile-name is not present in AppMetadata.
    We will Retrieve the SpaceSettings to fetch the user profile name. Along with that we need to fetch the list of any Git repositories configured at space settings level.
    """
    space_setting_response = await _get_space_settings()

    # List of repos from space settings
    space_git_repos = space_setting_response.get("CodeRepositories")
    userProfileName = space_setting_response.get("OwnerUserProfileName")

    # Get the repositories from user profile settings
    user_profile_response = await get_sagemaker_client().describe_user_profile(
        user_profile_name=userProfileName
    )

    # Repositories from user profile config
    user_profile_repos = (
        user_profile_response.get("UserSettings", {})
        .get("JupyterLabAppSettings", {})
        .get("CodeRepositories", [])
    )
    # Extract repositories into list
    profile_repo_list = list(repo["RepositoryUrl"] for repo in user_profile_repos)
    return profile_repo_list + space_git_repos


@alru_cache(maxsize=1, ttl=60)
async def _get_space_settings():
    resp = await get_sagemaker_client().describe_space()

    """
    Convert the response of describe space setting as per our needs. 
    """
    space_git_repos = (
        resp.get("SpaceSettings", {})
        .get("JupyterLabAppSettings", {})
        .get("CodeRepositories", [])
    )
    user_profile_name = resp.get("OwnershipSettings").get("OwnerUserProfileName")
    space_repo_list = list(repo["RepositoryUrl"] for repo in space_git_repos)
    response = {
        "CodeRepositories": space_repo_list,
        "OwnerUserProfileName": user_profile_name,
    }
    logging.info("Total repositories found in space settings %s", len(space_repo_list))
    return response
