import json
import psutil
import tornado
import os
import asyncio
import traceback
import datetime

from functools import reduce
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.utils import url_path_join
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
from sagemaker_jupyterlab_extension.utils.git_clone_util import (
    _get_domain_repositories,
    _get_user_profile_and_space_repositories,
)
from sagemaker_jupyterlab_extension.utils.project_clone_util import (
    _get_projects_list,
)
from ._version import __version__ as ext_version
from sagemaker_jupyterlab_extension_common.logging.logging_utils import HandlerLogMixin

from sagemaker_jupyterlab_extension.utils.metric_util import (
    create_metric_context,
    MetricUnit,
)
from sagemaker_jupyterlab_extension.utils.error_util import is_fault
from sagemaker_jupyterlab_extension_common.util.environment import (
    EnvironmentDetector,
)

DEFAULT_HOME_DIRECTORY = "/home/sagemaker-user"
CPU_USAGE_INTERVAL = 0.1

EXTENSION_NAME = "sagemaker_jupyterlab_extension"
EXTENSION_VERSION = ext_version


class InstanceMetricsHandler(HandlerLogMixin, JupyterHandler):
    # Do not rename or change the variable names, these are used by
    # loggers in common package.
    jl_extension_name = EXTENSION_NAME
    jl_extension_version = EXTENSION_VERSION

    skip_http_log_request = True

    """
    Schema for the resource usage api response

    response_json = {
        metrics: {
            memory: {
                rss_in_bytes: int,
                total_in_bytes: int,
                memory_percentage: float
            },
            cpu: {
                cpu_count: int,
                cpu_percentage: float
            },
            storage: {
                free_space_in_bytes: int,
                used_space_in_bytes: int,
                total_space_in_bytes: int
            }
        }
    }
    """

    executor = ThreadPoolExecutor(max_workers=5)

    """
         Function to calculate the cpu utilization percentage.
         Check official documentation here - https://psutil.readthedocs.io/en/latest/#psutil.cpu_percent
    """

    @run_on_executor
    def _get_cpu_percent(self):
        try:
            cpu_percent = psutil.cpu_percent(CPU_USAGE_INTERVAL, percpu=False)
        except Exception as err:
            self.log.exception(f"Failed to get cpu percent: {err}")
            cpu_percent = None
        return cpu_percent

    """
         This function returns the disk usage for the given path.
         Check official documentation here - https://psutil.readthedocs.io/en/latest/#psutil.disk_usage
    """

    def _get_disk_usage(self):
        try:
            path = (
                DEFAULT_HOME_DIRECTORY
                if os.path.exists(DEFAULT_HOME_DIRECTORY)
                else os.path.expanduser("~")
            )
            disk_usage = psutil.disk_usage(path)
            return {
                "free_space_in_bytes": disk_usage.free,
                "used_space_in_bytes": disk_usage.used,
                "total_space_in_bytes": disk_usage.total,
            }
        except Exception as err:
            self.log.exception(f"Failed to retrieve disk usage: {err}")
            # Record error metric
            fault_context = create_metric_context(
                "Error", "GetResourceUsage", "GetDiskUsage", 1
            )
            self.metric.put_fault("GetResourceUsage", **fault_context)
            return {}

    """
         This function returns the statistics about the system memory usage.
         Check official documentation here - https://psutil.readthedocs.io/en/latest/#psutil.virtual_memory
    """

    def _get_memory_usage(self):
        try:
            memory = psutil.virtual_memory()
            return {
                "rss_in_bytes": memory.used,
                "total_in_bytes": memory.total,
                "memory_percentage": memory.percent,
            }
        except Exception as err:
            self.log.exception(f"Failed to retrieve memory usage: {err}")
            # Record error metric
            fault_context = create_metric_context(
                "Fault", "GetResourceUsage", "GetMemoryUsage", 1, MetricUnit.Count
            )
            self.metric.put_fault("GetResourceUsage", **fault_context)
            return {}

    @tornado.web.authenticated
    async def get(self):
        self.set_header("Content-Type", "application/json")
        """
        Calculate and return the CPU, Memory and Disk usage for the Instance.
        :return: Response object compliant with above defined schema
        """

        curr_process = psutil.Process()

        if curr_process is None:
            # Record Fault metrics
            fault_context = create_metric_context(
                "Fault", "GetResourceUsage", "GetProcess", 1, MetricUnit.Count
            )
            self.metric.put_fault("GetResourceUsage", **fault_context)
            self.set_status(500)
            self.finish(json.dumps({"error": "No parent process found"}))

        """
        Get memory information for an instance.
        """

        memory_metrics = self._get_memory_usage()

        """
        Get CPU utilization
        """

        cpu_count = psutil.cpu_count()
        if cpu_count is None:
            cpu_count = None
        cpu_percent = await self._get_cpu_percent()
        cpu_metrics = {"cpu_count": cpu_count, "cpu_percentage": cpu_percent}

        """
            Get Disk Usage 
        """
        storage_metrics = self._get_disk_usage()

        metrics_response = {
            "metrics": {
                "memory": memory_metrics,
                "cpu": cpu_metrics,
                "storage": storage_metrics,
            }
        }
        self.set_status(200)
        self.finish(json.dumps(metrics_response))


