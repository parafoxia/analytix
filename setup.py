import sys

if sys.version_info < (3, 7, 1):
    print("analytix requires Python version >= 3.7.1.", file=sys.stderr)
    sys.exit(1)

import setuptools

import analytix

with open("./README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name=analytix.__productname__,
    version=analytix.__version__,
    description=analytix.__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=analytix.__url__,
    author=analytix.__author__,
    license=analytix.__license__,
    classifiers=[
        # "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Utilities",
    ],
    project_urls={
        "Documentation": analytix.__docs__,
        "Source": analytix.__url__,
    },
    install_requires=[
        "google-api-python-client>=1.12.0",
        "google-auth-oauthlib>=0.4.2",
        "pandas>=1.2.0",
    ],
    # extras_require={},
    python_requires=">=3.7.1",
    packages=setuptools.find_packages(exclude=["tests*"]),
)
