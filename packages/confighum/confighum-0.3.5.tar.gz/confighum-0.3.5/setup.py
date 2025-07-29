import pathlib
from setuptools import setup, find_packages

DISTRIBUTION_NAME = "confighum"
THIS_DIR = pathlib.Path(__file__).parent
LONG_DESCRIPTION = (THIS_DIR / "README.md").read_text()

from setuptools import setup, find_packages

setup(
    name="confighum",
    version="0.3.5",
    description="A collection of sinontop utilities and configurations.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Sintacs Ao",
    author_email="adas334@gmail.com",
    packages=find_packages(),
    python_requires=">=3.6",
)
