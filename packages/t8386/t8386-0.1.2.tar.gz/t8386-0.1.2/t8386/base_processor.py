from abc import ABC, abstractmethod
import asyncio
import math
import threading
import time
from typing import Optional, Dict, Any, List

import concurrent

from .base_rest import BaseRest
from .base_account import BaseAccount
from .logger import Logger
from .utils import Utils
from .wallets import WalletUtils
from .supbase_db import SupabseDB
class BaseProcessor(ABC):
    """Base processor class for handling accounts"""
    table_name = ""
    proxies: List[str] = []

    def __init__(self, table_name: str, file_proxy: str = "live.txt"):
        self.table_name = table_name
        self.rest: Optional[BaseRest] = None
        self.accounts: List[BaseAccount] = []
        self.proxies: List[str] = Utils.get_proxy_list(file_proxy)
        self.db = SupabseDB()
        Logger.log_info("" + "-" * 100)
        Logger.log_info(f"Initialized BaseProcessor with table: {self.table_name}")
        Logger.log_info(f"Loaded {len(self.proxies)} proxies from {file_proxy}")
        Logger.log_info(f"App started at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
        Logger.log_info("" + "-" * 100)

    def prepare_proxy(self) -> Optional[str]:
        """Prepare a proxy for the account."""
        return Utils.retry_get_proxy(proxies=self.proxies, retries=5)

    async def prepare_account(self, proxy: str = None) -> BaseAccount or None:  # type: ignore
        """Prepare a new account with a wallet address and private key."""

        wallet = WalletUtils.generate_wallet()

        account = BaseAccount(
            wallet_address=wallet.address,
            wallet_private_key=wallet.private_key,
            external_id=None,
            x_auth_token=None,
            proxy=proxy
        )

        if not proxy:
            proxy = Utils.retry_get_proxy(proxies=self.proxies, retries=5)
            account.proxy = proxy

        return account

    def check_auth_token_existed_db(self, x_auth_token: str) -> bool:
        """Check if the account already exists in the database."""
        if not isinstance(x_auth_token, str):
            raise TypeError("x_auth_token must be a string")

        if x_auth_token:
            exist_db = self.db._supabase.table(self.table_name).select(
                "*").eq("x_auth_token", x_auth_token).execute()
            if exist_db.data:
                return True
        return False


    async def save_account(self, account: BaseAccount):
        """Save account to the database"""
        if not isinstance(account, BaseAccount):
            raise TypeError("account must be an instance of BaseAccount")

        data = account.to_dict()

        if data.get('id') is None or data.get('id') == 0:
            del data['id']  # Remove id if it doesn't exist
            self.db.insert_data(table=self.table_name, data=data)
            Logger.log_success(f"{account} Inserted new account: {data}")
        else:
            self.db.update_data(table=self.table_name, data=data, key_eq="id")
            Logger.log_success(f"{account} Updated existing account: {data}")

    @abstractmethod
    async def process_single_account(self, account: BaseAccount):
        """Process a single account"""
        pass

    # @abstractmethod
    # async def process_accounts_batch(self, accounts: list[BaseAccount]):
    #     """Process a batch of accounts"""
    #     pass

    # def prepare_proxy(self, proxy: str = None) -> str or None:  # type: ignore
    #     """Prepare a proxy for the account."""
    #     proxy = Utils.retry_get_proxy(proxies=self.proxies, retries=5)
    #     return proxy
    async def after_process(self, account: BaseAccount):
        """Cleanup after processing an account"""
        await account.close_session()
        Logger.log_info(f"{account} Finished processing")

    def run_account_thread(self, account: BaseAccount, func_name: str = "process_single_account", **kwargs):
        """Create and start a thread for account processing"""
        thread = threading.Thread(
            target=self.run_account_task,
            args=(account, func_name),
            kwargs=kwargs,
            name=f"{BaseAccount.__name__}-{func_name}-{account}"
        )
        thread.start()
        return thread

    def run_account_task(self, account: BaseAccount, func_name: str, **kwargs):
        """Run the account registration in a separate thread."""
        try:
            method = getattr(self, func_name)
            asyncio.run(method(account, **kwargs))
        except Exception as e:
            # if e.__class__.__name__ == "KeyboardInterrupt":
            Logger.log_error(f"{account} {func_name} Error in thread for: {e.__class__.__name__} -> {str(e)}")
        finally:
            asyncio.run(self.after_process(account))
            Logger.log_info(
                f"{account} {func_name} Finished processing in thread.")

    async def after_process(self, account: BaseAccount):
        """Cleanup after processing an account"""
        await account.close_session()
        Logger.log_info(f"{account} Finished processing")

    async def process_with_workers(self, batch_size: int = 100):
        """Process accounts using worker threads"""
        total_accounts = len(self.accounts)
        num_workers = math.ceil(total_accounts / batch_size)

        Logger.log_info(
            f"Processing {total_accounts} accounts with {num_workers} workers")
        Logger.log_info(f"Batch size: {batch_size} accounts per worker")

        batches = [
            self.accounts[i:i + batch_size]
            for i in range(0, total_accounts, batch_size)
        ]

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            loop = asyncio.get_event_loop()
            futures = [
                loop.create_task(self.process_accounts_batch(batch))
                for batch in batches
            ]
            await asyncio.gather(*futures)

        Logger.log_info(f"Completed processing {total_accounts} accounts")
