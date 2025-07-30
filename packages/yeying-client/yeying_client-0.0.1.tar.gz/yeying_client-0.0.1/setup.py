# -*- coding:utf-8 -*-
import os
from setuptools import find_packages
from setuptools import setup
from pathlib import Path
import pkg_resources

version = {}
with open(os.path.join("yeying/version.py")) as fp:
    exec(fp.read(), version)

with Path('requirements.txt').open() as f:
    requirements = [
        str(req) for req in
        pkg_resources.parse_requirements(f)
    ]


setup(
    name="yeying_client",
    version=version["__version__"],
    description="yeying python sdk",
    url="https://github.com/yeying-community/yeying-client-python",
    author="yeying-community",
    author_email="yeying.community@gmail.com",
    install_requires=requirements,
    packages=find_packages(),
    entry_points={"console_scripts": [
        "yeying_cmd=yeying.client.tool.cmd.__main__:main",  # noqa
    ]},
    python_requires='>=3.12',
)