def build_url(web_app, endpoint):
    base_url = web_app.settings["base_url"]
    return url_path_join(base_url, endpoint)


class CustomMetricsHandler(HandlerLogMixin, JupyterHandler):
    """Handle custom metrics data and write it directly to a log file"""

    # Do not rename or change the variable names, these are used by
    # loggers in common package.
    jl_extension_name = EXTENSION_NAME
    jl_extension_version = EXTENSION_VERSION

    _metrics_logger = None

    def get_metrics_logger(self):
        """Get or create the metrics logger instance"""
        if not CustomMetricsHandler._metrics_logger:
            from sagemaker_jupyterlab_extension.utils.metrics_logger import (
                MetricsLogger,
            )

            CustomMetricsHandler._metrics_logger = MetricsLogger()
        return CustomMetricsHandler._metrics_logger

    @tornado.web.authenticated
    async def post(self):
        """Process custom metrics data and log to file"""
        self.log.info("Received metrics POST request")
        try:
            # Get the raw request body
            body = self.request.body.decode("utf-8")
            self.log.info(f"Received metrics data: {body[:100]}...")

            # Parse the request body to extract metric and output
            request_data = json.loads(body)
            metric_data = request_data.get("metric")
            output_data = request_data.get("output")

            # Log installation stdout in local log file with timestamp
            timestamp = datetime.datetime.now().isoformat()
            self.log.info(
                f"[{timestamp}] Extension Persistence Installation Command Output: {output_data}"
            )

            # Convert metric back to JSON string for logging
            metric_json = json.dumps(metric_data) if metric_data else body

            # Log the metric with optional output
            success = self.get_metrics_logger().log_metric(metric_json)

            if success:
                self.set_status(204)  # No content
            else:
                self.set_status(500)
                self.finish(json.dumps({"error": "Failed to log metric"}))

        except Exception as error:
            self.log.error(f"Error processing metrics: {error}")
            self.set_status(500)
            self.finish(json.dumps({"error": str(error)}))

    def options(self, *args, **kwargs):
        # Handle OPTIONS requests for CORS
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_status(204)
        self.finish()


