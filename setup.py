from setuptools import setup, find_packages
from os.path import dirname, join

here = dirname(__file__)

_VERSION = "2.1.0-rc.1"

setup(
    name="ovs-cluster-agent",
    version=_VERSION,
    description="Cluster API data aggregator",
    long_description=open(join(here, "README.md")).read(),
    long_description_content_type="text/markdown",
    license="MIT",
    author="omnivector-solutions",
    author_email="info@omnivector.solutions",
    url="https://github.com/omnivector-solutions/ovs-cluster-agent/",
    download_url="https://github.com/omnivector-solutions/ovs-cluster-agent/dist/cluster-agent-"
    + _VERSION
    + "tar.gz",
    install_requires=list(map(lambda string: string.strip("\n"), open("requirements.txt", "r"))),
    extras_require=dict(dev=[
        "pytest==7.1.0",
        "pytest-mock==3.7.0",
        "respx==0.19.2",
        "asynctest==0.13.0",
        "pytest-asyncio==0.18.2",
        "black==22.3.0",
        "flake8==4.0.1",
        "pytest-env==0.6.2",
        "pytest-random-order==1.0.4",
        "pytest-cov==3.0.0",
        "freezegun==1.2.2",

    ]),
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
            "agentrun=cluster_agent.main:main",
        ]
    },
)
