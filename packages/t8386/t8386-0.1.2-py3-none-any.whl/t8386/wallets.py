from eth_account import Account
from eth_account.messages import encode_defunct
from mnemonic import Mnemonic
from web3 import Web3

import json
import time
import sys
import os
from tronpy import Tron
from tronpy.keys import PrivateKey
import hashlib


class Wallet:
	def __init__(self, mnemonic, address, private_key):
		self.mnemonic = mnemonic
		self.address = address
		self.private_key = private_key

	def __str__(self):
		return f"Mnemonic: {self.mnemonic}\nAddress: {self.address}\nPrivate key: {self.private_key}"

class WalletUtils:

	@staticmethod
	def generate_wallet():
		"""Generate Ethereum wallet using pure Python libraries"""
		mnemo = Mnemonic("english")
		mnemonic = mnemo.generate(strength=128)

		# account = Account.create(f'{mnemonic} 1530')

		# Derive private key and address from mnemonic
		Account.enable_unaudited_hdwallet_features()
		account = Account.from_mnemonic(mnemonic)

		return Wallet(mnemonic, account.address, account.key.hex())

	@staticmethod
	def recover(message, signature):
		web3 = Web3(Web3.HTTPProvider("https://rpc.testnet.humanity.org"))
		# account = Account.recpv(message, signature=signature)
		message_encoded = encode_defunct(text=message)
		account = web3.eth.account.recover_message(message_encoded, signature)
		return account

	@staticmethod
	def personal_sign(message, private_key):
		account = Account.from_key(private_key)

		# print(account.key.hex())

		# web3 = Web3()

		message_encoded = encode_defunct(text=message)

		signature = Web3().eth.account.sign_message(
			message_encoded, private_key=account.key.hex())

		sign = signature.signature.hex()

		return sign if sign.startswith('0x') else '0x' + sign

	@staticmethod
	def wallet_from_private_key(private_key):
		"""Create a Wallet object from a private key"""
		account = Account.from_key(private_key)
		return Wallet("N/A", account.address, account.key.hex())

	@staticmethod	
	def generate_tron_wallet() -> Wallet:
		"""Generate a TRON wallet"""
		# Generate private key
		private_key = PrivateKey.random()
		public_key = private_key.public_key

		# Get address from public key
		address = public_key.to_base58check_address()

		return Wallet(
			mnemonic="N/A", # TRON doesn't use mnemonic by default
			address=address,
			private_key=private_key.hex()
		)

	@staticmethod
	def tron_sign_message(message: str, private_key: str) -> str:
		"""Sign a message using TRON private key"""
		try:
			# Create private key instance
			pk = PrivateKey(bytes.fromhex(private_key))

			# Prepare the message
			message_bytes = bytes(message, 'utf-8')
			message_hash = hashlib.sha256(message_bytes).digest()

			# Sign the message
			signature = pk.sign_msg_hash(message_hash)

			# Convert signature to hex
			signature_hex = signature.hex()
			return f"0x{signature_hex}"

		except Exception as e:
			raise Exception(f"Error signing TRON message: {str(e)}")