class MarkerFileHandler(HandlerLogMixin, JupyterHandler):
    """Handle marker file operations for library management"""

    jl_extension_name = EXTENSION_NAME
    jl_extension_version = EXTENSION_VERSION

    MARKER_FILE_PATH = "/opt/conda/.temp"

    @tornado.web.authenticated
    async def get(self):
        """Check if marker file exists and return status"""
        self.set_header("Content-Type", "application/json")

        try:
            file_exists = os.path.exists(self.MARKER_FILE_PATH)
            self.finish(json.dumps({"exists": file_exists}))

        except Exception as error:
            self.log.error(f"Error checking marker file: {error}")
            self.set_status(500)
            self.finish(json.dumps({"error": str(error)}))

    @tornado.web.authenticated
    async def post(self):
        """Create marker file if it doesn't exist and return status"""
        self.set_header("Content-Type", "application/json")

        try:
            file_exists = os.path.exists(self.MARKER_FILE_PATH)

            if not file_exists:
                # Create marker file
                with open(self.MARKER_FILE_PATH, "w") as f:
                    f.write("")
                self.finish(json.dumps({"created": True}))
                self.log.info("Extension Management marker file created successfully")
            else:
                self.finish(json.dumps({"created": False}))

        except Exception as error:
            self.log.error(f"Error creating marker file: {error}")
            self.set_status(500)
            self.finish(json.dumps({"error": str(error)}))


class EnvironmentHandler(HandlerLogMixin, JupyterHandler):
    """Handle marker file operations for library management"""

    jl_extension_name = EXTENSION_NAME
    jl_extension_version = EXTENSION_VERSION

    @tornado.web.authenticated
    async def get(self):
        """Check if is MD environment"""
        self.set_header("Content-Type", "application/json")

        try:
            await EnvironmentDetector.get_environment()
            isMaxDomeEnvironment = EnvironmentDetector.is_md_environment()
            self.finish(json.dumps({"isMaxDomeEnvironment": isMaxDomeEnvironment}))

        except Exception as error:
            self.set_status(500)
            self.finish(json.dumps({"error": str(error)}))


def register_handlers(nbapp):
    web_app = nbapp.web_app
    host_pattern = ".*$"
    handlers = [
        (
            build_url(web_app, r"/aws/sagemaker/api/instance/metrics"),
            InstanceMetricsHandler,
        ),
        (
            build_url(web_app, r"/aws/sagemaker/api/git/list-repositories"),
            GitCloneHandler,
        ),
        (
            build_url(web_app, r"/aws/sagemaker/api/projects/list-projects"),
            ProjectCloneHandler,
        ),
        (
            build_url(web_app, r"/aws/sagemaker/api/add-metrics"),
            CustomMetricsHandler,
        ),
        (
            build_url(web_app, r"/aws/sagemaker/api/create-marker-file"),
            MarkerFileHandler,
        ),
        (
            build_url(web_app, r"/aws/sagemaker/api/is-md-environment"),
            EnvironmentHandler,
        ),
    ]
    web_app.add_handlers(host_pattern, handlers)


