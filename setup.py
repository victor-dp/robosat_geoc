"""
RoboSat.pink
----------
Semantic Segmentation ecosystem for GeoSpatial Imagery

<http://www.robosat.pink>
"""

from setuptools import setup, find_packages
from pkg_resources import get_distribution
from os import path

here = path.dirname(__file__)

with open(path.join(here, "VERSION")) as f:
    version = f.read()

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


with open(path.join(here, "requirements.txt")) as f:
    install_requires = f.read().splitlines()

setup(
    name="RoboSat.pink",
    version=version,
    url="https://github.com/datapink/robosat.pink",
    download_url="https://github.com/datapink/robosat.pink/releases",
    license="MIT",
    maintainer="DataPink",
    maintainer_email="robosat@datapink.com",
    description="Semantic Segmentation ecosystem for GeoSpatial Imagery",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests"]),
    install_requires=install_requires,
    entry_points={"console_scripts": ["rsp = robosat_pink.tools.__main__:main"]},
    include_package_data=True,
    python_requires='~=3.6',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
)
