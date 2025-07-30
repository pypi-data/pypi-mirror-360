from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent

setup(
    name="toolforge-weld",
    version="1.6.11",
    author="Taavi Väänänen",
    author_email="hi@taavi.wtf",
    license="AGPL-3.0-or-later",
    packages=find_packages(),
    package_data={"toolforge_weld": ["py.typed"]},
    description="Shared Python code for Toolforge infrastructure components",
    long_description=(this_directory / "README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=[
        "python-dateutil",
        "PyYAML",
        "requests",
        "pyOpenSSL",
        "click>=8.0.3,<9.0.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Typing :: Typed",
    ],
    python_requires=">=3.9",
)
