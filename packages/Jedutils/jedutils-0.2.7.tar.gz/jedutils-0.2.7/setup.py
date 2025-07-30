from re import findall
from setuptools import setup, find_packages


with open("jedutils/__init__.py", "r") as f:
    version = findall(r"__version__ = \"(.+)\"", f.read())[0]

with open("README.md", "r") as f:
    readme = f.read()


setup(
    name="Jedutils",
    version=version,
    description="Jedutils is a Python utilities package that provides a collection of useful helper functions.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="AYMEN Mohammed",
    author_email="let.me.code.safe@gmail.com",
    url="https://github.com/AYMENJD/jedutils",
    license="MIT",
    project_urls={
        "Source": "https://github.com/AYMENJD/jedutils",
        "Tracker": "https://github.com/AYMENJD/jedutils/issues",
    },
    packages=find_packages(),
    extras_require={
        "all": ["redis", "aiohttp"],
    },
    keywords=[
        "utilities",
        "tools",
        "library",
        "helper",
        "functions",
        "development",
    ],
)
