from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from aiohttp import ClientResponse, ClientSession, ClientTimeout
DEFAULT_TIMEOUT = 120

class BaseAccount(ABC):
    """Base account class with common functionality"""

    def __init__(self,
                 wallet_address: str,
                 wallet_private_key: str,
                 x_auth_token: str = None,
                 proxy: Optional[str] = None,
                 external_id: Optional[str] = None,
                 id: Optional[int] = None,
                 **kwargs):
        self.wallet_address = wallet_address
        self.wallet_private_key = wallet_private_key
        self.x_auth_token = x_auth_token
        self.proxy = proxy
        self.external_id = external_id
        self.id = id
        self.session: Optional[ClientSession] = None
        self._init_additional_attributes(**kwargs)

    def _init_additional_attributes(self, **kwargs):
        """Initialize additional attributes from kwargs"""
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return f"[{self.wallet_address}]"

    async def get_session(self, headers: Dict = None, timeout: int = DEFAULT_TIMEOUT) -> ClientSession:
        """Get or create an aiohttp session"""
        if self.session is None:
            self.session = ClientSession(
                timeout=ClientTimeout(total=timeout),
                proxy=self.proxy if self.proxy else None,
                headers=headers or {}
            )
        return self.session

    async def close_session(self):
        """Close the session if it exists"""
        if self.session:
            await self.session.close()
            self.session = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert account to dictionary representation"""
        return {
            'wallet_address': self.wallet_address,
            'wallet_private_key': self.wallet_private_key,
            'x_auth_token': self.x_auth_token,
            'id': self.id,
            'external_id': self.external_id,
        }