class GitCloneHandler(HandlerLogMixin, JupyterHandler):
    # Do not rename or change the variable names, these are used by
    # loggers in common package.
    jl_extension_name = EXTENSION_NAME
    jl_extension_version = EXTENSION_VERSION

    """
    Response schema for the GitRepoList API
    {
        "GitCodeRepositories": [
            "repo1",
            "repo2"
        ]
    }

    """

    """
     Function to retrieve git repostiories from domain settings
    """

    async def _get_repositories_from_domain(self):
        repo_list = []
        try:
            self.log.info("Fetching repositories from domain settings")
            response = await _get_domain_repositories()
            if not response:
                self.log.warning(f"No git repositories found in domain settings")
            else:
                self.log.info(
                    "Successfully fetched %s repositories from domain setting",
                    len(response),
                )
                repo_list = response
        except Exception as error:
            self.log.error(
                (
                    "Failed to describe domain with exception: {0}".format(
                        traceback.format_exc()
                    )
                )
            )
            if is_fault(error):
                # Record Fault metrics
                fault_context = create_metric_context(
                    "Fault",
                    "GitListRepositories",
                    "DescribeDomain",
                    1,
                    MetricUnit.Count,
                )
                self.metric.put_fault("DescribeDomain", **fault_context)
            else:
                # Record Erorr metrics
                error_context = create_metric_context(
                    "Erorr",
                    "GitListRepositories",
                    "DescribeDomain",
                    1,
                    MetricUnit.Count,
                )
                self.metric.put_error("DescribeDomain", **error_context)
        return list(set(repo_list))

    """
     Function to retrieve git repostiories from user setting in user-profile
    """

    async def _get_repositories_from_user_profile_and_space(self):
        repo_list = []
        try:
            self.log.info(
                "Fetching repositories from user-profile settings and space settings"
            )
            response = await _get_user_profile_and_space_repositories()
            if not response:
                self.log.warning(
                    f"No git repositories found in user profile settings or space settings"
                )
            else:
                self.log.info(
                    "Successfully fetched %s repositories from user profile settings and space settings",
                    len(response),
                )
                repo_list = response
        except Exception as error:
            self.log.error(
                (
                    "Failed to describe user-profile with exception: {0}".format(
                        traceback.format_exc()
                    )
                )
            )
            if is_fault(error):
                # Record Fault metrics
                fault_context = create_metric_context(
                    "Fault",
                    "GitListRepositories",
                    "DescribeUserProfile",
                    1,
                    MetricUnit.Count,
                )
                self.metric.put_fault("DescribeUserProfile", **fault_context)
            else:
                # Record Error metrics
                error_context = create_metric_context(
                    "Error",
                    "GitListRepositories",
                    "DescribeUserProfile",
                    1,
                    MetricUnit.Count,
                )
                self.metric.put_error("DescribeUserProfile", **error_context)
        return list(set(repo_list))

    @tornado.web.authenticated
    async def get(self):
        self.set_header("Content-Type", "application/json")
        start_time = datetime.datetime.now()
        domain_repositories = self._get_repositories_from_domain()
        user_profile_repositories = self._get_repositories_from_user_profile_and_space()
        try:
            result = await asyncio.gather(
                domain_repositories, user_profile_repositories
            )
            res = reduce(lambda a, b: a + b, result)
            elapsedTime = datetime.datetime.now() - start_time
            latency_context = create_metric_context(
                "LatencyMS",
                "GitListRepositories",
                "GetRepositories",
                int(elapsedTime.total_seconds() * 1000),
                MetricUnit.Milliseconds,
            )
            self.metric.record_latency("GetRepositories", **latency_context)
            self.set_status(200)
            self.finish(json.dumps({"GitCodeRepositories": res}))
        except Exception as error:
            self.log.error(f"Failed to get repositories {error}")
            # Record Fault metrics
            fault_context = create_metric_context(
                "Fault", "GitListRepositories", "GetRepositories", 1, MetricUnit.Count
            )
            self.metric.put_fault("GetRepositories", **fault_context)
            self.set_status(500)
            self.finish(json.dumps({"error": "Internal Server error occurred"}))


class ProjectCloneHandler(HandlerLogMixin, JupyterHandler):
    # Do not rename or change the variable names, these are used by
    # loggers in common package.
    jl_extension_name = EXTENSION_NAME
    jl_extension_version = EXTENSION_VERSION

    """
    Response schema for the ListProjects API
    {
        "ProjectsList": [
            "project1",
            "project2"
        ]
    }

    """

    """
     Function to retrieve projects list
    """

    async def _get_projects_list(self):
        projects_list = []
        try:
            self.log.info("Fetching projects")
            response = await _get_projects_list()
            if not response:
                self.log.warning(f"No projects found")
            else:
                self.log.info(
                    "Successfully fetched %s projects",
                    len(response),
                )
                projects_list = response
        except Exception as error:
            projects_list = ["Failed to get projects "]
            self.log.error(
                (
                    "Failed to get projects with exception: {0}".format(
                        traceback.format_exc()
                    )
                )
            )
        return list(set(projects_list))

    @tornado.web.authenticated
    async def get(self):
        self.set_header("Content-Type", "application/json")
        try:
            result = await self._get_projects_list()
            self.set_status(200)
            self.finish(json.dumps({"projectsList": result}))
        except Exception as error:
            self.log.error(f"Failed to get projects {error}")
            self.set_status(500)
            self.finish(json.dumps({"error": "Internal Server error occurred"}))
