from setuptools import setup, find_packages
from os.path import dirname, join
from pathlib import Path

here = dirname(__file__)

_VERSION = Path("VERSION").read_text().strip()

setup(
    name="cluster-agent",
    version=_VERSION,
    description="Cluster API data aggregator",
    long_description=open(join(here, "README.md")).read(),
    license="MIT",
    author="omnivector-solutions",
    author_email="info@omnivector.solutions",
    url="https://github.com/omnivector-solutions/cluster-agent/",
    download_url="https://github.com/omnivector-solutions/cluster-agent/dist/cluster-agent-"
    + _VERSION
    + "tar.gz",
    install_requires=list(map(lambda string: string.strip("\n"), open("requirements.txt", "r"))),
    extras_require={
        "dev": [
            "pytest~=6.2.4",
            "pytest-asyncio~=0.17.2",
            "asynctest~=0.13.0",
            "respx~=0.17.1",
            "black~=21.6b0",
            "flake8~=3.9.2",
            "uvicorn~=0.13.4",
        ]
    },
    packages=find_packages(),
    keywords=["armada", "hpc"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Other Audience",
        "Topic :: Software Development",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Utilities",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "agentconfig=cluster_agent.scripts.agentconfig:parameters",
            "agentrun=cluster_agent.scripts.agentrun:run",
        ]
    },
)
