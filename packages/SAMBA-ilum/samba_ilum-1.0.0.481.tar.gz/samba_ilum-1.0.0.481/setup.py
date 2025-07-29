from distutils.core import setup
from setuptools import setup, find_packages
from pathlib import Path
from typing import Optional
import json

setup(
    name = "SAMBA_ilum",
    version = "1.0.0.481",
    entry_points={'console_scripts': ['samba_ilum = samba_ilum:main']},
    description = "...",
    author = "Augusto de Lelis Araujo", 
    author_email = "augusto-lelis@outlook.com",
    license = "Closed source",
    install_requires=['matplotlib',
                      'pymatgen',
                      'pyfiglet',
                      'requests',
                      'plotly',
                      'scipy',
                      'numpy',
                      'uuid',
                      'vasprocar'],
    package_data={"": ['*.dat', '*.png', '*.jpg', '*']},
)

# python3 -m pip install --upgrade twine
# python setup.py sdist
# python -m twine upload dist/*