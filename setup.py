from importlib.metadata import entry_points
from setuptools import setup, find_packages


setup(
    name="mdsl",
    version="0.0.1",
    packages=find_packages(),
    scripts=['marvin/bin/mdsl']
)