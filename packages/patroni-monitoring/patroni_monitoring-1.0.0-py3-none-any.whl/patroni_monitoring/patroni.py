import httpx
import sys
import datetime
from logging import getLogger
from patroni_monitoring.constants import Status

class PatroniAPI:
    """A class to interact with the Patroni API for cluster monitoring."""
    def __init__(self, url: str, timeout: int) -> None:
        self.base_url = url
        self._scope = None
        self._cluster_info = None
        self._members = []
        self._current_time = None
        self._timeout = timeout
        self._logger = getLogger(__name__)

    def _get_cluster_info(self) -> dict:
        """
        Fetches cluster information from the Patroni API.
        Returns:
            dict: A dictionary containing cluster information.
        """
        with httpx.Client() as client:
            try:
                response = client.get(f"{self.base_url}/cluster", timeout=self._timeout)
            except httpx.ConnectError as connect_error:
                self._logger.error("Failed to connect to Patroni API at %s: %s", self.base_url, connect_error)
                sys.exit(Status.UNKNOWN.value)
            except httpx.ConnectTimeout:
                self._logger.error("Connection to Patroni API at %s time out after %s seconds", self.base_url, self._timeout)
                sys.exit(Status.UNKNOWN.value)
            except KeyboardInterrupt:
                self._logger.error("Keyboard interrupt received, exiting...")
                sys.exit(Status.UNKNOWN.value)
            return response.json()

    @property
    def scope(self) -> str:
        """
        Returns the scope of the cluster.
        If the scope is not set, it fetches the cluster information to determine the scope.
        Returns:
            str: The scope of the cluster.
        """
        if self._scope is None:
            cluster_info = self._get_cluster_info()
            self._scope = cluster_info.get("scope", "unknown")
        return self._scope

    @property
    def cluster_info(self) -> dict:
        """
        Returns the cluster information.
        If the cluster information is not set, it fetches it from the Patroni API.
        Returns:
            dict: A dictionary containing cluster information.
        """
        if self._cluster_info is None:
            self._cluster_info = self._get_cluster_info()
        return self._cluster_info

    @property
    def members(self) -> list:
        """
        Returns the list of members in the cluster.
        If the members are not set, it fetches them from the cluster information.
        Returns:
            list: A list of dictionaries containing member information.
        """
        if not self._members:
            cluster_info = self.cluster_info
            self._members = cluster_info.get("members", [])
        return self._members

    def _get_member_by_api_uri(self, api_uri: str) -> dict:
        """
        Returns a member's information by its name.
        Args:
            name (str): The name of the member.
        Returns:
            dict: A dictionary containing the member's information.
        """
        with httpx.Client() as client:
            try:
                response = client.get(api_uri, timeout=self._timeout)
            except httpx.ConnectError as connect_error:
                self._logger.error("Failed to connect to Patroni API at %s: %s", self.base_url, connect_error)
                sys.exit(Status.UNKNOWN.value)
            except httpx.ConnectTimeout:
                self._logger.error("Connection to Patroni API at %s time out after %s seconds", self.base_url, self._timeout)
                sys.exit(Status.UNKNOWN.value)
            except KeyboardInterrupt:
                self._logger.error("Keyboard interrupt received, exiting...")
                sys.exit(Status.UNKNOWN.value)
            return response.json()

    def cluster_status(self) -> list:
        """
        Returns the status of the cluster.
        If the cluster information is not set, it fetches it from the Patroni API.
        Returns:
            str: The status of the cluster.
        """
        results = []
        for member in self.members:
            member_result = {}
            self._current_time = datetime.datetime.now(datetime.timezone.utc).astimezone()
            api_url = member.get("api_url")
            member_health = self._get_member_by_api_uri(api_url)
            patroni_time_format = "%Y-%m-%d %H:%M:%S.%f%z"
            results_time_format = "%Y-%m-%d %H:%M:%S%z"
            start_time = datetime.datetime.strptime(str(member_health.get("postmaster_start_time")), patroni_time_format)
            xlog = member_health.get("xlog") if member_health.get("role") != "primary" else {}
            replay_time = datetime.datetime.strptime(str(xlog.get("replayed_timestamp")), patroni_time_format) if member_health.get("role") != "primary" else self._current_time
            member_result.update({
                "name": member.get("name"),
                "role": member_health.get("role"),
                "state": member_health.get("state"),
                "Start_time": start_time.strftime(results_time_format),
                "timeline": member_health.get("timeline"),
                "version": member_health.get("server_version"),
                "lag": member.get("lag", "N/A"),
                "pending_restart": member_health.get("pending_restart", False),
                "xlog_paused": xlog.get("paused", "N/A"),
                "xlog_replay_time": replay_time.strftime(results_time_format),
                "current_time": self._current_time.strftime(results_time_format),
                "delay": round((abs(self._current_time - replay_time).total_seconds()), 2)
            })
            results.append(member_result)
        return results