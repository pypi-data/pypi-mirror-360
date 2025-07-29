class BaseWallet:
    """Base wallet class for common wallet functionality"""

    def __init__(self, wallet_address: str, wallet_private_key: str):
        self.address = wallet_address
        self.private_key = wallet_private_key
