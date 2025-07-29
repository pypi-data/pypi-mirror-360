import requests
import time

from typing import Optional, Any, Dict
from datetime import datetime

from ..utility_base import UtilityBase

class TeamsClient(UtilityBase):
    """
    Client for sending messages and issue cards to Microsoft Teams webhooks
    mapped by channel name.

    Supports adaptive card formatting for lists of Jira issues,
    and plain text messages, with configurable retries and timeouts.
    Inherits logging behavior from LoggingBase.
    """

    def __init__(
        self,
        channels: Dict[str, str],
        jira_base_url: str,
        verbose: Optional[bool] = None,
        logger: Optional[Any] = None,
        log_level: Optional[int] = None,
        max_issues: int = 20,
        post_timeout: int = 8,
        post_retries: int = 2,
    ) -> None:
        """
        Initialize the TeamsClient.

        Args:
            channels (Dict[str, str]): Mapping of channel names to Teams webhook URLs.
            jira_base_url (str): Base URL for Jira instance.
            verbose (Optional[bool]): Enable verbose logging.
            logger (Optional[Any]): Logger object to use.
            log_level (Optional[int]): Log level.
            max_issues (int): Max issues per card to display (default: 20).
            post_timeout (int): Timeout (seconds) for POST requests (default: 8).
            post_retries (int): Number of retries for failed requests (default: 2).
        """
        super().__init__(verbose, logger, log_level)

        self.channels: Dict[str, str] = {k: v.rstrip('/') for k, v in channels.items()}
        self.jira_base_url = jira_base_url.rstrip('/')
        self.max_issues = max_issues
        self.post_timeout = post_timeout
        self.post_retries = post_retries

    def send_message(self, channel: str, message: str) -> bool:
        """
        Send a simple plain text message to a Teams channel.

        Args:
            channel (str): Name of the Teams channel to send to.
            message (str): The message text to send.

        Returns:
            bool: True if sent successfully, False otherwise.
        """
        webhook_url = self.channels.get(channel)
        if not webhook_url:
            self._log_critical(f"Invalid channel: '{channel}' not found in TeamsClient.")
            return False

        payload: Dict[str, Any] = {"text": message}
        return self._post_payload(webhook_url, payload)

    def send_formatted_message(self, channel: str, payload: Dict[str, Any]) -> bool:
        """
        Send a formatted text message to a Teams channel. 
        Formatting is provided by the user

        Args:
            channel (str): Name of the Teams channel to send to.
            payload (str): The formatted message dictionary to send.

        Returns:
            bool: True if sent successfully, False otherwise.
        """
        webhook_url = self.channels.get(channel)
        if not webhook_url:
            self._log_critical(f"Invalid channel: '{channel}' not found in TeamsClient.")
            return False

        return self._post_payload(webhook_url, payload)

    def _post_payload(self, webhook_url: str, payload: Dict[str, Any]) -> bool:
        """
        Send a payload to the Teams webhook, with retries and timeout.

        Args:
            webhook_url (str): The webhook URL to post to.
            payload (Dict[str, Any]): The payload to send to Teams.

        Returns:
            bool: True if sent successfully, False otherwise.
        """
        self._log_debug(f"Sending payload to Teams at '{webhook_url}': {payload}")

        for attempt in range(1, self.post_retries + 2):  # try N+1 times
            try:
                response = requests.post(
                    webhook_url,
                    json=payload,
                    timeout=self.post_timeout
                )
                text = response.text
                if response.status_code == 200:
                    self._log("Notification sent to Teams successfully.")
                    return True
                else:
                    self._log_error(
                        f"Failed to send Teams notification: {response.status_code}, {text} (attempt {attempt})"
                    )
            except Exception as exc:
                self._log_exception(f"Exception during Teams notification (attempt {attempt}): {exc}")

            if attempt < self.post_retries + 1:
                time.sleep(2)  # wait before retry

        return False

    @staticmethod
    def _format_datetime(dt: Optional[Any]) -> str:
        """
        Format a datetime object (or ISO string) to a readable string for Teams.

        Args:
            dt (Optional[Any]): The datetime object or string.

        Returns:
            str: Formatted date/time, or '-' if None.
        """
        if not dt:
            return "-"
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt)
            except Exception:
                return str(dt)
        return dt.strftime("%Y-%m-%d %H:%M")
