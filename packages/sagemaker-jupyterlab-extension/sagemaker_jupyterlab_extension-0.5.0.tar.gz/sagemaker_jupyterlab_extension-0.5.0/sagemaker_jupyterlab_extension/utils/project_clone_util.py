import asyncio
import logging

from async_lru import alru_cache
from sagemaker_jupyterlab_extension_common.clients import (
    get_sagemaker_client,
)

"""
This utlility file provides methods for validating Project Clone Plugin URL.  
The current TTL is set to 60 secs.
"""


@alru_cache(maxsize=1, ttl=60)
async def _get_projects_list():
    response = await get_sagemaker_client().list_projects()
    projects = response.get("ProjectSummaryList", [])
    projects_list = list(project["ProjectName"] for project in projects)
    return projects_list
