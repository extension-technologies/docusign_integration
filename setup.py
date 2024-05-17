from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in docusign_integration/__init__.py
from docusign_integration import __version__ as version

setup(
	name="docusign_integration",
	version=version,
	description="Docusign Integration",
	author="Extension",
	author_email="hello@extensioncrm.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
