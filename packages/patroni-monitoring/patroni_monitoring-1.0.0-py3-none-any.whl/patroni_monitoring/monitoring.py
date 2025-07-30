import logging
from patroni_monitoring.constants import Status

class Monitoring:
    def __init__(self,
            results: list,
            warning: int,
            critical: int,
            d_warning: float,
            d_critical: float,
            status: Status = Status.UNKNOWN) -> None:
        self._status = status
        self.results = results
        self.warning = warning
        self.critical = critical
        self.d_warning = d_warning
        self.d_critical = d_critical
        self._message = []
        self._logger = logging.getLogger(__name__)

    def __check_xlog_paused(self, xlog_paused: bool) -> None:
        """
        Checks if the xlog is paused.
        Args:
            xlog_paused (bool): Indicates if the xlog is paused.
        """
        if xlog_paused:
            status = Status.CRITICAL
        else:
            status = Status.OK
        if status.value > self._status.value:
            self._status = status
            self._message.append("XLOG is paused")

    def __check_pending_restart(self, pending_restart: bool) -> None:
        """
        Checks if the member is pending restart.
        Args:
            pending_restart (bool): Indicates if the member is pending restart.
        """
        if pending_restart:
            status = Status.WARNING
        else:
            status = Status.OK
        if status.value > self._status.value:
            self._status = status
            self._message.append("Member is pending restart")

    def __check_lag(self, lag: int) -> None:
        """
        Checks the replication lag against warning and critical thresholds.
        Args:
            lag (int): The replication lag in bytes.
        """
        if lag >= self.critical:
            status = Status.CRITICAL
        elif lag >= self.warning:
            status = Status.WARNING
        else:
            status = Status.OK
        if status.value > self._status.value:
            self._status = status
            self._message.append(f"Replication lag is {lag} bytes")

    def __check_delay(self, delay: float) -> None:
        """
        Checks the delay in seconds.
        Args:
            delay (float): The delay in seconds.
        """
        if delay >= self.d_critical:
            status = Status.CRITICAL
        elif delay >= self.d_warning:
            status = Status.WARNING
        else:
            status = Status.OK
        if status.value > self._status.value:
            self._status = status
            self._message.append(f"Delay is {delay} seconds")

    def _check_results(self) -> None:
        """
        """
        if len(self.results) == 0:
            self._status = Status.UNKNOWN
            return
        self._status = Status.OK
        for result in self.results:
            if result.get("state") != "running":
                self._status = Status.UNKNOWN
                self._message.append(f"Member {result.get('name')} is not running")
                return
            if result.get("role") == "primary":
                continue
            if result.get("role") == "standby_leader":
                continue
            lag = result.get("lag")
            self.__check_lag(lag)
            self.__check_pending_restart(result.get("pending_restart"))
            self.__check_xlog_paused(result.get("xlog_paused"))
            self.__check_delay(result.get("delay"))

    @property
    def status(self) -> int:
        """
        Returns the status of the monitoring.
        Returns:
            int: The status code (0 for OK, 1 for WARNING, 2 for CRITICAL, 3 for UNKNOWN).
        """
        self._check_results()
        message = self._message if self._message else ["No issues were found"]
        self._logger.warning("Issues: %s", ", ".join(message))
        self._logger.info("Status: %s", self._status.name)
        return self._status.value