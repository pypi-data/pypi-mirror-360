import os

import setuptools
from setuptools import setup

CURR_DIR = os.path.abspath(os.path.dirname(__file__))


def readme():
    with open(os.path.join(CURR_DIR, "README.md"), "r", encoding="utf-8") as fh:
        return fh.read()


def getver():
    version = dict()
    with open(os.path.join(CURR_DIR, "src", "naludaq", "_version.py")) as fp:
        exec(fp.read(), version)
        return version["__version__"]


setup(
    name="naludaq",
    version=getver(),
    author="Marcus Luck",
    author_email="marcus@naluscientific.com",
    description="Backend package for Nalu hardware",
    python_requires=">=3.9",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="",
    install_requires=[
        "naluconfigs>=13.3.0",
        "ftd3xx>=1.0",
        "naludaq_rs>=0.1.10",
        "deprecation",
        "ftd2xx>=1.1.2",
        "h5py",
        "numpy<1.24",
        "pyserial==3.4",
        "pyyaml>=5.1.1",
        "scikit-learn==1.1.3",
        "requests",
    ],
    tests_require=[
        "pytest==5.0.1",
        "pytest-mock",
        "pytest-xdist",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
