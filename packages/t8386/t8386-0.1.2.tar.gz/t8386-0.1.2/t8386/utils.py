import base64
import json
import random
import time
from typing import Optional
import uuid
from faker import Faker
import requests

from .logger import Logger

class Utils:

	@staticmethod
	def generate_gmail(email: str, multiple_dot: bool = False, allow_uppercase: bool = False, maximum: int = 10000) -> list:
		"""Generate a list of Gmail addresses based on the provided email."""
		if '@' not in email:
			return []

		local_part, domain = email.split('@')
		variations = []

		if multiple_dot:
			# TODO: Implement logic to generate multiple dot variations
			for i in range(len(local_part)):
				for j in range(i + 1, len(local_part) + 1):
					if i != j:
						variations.append(
							local_part[:i] + '.' + local_part[i:j] + local_part[j:])
			return variations
		else:
			variations = [local_part[:i] + '.' + local_part[i:]
				for i in range(1, len(local_part))]

		if allow_uppercase:
			# if not variations:
			# append domain into variations if no variations were created
			# variations.append(local_part + '@' + domain)

			for i in range(len(local_part)):
				for variation in variations[:]:
					if len(variation) > i:
						new_variation = variation[:i] + \
							variation[i].upper() + variation[i + 1:]
						if new_variation not in variations:
							variations.append(new_variation)
							if len(variations) >= maximum:
								break

		variations = [v + '@' + domain for v in variations if v]
		variations = list(set(variations)) # Remove duplicates
		if len(variations) > maximum:
			# Limit to maximum number of variations
			variations = variations[:maximum]
		return variations

	@staticmethod
	def extract_cookie_value(cookie_str: str, key: str) -> str:
		"""Extract a specific cookie value from a cookie string."""
		cookies = cookie_str.split(';')
		for cookie in cookies:
			if key in cookie:
				return cookie.split('=')[1].strip()
		return ""

	@staticmethod
	def jwt_to_dict(jwt_token: str) -> dict:
		"""Convert a JWT token to a dictionary."""
		try:
			header, payload, signature = jwt_token.split('.')
			payload += '=' * (-len(payload) % 4) # Add padding if necessary
			decoded_payload = json.loads(
				base64.urlsafe_b64decode(payload).decode('utf-8'))
			return decoded_payload
		except Exception as e:
			Logger.log_error(f"Error decoding JWT: {str(e)}")
			return {}

	@staticmethod
	def jwt_is_valid(jwt_token: str) -> bool:
		"""Check if a JWT token is valid (not expired)."""
		payload = Utils.jwt_to_dict(jwt_token)
		exp = payload.get("exp")
		if exp:
			return exp > time.time()
		return False

	@staticmethod
	def read_file(file_path: str):
		"""Read a text file and return its content as a list of lines."""
		try:
			with open(file_path, 'r', encoding='utf-8') as file:
				return [line.strip() for line in file if line.strip()]
		except FileNotFoundError:
			Logger.log_error(f"File not found: {file_path}")
			return []
		except Exception as e:
			Logger.log_error(f"Error reading file {file_path}: {str(e)}")
			return []

	@staticmethod
	def read_file_json(file_path: str):
		"""Read a JSON file and return its content."""
		try:
			with open(file_path, 'r', encoding='utf-8') as file:
				return json.load(file)
		except FileNotFoundError:
			Logger.log_error(f"File not found: {file_path}")
			return {}
		except json.JSONDecodeError:
			Logger.log_error(f"Error decoding JSON from file: {file_path}")
			return {}

	@staticmethod
	def extract_auth_tokens(file_path: str) -> list:
		"""Extract auth tokens from a list of data dictionaries."""
		auth_tokens = []
		data = Utils.read_file_json(file_path)
		for item in data:
			cookie = item.get("cookie", "")
			if not cookie:
				continue
			parts = cookie.split(';')
			for part in parts:
				if 'auth_token=' in part:
					auth_token = part.split('=')[1].strip()
					auth_tokens.append(auth_token)
					break # Stop after finding the first auth_token
		return auth_tokens

	@staticmethod
	def get_proxy_list(file_path: str) -> list:
		"""Read a list of proxies from a file."""
		try:
			with open(file_path, 'r', encoding='utf-8') as file:
				proxies = [line.strip() for line in file if line.strip()]
			return proxies
		except FileNotFoundError:
			Logger.log_error(f"File not found: {file_path}")
			return []

	@staticmethod
	def proxy_to_str(proxy: str) -> str:
		"""Convert a proxy string to a formatted string."""
		parts = proxy.split(':')
		if len(parts) == 4:
			return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
		elif len(parts) == 2:
			return f"http://{parts[0]}:{parts[1]}"
		else:
			Logger.log_error(f"Invalid proxy format: {proxy}")
		return proxy

	@staticmethod
	def generate_nonce(length: int) -> str:
		"""Generate a nonce for use in requests. Remove special characters and padding."""
		return base64.urlsafe_b64encode(
			random.randbytes(length)).decode('utf-8').rstrip('=')

	@staticmethod
	def generate_uuid() -> str:
		"""Generate a UUID string."""
		return str(uuid.uuid4())

	@staticmethod
	def retry_get_proxy(proxies: list, retries: int = 3) -> Optional[str]:
		"""Retry getting a working proxy"""
		for attempt in range(retries):
			if attempt > 0:
				Logger.log_warning(
					f"Retrying to get proxy (Attempt {attempt + 1}/{retries})")

			proxy = Utils.proxy_to_str(
				random.choice(proxies)) if proxies else None

			if proxy and Utils.check_live_proxy(proxy):
				return proxy

			time.sleep(1) # Wait before retrying

		return None

	@staticmethod
	def check_live_proxy(proxy: str) -> bool:
		"""Check if a proxy is live by making a request to a known URL."""

		try:
			response = requests.get("https://api.ipify.org?format=json",
				proxies={"http": proxy, "https": proxy}, timeout=5)
			response.raise_for_status()
			ip_info = response.json()

			# assuming the response contains an "ip" field
			ip = ip_info.get("ip", "Unknown IP")

			Logger.log_success(f"✅ Proxy is live: {ip}")

			return True
		except requests.RequestException as e:
			Logger.log_error(f"❌ Error checking IP: {str(e)}")
			return False

	# auth_tokens = extract_auth_tokens("x1261.json")

	# auth_token = auth_tokens.pop(0) if auth_tokens else None

	# print(f"Extracted {len(auth_tokens)} auth tokens:")
	@staticmethod
	def random_username_with_prefix(length: int = 15) -> str:
		"""Generate a random username with a specified prefix."""
		fake = Faker()
		username = fake.user_name()

		prefix = random.choice(['eth_', 'btc_', 'airdrop_', 'doge_'])

		cleaned = ''.join(c for c in username if c.isalnum() or c == '_')

		cleaned = prefix + cleaned

		return cleaned[:length]

	@staticmethod
	def random_username(length: int = 20) -> str:
		"""Generate a random username of specified length."""
		fake = Faker()
		username = fake.user_name()
		# cleaned = ''.join(c for c in username if c.isalnum() or c == '_')

		prefixes = ['eth_', 'btc_', 'airdrop_', 'doge_', 'satoshi_', 'whale_', 'crypto_', 'nft_', 'web3_']

		# if cleaned[0].isdigit():
		cleaned = random.choice(prefixes) + username + str(random.randint(1, 9999))
		return cleaned[:length]

	@staticmethod
	def append_to_file(file_path: str, data: str):
		"""Append data to a file."""
		try:
			with open(file_path, 'a', encoding='utf-8') as file:
				file.write(data + '\n')
		except Exception as e:
			Logger.log_error(f"Error appending to file {file_path}: {str(e)}")

	@staticmethod
	def check_jwt_token_validity(jwt_token: str) -> bool:
		"""Check if a JWT token is valid."""
		try:
			if not jwt_token:
				return False
			payload = Utils.jwt_to_dict(jwt_token)
			exp = payload.get("exp")
			if exp and exp > time.time():
				return True
		except Exception as e:
			Logger.log_error(f"Error checking JWT token validity: {str(e)}")
		return False

	@staticmethod
	def generate_api_keys() -> tuple:
		"""Generate a random API key and secret key."""
		api_key = base64.urlsafe_b64encode(
			random.randbytes(16)).decode('utf-8').rstrip('=')
		api_secret = base64.urlsafe_b64encode(
			random.randbytes(32)).decode('utf-8').rstrip('=')
		return api_key, api_secret

	@staticmethod
	def tuple_to_int(tup):
		if len(tup) == 1:
			return tup[0]
		else:
			return tup[0] * (10 ** (len(tup) - 1)) + Utils.tuple_to_int(tup[1:])

	@staticmethod
	def tuple_to_bool(tup):
		"""Convert a tuple of integers to a boolean value."""
		if len(tup) == 1:
			return bool(tup[0])
		else:
			return bool(tup[0]) or Utils.tuple_to_bool(tup[1:])

	@staticmethod
	def read_proof_data_file(file_path: str) -> list:
		"""Read proof data from a file and return as a list."""
		try:
			with open(file_path, 'r', encoding='utf-8') as file:
				result = []
				for line in file:
					if line.strip():
						try:
							data = json.loads(line.strip())
							if isinstance(data, dict):
								result.append(data)
						except json.JSONDecodeError:
							Logger.log_error(f"Error decoding JSON from line: {line.strip()}")
				return result
		except FileNotFoundError:
			Logger.log_error(f"File not found: {file_path}")
			return []
		except Exception as e:
			Logger.log_error(f"Error reading file {file_path}: {str(e)}")
			return []

	@staticmethod
	def read_proof_data() -> list:
		data = Utils.read_proof_data_file("proof.txt")
		data_used = Utils.read_proof_data_file("proof_used.txt")

		Logger.log_info(f"Total proof data: {len(data)}")
		Logger.log_info(f"Total proof used data: {len(data_used)}")

		if not data or not isinstance(data, list):
			Logger.log_warning("No valid proof data found.")
			return []
		if not data_used or not isinstance(data_used, list):
			Logger.log_warning("No valid proof used data found.")
			return []
		
		# print(data[0])
		# print(data_used[0])
		
		# Filter out used data
		result = []
		for item in data:
			task_id = item['taskId']

			if any(used_item['taskId'] == task_id for used_item in data_used):
				# print(f"Skipping used taskId: {task_id}")
				continue
			result.append(item)


		Logger.log_info(f"Total proof data remaining: {len(result)}")

		return result
	
	@staticmethod
	def read_file_csv(file_path: str) -> list:
		"""Read a CSV file and return its content as a list of dictionaries."""
		try:
			with open(file_path, 'r', encoding='utf-8') as file:
				lines = file.readlines()
				if not lines:
					return []
				headers = lines[0].strip().split(',')
				data = []
				for line in lines[1:]:
					values = line.strip().split(',')
					if len(values) == len(headers):
						data.append(dict(zip(headers, values)))
				return data
		except FileNotFoundError:
			Logger.log_error(f"File not found: {file_path}")
			return []
		except Exception as e:
			Logger.log_error(f"Error reading file {file_path}: {str(e)}")
			return []
