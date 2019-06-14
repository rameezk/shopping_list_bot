#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import sys
from shutil import rmtree

from setuptools import Command, find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

# Package meta-data.
NAME = "shopping list bot"
DESCRIPTION = "Automated shopping list creator."
URL = "https://github.com/mmphego/shopping_list_bot"
EMAIL = "mpho112@gmail.com"
AUTHOR = "Mpho Mphego"
REQUIRES_PYTHON = ">=3.6.0"
VERSION = "0.0.4"
REQUIRED = [
    "requests",
    "selenium",
    "beautifulsoup4",
    "oauth2client",
    "gspread",
    "coloredlogs",
]

try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION

SCRIPTS = []
for dirname, dirnames, filenames in os.walk("scripts"):
    for filename in filenames:
        SCRIPTS.append(os.path.join(dirname, filename))


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        try:
            import twine
        except ImportError:
            errmsg = "\n'Twine' is not installed.\n\nRun: \n\tpip install twine"
            self.status(errmsg)
            raise SystemExit(1)

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")

        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(about["__version__"]))
        os.system("git push --tags")

        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=REQUIRED,
    include_package_data=True,
    scripts=SCRIPTS,
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    project_urls={
        "Bug Reports": f"{URL}/issues",
        "Source": URL,
        "Say Thanks!": f"https://saythanks.io/to/mmphego",
        "AboutMe": "https://blog.mphomphego.co.za/aboutme",
    },
    # $ setup.py publish support.
    cmdclass={"upload": UploadCommand},
)
