import json
import logging
import time 
import tempfile
import os
import asyncio
import aiohttp
import openai

from typing import Optional, Dict, Union
from openai import AsyncAzureOpenAI

from ..utility_base import UtilityBase
from ..logger import Logger, LogWrapper


# Define exceptions
class OpenAIClientError(Exception):
    """Custom exception for AzureOpenAIClient errors."""
    pass


class AzureOpenAIClient(UtilityBase):
    """
    A wrapper for interacting with Azure OpenAI.
    """
    SESSION_DIR = "sessions"

    def __init__(
            self, 
            azure_endpoint: str,
            api_key: str,
            api_version: str,
            llm_model: str,
            default_system_message: str = "You are a helpful assistant.",
            max_tokens: int = 4000,
            temperature: float = 0.0,
            top_p: float = 0.95,
            frequency_penalty: float = 0.0,
            presence_penalty: float = 0.0,
            include_message_history: bool = True,
            save_sessions_to_disk: bool = True,
            verbose: bool = False,
            log_messages: bool = False,
            logger: Optional[Union[logging.Logger | Logger | LogWrapper]] = None,
            log_level: Optional[int] = None
        ):
        """
        Initializes the LLMWrapper with the provided parameters.

        Args:
            azure_endpoint (str): Azure endpoint URL.
            api_key (str): API key for Azure OpenAI.
            api_version (str): API version for Azure OpenAI.
            llm_model (str): The model name to use.
            default_system_message (str, optional): Default system message to guide the LLM's behavior. Defaults to "You are a helpful assistant.".
            max_tokens (int, optional): Maximum tokens for the response. Defaults to 4000.
            temperature (float, optional): Sampling temperature for randomness. Defaults to 0.0.
            top_p (float, optional): Probability for nucleus sampling. Defaults to 0.95.
            frequency_penalty (float, optional): Penalize repeated tokens. Defaults to 0.0.
            presence_penalty (float, optional): Penalize repeated topics. Defaults to 0.0.
            include_message_history (bool, optional): Whether to include full history in requests. Defaults to True.
            save_sessions_to_disk (bool, optional): Whether to backup the chat history onto the hard drive. Defaults to True.
            verbose (bool, optional): If true debug messages are logged during the operations.
            log_messages (bool, optional): If true messages and system messages are logged too.
            logger (Optional[Union[logging.Logger, Logger, LogWrapper]], optional): Optional logger instance. If not provided, a default logger is used.
            log_level (Optional[int], optional): Optional log level. If not provided, INFO level will be used for logging.
        """
        # Init base class
        super().__init__(verbose, logger, log_level)
        self.log_messages = log_messages

        # Validate required parameters
        self._validate_initialization_params(azure_endpoint, api_key, api_version, llm_model)

        # Set Azure OpenAI parameters
        self.azure_endpoint = azure_endpoint
        self.api_key = api_key
        self.api_version = api_version
        self.llm_model = llm_model
        self.default_system_message = {"role": "system", "content": default_system_message}

        # Model configuration
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.include_message_history = include_message_history

        # Azure OpenAI Clients
        self.async_client = AsyncAzureOpenAI(azure_endpoint=azure_endpoint, api_key=api_key, api_version=api_version)

        # Initialize storage
        self.save_sessions_to_disk = save_sessions_to_disk
        if save_sessions_to_disk:
            os.makedirs(self.SESSION_DIR, exist_ok=True)
            self._load_all_sessions_from_disk()
        else:
            self.sessions = {}

        self._log(f"LLMWrapper initialized successfully. Conversation history {'enabled' if include_message_history else 'disabled'}.")
        self._log(f"Default system message: {default_system_message}")

    def request_completion(
            self, 
            message_content: str, 
            session_id: Optional[str] = None, 
            timeout: int = 30,
            retries: int = 3, 
            retry_delay: float = 2.0
        ) -> str:
        """
        Sends a new message to the LLM and retrieves the response with retry support.
        Do not use this function inside a running event loop.

        Args:
            message_content (str): The user's message to send to the LLM.
            session_id (Optional[str], optional): ID of the conversation session. Defaults to None.
            timeout (int, optional): Timeout for the API request (in seconds). Defaults to 30.
            retries (int, optional): Number of retry attempts for transient failures. Defaults to 3.
            retry_delay (float, optional): Delay (in seconds) between retries. Defaults to 2.0.

        Returns:
            str: The LLM's response.

        Raises:
            ValueError: If message content is empty.
            OpenAIClientError: If the request fails after all retries.
        """
        if not message_content.strip():
            raise ValueError("Message content cannot be empty.")

        # Request a completion, try it again "retries" times, if it fails
        for attempt in range(retries):
            try:
                response = asyncio.run(self._request_completion(message_content, session_id, timeout))
                return response
            except Exception as e:
                self._log_warning(f"Attempt {attempt + 1} failed. Retrying in {retry_delay * (2 ** attempt):.2f} seconds...")
                time.sleep(retry_delay * (2 ** attempt))

                if (attempt+1) == retries:
                    raise OpenAIClientError("Failed to complete the request after multiple retries.") from e

    async def request_completion_async(
            self, 
            message_content: str, 
            session_id: Optional[str] = None, 
            timeout: int = 30,
            retries: int = 3, 
            retry_delay: float = 2.0
        ) -> str:
        """
        Sends a new message to the LLM and retrieves the response with retry support asynchronously.

        Args:
            message_content (str): The user's message to send to the LLM.
            session_id (Optional[str], optional): ID of the conversation session. Defaults to None.
            timeout (int, optional): Timeout for the API request (in seconds). Defaults to 30.
            retries (int, optional): Number of retry attempts for transient failures. Defaults to 3.
            retry_delay (float, optional): Delay (in seconds) between retries. Defaults to 2.0.

        Returns:
            str: The LLM's response.

        Raises:
            ValueError: If message content is empty.
            OpenAIClientError: If the request fails after all retries.
        """
        if not message_content.strip():
            raise ValueError("Message content cannot be empty.")

        for attempt in range(retries):
            try:
                response = await self._request_completion(message_content, session_id, timeout)
                return response
            except Exception as e:
                self._log_warning(f"Attempt {attempt + 1} failed. Retrying in {retry_delay * (2 ** attempt):.2f} seconds...")
                await asyncio.sleep(retry_delay * (2 ** attempt))

                if (attempt+1) == retries:
                    raise OpenAIClientError("Failed to complete the request after multiple retries.") from e

    def trim_conversation_history(self, session_id: Optional[str] = None, max_length: int = 50) -> None:
        """
        Trims the conversation history to the last `max_length` messages.

        Args:
            session_id (Optional[str], optional): ID of the conversation session. Defaults to None.
            max_length (int, optional): The maximum number of messages to retain in the history. Defaults to 50.

        Raises:
            ValueError: If max_length is not positive.
        """
        if max_length <= 0:
            raise ValueError("`max_length` must be a positive integer.")

        session_id = self._validate_session(session_id)
        self._log(f"Trimming conversation history for session `{session_id}`")

        original_length = len(self.sessions[session_id])
        if original_length > max_length:
            self.sessions[session_id] = self.sessions[session_id][-max_length:]
            self._save_session_to_disk(session_id)

    def get_message_count(self, session_id: Optional[str] = None) -> int:
        """
        Gets the message count from the message history between the user and the LLM.

        Args:
            session_id (Optional[str], optional): ID of the conversation session. Defaults to None.

        Returns:
            int: The number of messages in the session.
        """
        session_id = self._validate_session(session_id)

        return len(self.sessions[session_id])

    def change_system_message(self, system_message: str, session_id: Optional[str] = None) -> None:
        """
        Changes the default system message.

        Args:
            system_message (str): The new system message for the completion API.
            session_id (Optional[str], optional): ID of the conversation session. Defaults to None.

        Raises:
            ValueError: If system_message is empty.
        """
        if not system_message.strip():
            raise ValueError("System message cannot be empty.")

        session_id = self._validate_session(session_id)

        if self.log_messages:
            self._log(f"Changing system message for session `{session_id}`. New system message: `{system_message}`")
        
        new_system_message: Dict[str, str] = {"role": "system", "content": system_message}
        self.sessions[session_id][0] = new_system_message

    def get_conversation_history_as_text(self, session_id: Optional[str] = None) -> str:
        """
        Returns the conversation history as a formatted plain text string.

        Args:
            session_id (Optional[str], optional): ID of the session. Defaults to None.

        Returns:
            str: The formatted conversation history as plain text.
        """
        session_id = self._validate_session(session_id)

        if not self.sessions[session_id]:
            return []

        history = "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in self.sessions[session_id])
        return history

    def reset_conversation(self, session_id: Optional[str] = None) -> None:
        """
        Resets the conversation history to the default messages.

        Args:
            session_id (Optional[str], optional): ID of the session. Defaults to None.
        """
        session_id = self._validate_session(session_id)
        self._log(f"Resetting conversation for session `{session_id}`.")

        if len(self.sessions[session_id]) <= 1:  # Only system message exists
            self._log_warning(f"Session '{session_id}' is already at its default state.")

        self.sessions[session_id] = [self.sessions[session_id][0]] # Preserve system message
        self._save_session_to_disk(session_id)

    def save_conversation(self, file_path: str, session_id: Optional[str] = None) -> None:
        """
        Saves the current conversation history.

        Args:
            file_path (str): The path to save the conversation history as a JSON file.
            session_id (Optional[str], optional): ID of the conversation session. Defaults to None.
        """
        session_id = self._validate_session(session_id)
        self._log(f"Saving conversation for session `{session_id}`.")

        with tempfile.NamedTemporaryFile("w", delete=False) as tmp_file:
            json.dump(self.sessions[session_id], tmp_file)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())
        os.replace(tmp_file.name, file_path)

    def load_conversation(self, file_path: str, session_id: Optional[str] = None) -> None:
        """
        Loads a conversation history from a JSON file.

        Args:
            file_path (str): The path to the JSON file containing the conversation history.
            session_id (Optional[str], optional): ID of the conversation session. Defaults to None.

        Raises:
            ValueError: If the loaded file is not valid or has an invalid JSON format.
        """
        session_id = self._validate_session(session_id)
        self._log(f"Loading conversation for session `{session_id}`.")

        try:
            with open(file_path, 'r') as f:
                loaded_session = json.load(f)
                if not isinstance(loaded_session, list):
                    raise ValueError("Invalid conversation format. Expected a list of messages.")

            self.sessions[session_id] = loaded_session
        except FileNotFoundError:
            self._log_warning(f"File '{file_path}' not found. Starting a fresh session for '{session_id}'.")
            self.reset_conversation(session_id)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in the conversation file.")
        except Exception as e:
            raise e

    async def _request_completion(self, message_content: str, session_id: Optional[str], timeout: int) -> str:
        """
        Internal function to handle synchronous and asynchronous requests to the OpenAI API.

        Args:
            message_content (str): The user's message.
            session_id (Optional[str]): ID of the conversation session.
            timeout (int): Request timeout in seconds.

        Returns:
            str: The LLM's response.

        Raises:
            asyncio.TimeoutError: If the request times out.
            openai.error.APIError: If the OpenAI API returns an API error.
            openai.error.APIConnectionError: If a connection error occurs.
            openai.error.InvalidRequestError: If the request is invalid.
            openai.error.AuthenticationError: If authentication fails.
            openai.error.PermissionError: If permission is denied.
            openai.error.RateLimitError: If rate limit is exceeded.
            aiohttp.ClientResponseError: If an HTTP error occurs.
            aiohttp.ClientConnectionError: If a connection error occurs.
            ValueError: For invalid inputs.
            Exception: For any other unexpected errors.
        """
        session_id = self._validate_session(session_id)

        if self.log_messages:
            self._log(f"Requesting completion for session `{session_id}`. Message `{message_content}`")

        new_message = {"role": "user", "content": message_content}
        messages = self.sessions[session_id] + [new_message]

        try:
            completion = await self.async_client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                timeout=timeout
            )
            response = completion.choices[0].message.content

            if self.include_message_history:
                self.sessions[session_id].append(new_message)
                self.sessions[session_id].append({"role": "assistant", "content": response})
                self._save_session_to_disk(session_id)

            return response

        # --- Timeout from asyncio or OpenAI directly ---
        except (asyncio.TimeoutError, openai.error.Timeout):
            self._log_exception(f"The request timed out (timeout={timeout}).")
            raise

        # --- OpenAI-specific error types ---
        except openai.error.APIError as e:
            self._log_exception(f"OpenAI API error: {e}")
            raise
        except openai.error.APIConnectionError as e:
            self._log_exception(f"Failed to connect to OpenAI API: {e}")
            raise
        except openai.error.InvalidRequestError as e:
            self._log_exception(f"Invalid request to OpenAI API: {e}")
            raise
        except openai.error.AuthenticationError:
            self._log_exception("Authentication with OpenAI API failed.")
            raise
        except openai.error.PermissionError:
            self._log_exception("Permission denied for OpenAI API.")
            raise
        except openai.error.RateLimitError:
            self._log_exception("Rate limit exceeded for OpenAI API.")
            raise

        # --- aiohttp-specific HTTP/connection errors ---
        except aiohttp.ClientResponseError as e:
            self._log_exception(f"HTTP Error {e.status}: {e.message}")
            raise OpenAIClientError()
        except aiohttp.ClientConnectionError as e:
            self._log_exception(f"Connection error while accessing OpenAI API: {e}")
            raise OpenAIClientError()

        # --- General issues ---
        except ValueError as e:
            self._log_exception(f"Invalid input: {e}")
            raise
        except Exception as e:
            self._log_exception(f"An unexpected error occurred: {e}")
            raise
        
    def _load_all_sessions_from_disk(self) -> None:
        """
        Loads all session files into memory.
        """
        self.sessions = {}

        for filename in os.listdir(self.SESSION_DIR):
            if filename.endswith(".json"):
                session_id = filename[:-5]  # Remove '.json'

                with open(os.path.join(self.SESSION_DIR, filename), "r") as file:
                    self.sessions[session_id] = json.load(file)

    def _save_session_to_disk(self, session_id: str) -> None:
        """
        Saves a session to a file.

        Args:
            session_id (str): ID of the conversation session.
        
        Raises:
            ValueError: If session ID is empty.
        """
        if not self.save_sessions_to_disk or not self.include_message_history:
            return
        
        if not session_id.strip():
            raise ValueError("Session ID cannot be empty.")
        
        filepath = os.path.join(self.SESSION_DIR, f"{session_id}.json")
        with open(filepath, "w") as file:
            json.dump(self.sessions[session_id], file)

    def _validate_session(self, session_id: Optional[str] = None) -> str:
        """
        Validates the session ID and returns a valid session identifier.
        If the session does not exist, initializes it with the default system message.

        Args:
            session_id (Optional[str], optional): The session ID to validate. Defaults to None.

        Returns:
            str: A valid session ID.
        """
        session_id = session_id or "default"
        if session_id not in self.sessions:
            self.sessions[session_id] = [self.default_system_message]
            self._save_session_to_disk(session_id)

        return session_id

    def _validate_initialization_params(self, azure_endpoint: str, api_key: str, api_version: str, llm_model: str) -> None:
        """
        Validates the Azure OpenAI parameters.

        Args:
            azure_endpoint (str): Azure endpoint URL.
            api_key (str): API key for Azure OpenAI.
            api_version (str): API version for Azure OpenAI.
            llm_model (str): The model name to use.

        Raises:
            OpenAIClientError: If any of the configuration parameters are missing.
        """
        self._log("Validating Azure OpenAI parameters.")

        if not all([azure_endpoint, api_key, api_version, llm_model]):
            raise OpenAIClientError("Azure OpenAI configuration parameters are missing.")
