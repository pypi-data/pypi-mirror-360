import os
import setuptools

from datetime import datetime
from distutils.core import setup

import version


# Read the contents of README.md
this_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


version_nr = version.get()

setup(
    name="flyr",
    packages=["flyr", "flyr.palettes"],
    version=version_nr,
    license="EUPL v1.2",
    description="Flyr is a library for extracting thermal data from FLIR images written fully in Python, without depending on ExifTool.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Arthur Nieuwland",
    author_email="anieuwland@nimmerfort.eu",
    url="https://bitbucket.org/nimmerwoner/flyr/",
    project_urls={
        "Issues": "https://bitbucket.org/nimmerwoner/flyr/issues?status=new&status=open",
        "Releases": "https://bitbucket.org/nimmerwoner/flyr/downloads/",
        "Author website": "http://nimmerfort.eu",
    },
    download_url=f"https://bitbucket.org/nimmerwoner/flyr/downloads/flyr-{version_nr}.tar.gz",
    keywords=["flir", "thermography", "heat imagery"],
    install_requires=["numpy", "nptyping==0.3.1", "pillow"],
    python_requires=">=3.6",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    entry_points={"console_scripts": ["flyr=flyr.flyr:main"]},
)
