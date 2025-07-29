from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from aiohttp import ClientResponse, ClientSession, ClientTimeout

from .base_account import BaseAccount
from .base_rest_config import BaseRestConfig
from .logger import Logger
from .x import AppBindConfig, Twitter

class BaseRest(ABC):
    """Base REST client with common functionality"""

    def __init__(self, config: BaseRestConfig):
        if not isinstance(config, BaseRestConfig):
            raise TypeError("config must be an instance of BaseRestConfig")
        self.config = config

    async def get_code_x_connect(self, account: BaseAccount, app_bind_config: AppBindConfig, skip_check_x_token: bool = False) -> Optional[str]:
        """Connect a Twitter account using the x_auth_token."""
        if not skip_check_x_token:
            valid = Twitter.check_x_token(account.x_auth_token, proxy=account.proxy)

            if not valid:
                Logger.log_error(f"{account} Invalid X token")
                return False

        bind_result = Twitter.bind(
            app_bind_config=app_bind_config,
            auth_token=account.x_auth_token,
            proxy=account.proxy,
        )

        if not bind_result:
            Logger.log_error(f"{account} Failed to bind X account")
            return False
        Logger.log_success(f"{account} X account bound successfully")

        return bind_result.get('code', None)

    async def before_request(self, account: BaseAccount) -> ClientSession:
        """Prepare the account session before making a request."""
        session = await account.get_session()

        if not session or session.closed:
            Logger.log_info(
                f"Creating new session for {account.wallet_address}")
            session = await account.get_session()

        headers = await self.get_header_before_request(account) or {}

        default_headers = self.config.headers.copy()

        session._default_headers.update({
            **default_headers,
            **headers,
        })

        return session

    async def handle_response(self, response: ClientResponse) -> Optional[Dict[str, Any]]:
        """Handle the response from the server."""
        if response.status in [200, 201, 202, 204]:
            return await self.extract_response_json(response)
        else:
            Logger.log_error(
                f"Error response: Method={response.method} URL={response.url} Status={response.status} Reason={response.reason} Text={await response.text()}")
            return None

    async def extract_response_json(self, response: ClientResponse) -> Optional[Dict[str, Any]]:
        """Extract JSON from the response."""
        try:
            json_data = await response.json()
            return json_data
        except Exception as e:
            Logger.log_error(f"Error extracting JSON: {e}")
            return None

    async def get_header_before_request(self, account: BaseAccount) -> Dict[str, str]:
        """Get headers before making a request."""
        pass
