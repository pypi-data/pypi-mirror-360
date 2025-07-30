from typing import Optional
from clappia_tools._utils.api_utils import ClappiaAPIUtils


class BaseClappiaClient:
    """Base client with shared functionality for all Clappia clients.
    
    This class provides the common initialization and shared utilities
    that all specialized Clappia clients will inherit from.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        workplace_id: Optional[str] = None,
        timeout: int = 30,
    ):
        """Initialize base Clappia client.

        Args:
            api_key: Clappia API key.
            base_url: API base URL.
            workplace_id: Workspace ID.
            timeout: Request timeout in seconds.
        """
        self.api_utils = ClappiaAPIUtils(api_key, base_url, workplace_id, timeout)