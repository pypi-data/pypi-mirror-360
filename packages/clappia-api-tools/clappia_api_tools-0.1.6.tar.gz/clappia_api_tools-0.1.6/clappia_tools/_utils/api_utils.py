import os
import json
import requests
from typing import Optional, Dict, Any, Tuple
from clappia_tools._utils.logging_utils import get_logger

logger = get_logger(__name__)


class ClappiaAPIUtils:
    """Utilities for Clappia API interactions"""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        workplace_id: str,
        timeout: int = 30,
    ):
        """
        Initialize API utilities with configurable parameters

        Args:
            api_key: Clappia API key
            base_url: API base URL
            workplace_id: Workplace ID
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url
        self.workplace_id = workplace_id
        self.timeout = timeout

    def validate_environment(self) -> Tuple[bool, str]:
        """Validate that required configuration is available"""
        if not self.api_key:
            return (
                False,
                "API key is not configured",
            )
        if not self.base_url:
            return (
                False,
                "Base URL is not configured",
            )
        if not self.workplace_id:
            return (
                False,
                "Workplace ID is not configured",
            )
        return True, ""

    def get_headers(self) -> Dict[str, str]:
        """Get standard headers for API requests"""
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "workplaceId": self.workplace_id,
        }

    def handle_response(
        self, response: requests.Response
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Handle API response and return structured result

        Returns:
            Tuple of (success: bool, error_message: str, data: dict)
        """
        if response.status_code == 200:
            try:
                return True, None, response.json()
            except json.JSONDecodeError:
                logger.warning(f"Valid response but invalid JSON: {response.text}")
                return True, None, {"raw_response": response.text}

        error_message = self._format_error_message(response)
        return False, error_message, None

    def _format_error_message(self, response: requests.Response) -> str:
        """Format error message from API response"""
        if response.status_code in [400, 401, 403, 404]:
            try:
                error_data = response.json()
                return f"API Error ({response.status_code}): {json.dumps(error_data, indent=2)}"
            except json.JSONDecodeError:
                return f"API Error ({response.status_code}): {response.text}"
        else:
            return f"Unexpected API response ({response.status_code}): {response.text}"

    def make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Make HTTP request to Clappia API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (will be appended to base_url)
            data: Request body data (for POST/PUT requests)
            params: Query parameters (for GET requests)

        Returns:
            Tuple of (success: bool, error_message: str, response_data: dict)
        """
        env_valid, env_error = self.validate_environment()
        if not env_valid:
            return False, f"Configuration error: {env_error}", None

        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = self.get_headers()

        try:
            logger.info(f"Making {method} request to {url}")
            if data:
                logger.debug(f"Request data: {json.dumps(data, indent=2)}")

            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=self.timeout,
            )

            logger.info(f"Response status: {response.status_code}")
            logger.debug(f"Response body: {response.text}")

            return self.handle_response(response)

        except requests.exceptions.Timeout:
            return False, f"Request timeout after {self.timeout} seconds", None
        except requests.exceptions.ConnectionError:
            return False, "Connection error - unable to reach Clappia API", None
        except Exception as e:
            return False, f"Unexpected error: {str(e)}", None
