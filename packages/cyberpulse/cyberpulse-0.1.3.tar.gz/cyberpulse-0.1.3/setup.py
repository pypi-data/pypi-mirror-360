# setup.py

import io
import os
from setuptools import setup, find_packages

# Read the version from src/cyberpulse/__init__.py
version = {}
here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'src', 'cyberpulse', '__init__.py'), encoding='utf-8') as f:
    for line in f:
        if line.startswith('__version__'):
            # e.g. __version__ = "0.1.0"
            version['__version__'] = line.split('=', 1)[1].strip().strip('"\'')
            break

setup(
    name='cyberpulse',
    version=version['__version__'],
    description='CLI to ingest vulnerability exports and generate remediation steps',
    author='Jason Wexler',
    url='https://github.com/yourusername/cyberpulse',  # update as needed
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    install_requires=[
        # this should mirror requirements.txt; we'll install via pip install -r later
    ],
    entry_points={
        'console_scripts': [
            'cyberpulse=cyberpulse.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
