from setuptools import setup, find_packages
from os.path import dirname
from pathlib import Path

here = dirname(__file__)

_VERSION = Path('VERSION').read_text().strip()

setup(
    name='armada-agent',
    version=_VERSION,
    description="Armada data aggregator",
    # long_description=open(join(here, 'README.md')).read(),
    license='MIT',
    author='omnivector-solutions',
    author_email='info@omnivector.solutions',
    url='https://github.com/omnivector-solutions/armada-agent/',
    download_url='https://github.com/omnivector-solutions/armada-agent/dist/armada-agent-' + \
        _VERSION + 'tar.gz',
    install_requires=list(map(
        lambda string: string.strip("\n"),
        open("requirements.txt", "r")
    )),
    packages=find_packages(),
    keywords=['armada', 'hpc'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Other Audience',
        'Topic :: Software Development',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Utilities',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
    ],
    entry_points={
        "console_scripts": [
            "agentconfig=armada_agent.scripts.agentconfig:parameters",
            "agentrun=armada_agent.scripts.agentrun:run"
        ]
    }
)
