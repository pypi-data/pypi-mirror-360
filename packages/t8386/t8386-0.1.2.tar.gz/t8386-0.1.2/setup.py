from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
	long_description = fh.read()

setup(
	name="t8386",
	version="0.1.2",
	author="t8386",
	author_email="dinhty.luu@gmail.com",
	description="A Python package for managing blockchain accounts and interactions with REST APIs.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/tyluudinh/t8386",
	project_urls={
		"Bug Tracker": "https://github.com/tyluudinh/t8386/issues",
	},
	classifiers=[
		"Development Status :: 3 - Alpha",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.7",
		"Programming Language :: Python :: 3.8",
		"Programming Language :: Python :: 3.9",
		"Programming Language :: Python :: 3.10",
		"Programming Language :: Python :: 3.11",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Topic :: System :: Logging",
	],
	package_dir={"": "."},
	packages=find_packages(where="."),
	python_requires=">=3.7",
	install_requires=[
		  "requests",
			"colorama",
			"brotli",
			"cloudscraper",
			"apscheduler",
			"schedule",
			"pytz",
			"datetime",
			"Faker",
			"aiohttp",
			"logging",
			"supabase",
			"tenacity==8.2.3",
			"argparse",
			"Web3",
			"eth_account",
			"eth_abi",
			"mnemonic",
			"tronpy",
			"python-dotenv"
	],
	extras_require={
		"dev": [
			"pytest>=6.0",
			"pytest-cov",
			"black",
			"flake8",
		],
	},
)
