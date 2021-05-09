import sys

if sys.version_info < (3, 6, 0):
    print(
        "analytix only supports Python versions 3.6.0 or greater.",
        file=sys.stderr,
    )
    sys.exit(1)

import setuptools

with open("analytix/__init__.py", mode="r", encoding="utf-8") as f:
    # I didn't choose this life, okay?
    productname, version, description, url, docs, author, license_ = [
        l.split('"')[1] for l in f.readlines()[:7]
    ]

with open("./README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name=productname,
    version=version,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=url,
    author=author,
    license=license_,
    classifiers=[
        "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",
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
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        # "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
    ],
    project_urls={
        "Documentation": docs,
        "Source": url,
    },
    install_requires=[
        "google-api-python-client<3,>=1.12.2",
        "google-auth-oauthlib<1",
    ],
    # Previous versions might be okay
    extras_require={
        "contrib": [
            "black>=21",
            "mypy>=0.812",
            "pandas<2,>=1.2",
            "sphinx<4,>=3.5",
            "sphinx-rtd-dark-mode<2,>=1.1.1",
            "sphinx-rtd-theme<1,>=0.5",
        ]
    },
    python_requires=">=3.6.0",
    packages=setuptools.find_packages(exclude=["tests*"]),
)
