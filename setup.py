#
# Copyright 2018-2019 Happineo
#
"""setuptools installer for zamita."""

import os
import uuid

from setuptools import find_packages
from setuptools import setup
from setuptools.command.build_py import build_py

# local imports
from build_scripts.version import VersionInfo

HERE = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(HERE, "README.md"), encoding="UTF-8").read()
NEWS = open(os.path.join(HERE, "NEWS.md"), encoding="UTF-8").read()
PROJECT_NAME = "ejabberd_external_auth_jwt"

VERSION = None
try:
    VERSION = VersionInfo().version
except Exception:
    pass

if VERSION is None or not VERSION:
    try:
        VERSION_FILE = open(f"{PROJECT_NAME}/RELEASE-VERSION", "r")
        try:
            VERSION = VERSION_FILE.readlines()[0]
            VERSION = VERSION.strip()
        except Exception:
            VERSION = "0.0.0"
        finally:
            VERSION_FILE.close()
    except IOError:
        VERSION = "0.0.0"


class CustomBuild(build_py):
    """custom build class."""

    def run(self):
        """Add target and write the release-VERSION file."""
        # honor the --dry-run flag
        if not self.dry_run:
            target_dirs = []
            target_dirs.append(os.path.join(self.build_lib, PROJECT_NAME))
            target_dirs.append(PROJECT_NAME)
            # mkpath is a distutils helper to create directories
            for _dir in target_dirs:
                self.mkpath(_dir)

            try:
                for _dir in target_dirs:
                    fobj = open(os.path.join(_dir, "RELEASE-VERSION"), "w")
                    fobj.write(VERSION)
                    fobj.close()
            except Exception:
                pass

        super().run()


with open("requirements.txt") as f:
    requirements = f.read().splitlines()

if requirements[0].startswith("-i"):
    requirements = requirements[1:]

setup(
    name=PROJECT_NAME,
    version=VERSION,
    description="ejabberd_external_auth_jwt",
    long_description=README + "\n\n" + NEWS,
    cmdclass={"build_py": CustomBuild},
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: Linux",
    ],
    keywords="",
    author="Thomas Chiroux",
    author_email="",
    url="https://www.github.com/ThomasChiroux/ejabberd_external_auth_jwt",
    license="LICENSE.txt",
    packages=find_packages(exclude=["ez_setup"]),
    package_data={"": ["*.rst", "*.md", "*.yaml", "*.cfg"]},
    include_package_data=True,
    zip_safe=False,
    test_suite="pytest",
    tests_require=[],
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ejabberd_external_auth_jwt=ejabberd_external_auth_jwt.main:main_sync"
        ]
    },
)
