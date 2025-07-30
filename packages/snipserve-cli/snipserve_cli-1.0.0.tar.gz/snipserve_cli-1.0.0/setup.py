# setup.py
from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

# Read version from __init__.py
def get_version():
    with open('snipserve_cli/__init__.py', 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return '0.1.0'

setup(
    name='snipserve-cli',
    version=get_version(),
    author='Spkal01',
    author_email='kalligeross@gmail.com',
    description='Command-line interface for SnipServe paste service',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/spkal01/snipserve-cli',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing',
        'Topic :: Utilities',
    ],
    python_requires='>=3.7',
    install_requires=[
        'click>=8.0.0',
        'requests>=2.25.0',
    ],
    entry_points={
        'console_scripts': [
            'snipserve=snipserve_cli.cli:cli',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/spkal01/snipserve-cli/issues',
        'Source': 'https://github.com/spkal01/snipserve-cli',
        'Documentation': 'https://github.com/spkal01/snipserve-cli#readme',
    },
)