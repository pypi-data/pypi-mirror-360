import time
from colorama import Fore, Style

class Logger:
	"""A simple logger class to print messages with a timestamp."""

	@staticmethod
	def log_info(message: str):
		"""Prints a message with a timestamp."""
		print(
			f"{Fore.BLUE}[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}{Style.RESET_ALL}")

	@staticmethod
	def log_error(message: str):
		"""Prints an error message with a timestamp."""
		print(
			f"{Fore.RED}[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}{Style.RESET_ALL}")

	@staticmethod
	def log_success(message: str):
		"""Prints a success message with a timestamp."""
		print(
			f"{Fore.GREEN}[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}{Style.RESET_ALL}")

	@staticmethod
	def log_warning(message: str):
		"""Prints a warning message with a timestamp."""
		print(
			f"{Fore.YELLOW}[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}{Style.RESET_ALL}")

	@staticmethod
	def log_debug(message: str):
		"""Prints a debug message with a timestamp."""
		print(
			f"{Fore.CYAN}[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}{Style.RESET_ALL}")

	@staticmethod
	def log(message: str):
		"""Prints a generic message with a timestamp."""
		print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")

	@staticmethod
	def log_hana(message: str):
		"""Prints a message with a timestamp in HANA style."""
		print(
			f"{Fore.MAGENTA}[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}{Style.RESET_ALL}")
