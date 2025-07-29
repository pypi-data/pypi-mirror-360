import aiohttp
import asyncio
import logging

from typing import Optional, Dict, Any, List, Union
from collections import defaultdict

from ..utility_base import UtilityBase
from ..logger import Logger, LogWrapper

async def _noop():
    """Helper function."""
    return None


class JiraClient(UtilityBase):
    """A client for interacting with Jira's REST API."""
    
    def __init__(
            self, 
            api_key: str, 
            jira_url: str,
            retry_cnt: int = 1,
            verbose: bool = False,
            log_urls: bool = False,
            logger: Optional[Union[logging.Logger, Logger, LogWrapper]] = None,
            log_level: Optional[int] = None
        ):
        """
        Initializes the Jira client with an API key and optional logger.

        Args:
            api_key (str): Jira API key for authentication.
            jira_url (str): Base URL of the Jira instance.
            retry_cnt (int, optional): Number of retries in case of a failed request.
            verbose (bool, optional): If True, debug messages are logged during the operations. Exceptions, Errors and Warnings are always logged.
            log_urls (bool, optional): If True, all the requested URLs are logged.
            logger (Optional[Union[logging.Logger, Logger, LogWrapper]], optional): Logger instance. If not provided, a default logger is used.
            log_level (Optional[int], optional): Log level. If not provided, INFO level will be used for logging.
        """
        # Init base class
        super().__init__(verbose, logger, log_level)
        self.log_urls = log_urls

        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        }
        self.session: Optional[aiohttp.ClientSession] = None  # Session is not created yet

        self.jira_url = jira_url
        self.base_issue_url = f"{jira_url}/rest/api/2/issue"
        self.base_search_url = f"{jira_url}/rest/api/2/search"
        self.base_board_url = f"{jira_url}/rest/agile/1.0/board"

        self.retry_cnt = retry_cnt
                
    async def _fetch_json(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch JSON data from Jira. Requires session to be started first.

        Args:
            url (str): The Jira URL that returns a JSON object as a response.

        Returns:
            Optional[Dict[str, Any]]: The response as a Python dictionary or None in case of a failed retrieval.
        """
        if self.session is None:
            raise RuntimeError("JiraClient session is not initialized. Call `await start_session()` first.")
        
        if self.log_urls:
            self._log(f"Requested URL: `{url}`")

        try:
            counter = 0
            while counter < self.retry_cnt:
                async with self.session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self._log_warning(f"Failed to fetch `{url}`. Response status: {response.status} ({counter+1}. attempt).")
                counter += 1

            self._log_error(f"Failed to fetch `{url}` after {self.retry_cnt} retries.")
        except aiohttp.ClientConnectionError as e:
            self._log_exception(f"Connection error while requesting `{url}`: {e}")
            raise
        except aiohttp.ClientResponseError as e:
            self._log_exception(f"Response error {e.status} while requesting `{url}`: {e}")
            raise
        except aiohttp.ClientPayloadError as e:
            self._log_exception(f"Payload error while requesting `{url}`: {e}")
            raise
        except aiohttp.ClientError as e:
            self._log_exception(f"General client error while requesting `{url}`: {e}")
            raise
        except Exception as e:
            self._log_exception(f"Unexpected error while requesting `{url}`: {e}")
            raise

        return None

    async def _read_issue_worklog(self, issue_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the worklog details for a Jira issue.
        
        Args:
            issue_id (str): The Jira issue ID.

        Returns:
            Optional[Dict[str, Any]]: Worklog JSON data as a dictionary, or None if an error occurs.
        """
        url = f"{self.base_issue_url}/{issue_id}/worklog"

        return await self._fetch_json(url)

    async def _read_issue_comments(self, issue_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the comments for a Jira issue.
        
        Args:
            issue_id (str): The Jira issue ID.

        Returns:
            Optional[Dict[str, Any]]: Comments JSON data as a dictionary, or None if an error occurs.
        """
        url = f"{self.base_issue_url}/{issue_id}/comment"

        return await self._fetch_json(url)

    async def start_session(self):
        """Explicitly initialize the aiohttp session. Must be called once before making requests."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        else:
            self._log("Session already initialized. Skipping.")

    async def close_session(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def read_custom_jql_keys(self, custom_jql: str) -> list[str]:
        """
        Retrieve all issue keys for a custom JQL query.

        Args:
            custom_jql (str): The JQL query as a string.

        Returns:
            list[str]: The result of the JQL query.
        """
        issue_keys = []
        start_at = 0
        batch_size = 1000  # Jira API limit per request

        while True:
            url = f"{self.base_search_url}?jql={custom_jql}&fields=key&startAt={start_at}&maxResults={batch_size}"

            response_data = await self._fetch_json(url)
            if not response_data or "issues" not in response_data:
                self._log_error(f"Failed to retrieve result keys for query '{custom_jql}'")
                break

            # Extract issue keys
            batch_keys = [issue["key"] for issue in response_data["issues"]]
            issue_keys.extend(batch_keys)

            # Pagination check: Stop if fewer results than batch size
            if len(batch_keys) < batch_size:
                break  # No more issues left to fetch

            # Move to the next batch
            start_at += batch_size

        self._log(f"Read {len(issue_keys)} keys for JQL query:\n\t`{custom_jql}`")
        return issue_keys

    async def read_linked_issue_keys(self, issue_key: str) -> dict[str, list[str]]:
        """
        Retrieve related issue keys for a given Jira issue, grouped by link type.

        Args:
            issue_key (str): The Jira issue key.

        Returns:
            dict[str, list[str]]: Dictionary with link types as keys and lists of issue keys as values.
        """
        url = f"{self.base_issue_url}/{issue_key}"
        issue_data = await self._fetch_json(url)
        if not issue_data:
            self._log_error(f"Failed to fetch issue data for {issue_key}")
            return {}

        issuelinks = issue_data.get("fields", {}).get("issuelinks", [])
        result = defaultdict(list)

        for link in issuelinks:
            link_type = link.get("type", {}).get("name", "Unknown")
            # Can be 'inwardIssue' or 'outwardIssue'
            if "outwardIssue" in link:
                result[link_type].append(link["outwardIssue"]["key"])
            if "inwardIssue" in link:
                result[link_type].append(link["inwardIssue"]["key"])

        return dict(result)

    async def read_linked_epic_keys(self, epic_key: str) -> list[str]:
        """
        Retrieve related issue keys for a given Jira epic.

        Args:
            epic_key (str): The Jira issue (epic) key.

        Returns:
            list[str]: The list of issue keys as values.
        """
        return await self.read_custom_jql_keys(custom_jql=f'"Epic Link"={epic_key}')

    async def read_issue(
            self, 
            issue_id: str, 
            read_changelog: Optional[bool] = False, 
            read_comments: Optional[bool] = False, 
            read_worklog: Optional[bool] = False,
            changelog_filter: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch the details of a Jira issue, with optional inclusion of changelog, comments, and worklog data.

        This method asynchronously retrieves data for a specified Jira issue. By default, it only fetches 
        the main issue data, but it can also fetch and merge additional information such as the changelog, 
        comments, and worklog if the corresponding flags are set to True.

        If `read_changelog` is enabled and a `changelog_filter` is provided, the changelog will be filtered
        to include only entries where the changed field name matches one of the specified filter values. 
        The filter is case-insensitive.

        The method uses asynchronous calls for efficiency and supports partial data loading depending 
        on the specified flags.

        Args:
            issue_id (str): The unique identifier of the Jira issue to fetch.
            read_changelog (Optional[bool], optional): If True, fetches the issue changelog and includes it in the result. Defaults to False.
            read_comments (Optional[bool], optional): If True, fetches the issue comments and includes them in the result. Defaults to False.
            read_worklog (Optional[bool], optional): If True, fetches the issue worklog and includes it in the result. Defaults to False.
            changelog_filter (Optional[List[str]], optional): An optional list of field names to filter the changelog. Only changes to these fields will be included in the result. Filtering is case-insensitive. Ignored if `read_changelog` is False.

        Returns:
            Optional[Dict[str, Any]]: A dictionary representing the full issue data with optionally merged changelog, comments, and worklog. Returns None if the issue cannot be fetched or if an error occurs.
        """
        url = f"{self.base_issue_url}/{issue_id}"
        if read_changelog:
            url = f"{url}?expand=changelog"

        issue_data, worklog, comments = await asyncio.gather(
            self._fetch_json(url),
            self._read_issue_worklog(issue_id) if read_worklog else _noop(),
            self._read_issue_comments(issue_id) if read_comments else _noop(),
            return_exceptions=True)

        if issue_data and "fields" in issue_data:
            issue_data["fields"]["worklog"] = worklog if worklog else {}
            issue_data["fields"]["comment"] = comments if comments else {}

            if read_changelog and changelog_filter and len(changelog_filter) > 0:
                changelog_filter_lower = [item.lower() for item in changelog_filter]

                filtered_changelog = []
                for log in issue_data["changelog"]["histories"]:
                    matching_items = [
                        item for item in log["items"]
                        if item["field"].lower() in changelog_filter_lower
                    ]
                    if matching_items:
                        filtered_log = dict(log)  # shallow copy to avoid mutating original
                        filtered_log["items"] = matching_items
                        filtered_changelog.append(filtered_log)

                issue_data["changelog"]["histories"] = filtered_changelog

            return issue_data
        else:
            self._log_error(f"Could not fetch issue {issue_id}")
        
        return None
    
    async def read_board_id(self, board_name: str) -> int | None:
        """
        Asynchronously retrieve the ID of a board given its name.

        Constructs the request URL using the board name and fetches the JSON response.
        Searches through the response to find a board with a matching name and returns its ID.

        Args:
            board_name (str): The name of the board to look up.

        Returns:
            Optional[int]: The ID of the board if found, otherwise None.
        """
        url = f"{self.base_board_url}?name={board_name}"
        response = await self._fetch_json(url)

        if response and len(response) > 0:
            for board in response["values"]:
                if board["name"] == board_name:
                    self._log(f"Read board ID ({int(board['id'])}) for board `{board_name}`")
                    return int(board["id"])
        else:
            self._log_error(f"Could not retrieve ID for board `{board_name}`")
                
        return None
    
    async def read_sprint_list(self, 
                               board_id: int, 
                               origin_board: Optional[bool] = False,
                               name_filter: Optional[str] = None
        ) -> List[Dict[str, Any]]:   
        """
        Asynchronously retrieve a list of active and closed sprints for a given Jira board.

        The method paginates through the Jira API to collect all matching sprints. It can optionally
        filter the results to only include:
        - Sprints originating from the specified board (via `origin_board`)
        - Sprints whose names contain a specific substring (via `name_filter`)

        Args:
            board_id (int): The ID of the Jira board to fetch sprints from.
            origin_board (Optional[bool], optional): If True, only sprints where `originBoardId` matches the board_id are returned.
            name_filter (Optional[str], optional): If provided, only sprints whose names include this substring will be returned.

        Returns:
            List[Dict[str, Any]]: A list of sprint dictionaries with data as returned by the Jira API. Returns None on failure.
        """
        sprint_list = []
        start_at = 0
        batch_size = 50  # Jira API limit per request

        while True:
            url = f"{self.base_board_url}/{board_id}/sprint?state=active,closed&startAt={start_at}&maxResults={batch_size}"
            
            response_data = await self._fetch_json(url)
            if not response_data or "values" not in response_data:
                self._log_error(f"Failed to retrieve sprints for board {board_id}")
                return None

            # Extract sprints
            if origin_board:
                batch_sprints = [sprint for sprint in response_data["values"] if int(sprint["originBoardId"]) == board_id]
            else:
                batch_sprints = [sprint for sprint in response_data["values"]]

            if name_filter:
                batch_sprints = [sprint for sprint in batch_sprints if name_filter in sprint["name"]]

            sprint_list.extend(batch_sprints)
            
            # Pagination check: Stop if fewer results than batch size
            if len(response_data["values"]) < batch_size:
                break  # No more sprints left to fetch

            # Move to the next batch
            start_at += batch_size

        self._log(f"Read {len(sprint_list)} sprints for board `{board_id}`")
        return sprint_list
    
    async def send_request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        allow_redirects: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Send a raw HTTP request to the Jira API.

        Args:
            method (str): HTTP method, e.g., 'GET', 'POST', 'PUT', 'DELETE'.
            path (str): The API path, e.g., '/rest/api/2/issue'.
            json (Optional[Dict]): JSON body (for POST/PUT/PATCH).
            params (Optional[Dict]): URL query parameters.
            headers (Optional[Dict]): Extra headers.
            allow_redirects (bool): Whether to follow redirects.

        Returns:
            Optional[Dict]: Response JSON, if available.
        """
        if self.session is None:
            raise RuntimeError("Session not started. Call `await start_session()`.")

        url = path if path.startswith("http") else f"{self.jira_url.rstrip('/')}/{path.lstrip('/')}"
        merged_headers = {**self.headers, **(headers or {})}

        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=merged_headers,
                json=json,
                params=params,
                allow_redirects=allow_redirects,
            ) as resp:
                
                if resp.status in (200, 201, 204):
                    if resp.content_length == 0 or resp.status == 204:
                        return None
                    
                    return await resp.json()
                else:
                    text = await resp.text()
                    self._log_error(f"{method} {url} failed: {resp.status} - {text}")
        except Exception as e:
            self._log_exception(f"Error with {method} {url}: {e}")
            raise

        return None
