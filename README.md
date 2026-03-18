<!-- SPDX-FileCopyrightText: 2021-2026 Ethan Henderson -->
<!-- SPDX-License-Identifier: BSD-3-Clause -->

<div align="center">
<img alt="analytix logo" src="https://raw.githubusercontent.com/parafoxia/analytix/main/assets/logo.png" width="400px">
<br /><br />
A simple yet powerful SDK for the YouTube Analytics API.
<br /><br />
<a href="https://pypi.python.org/pypi/analytix"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/analytix"></a>
<a href="https://pypi.python.org/pypi/analytix"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/analytix"></a>
<a href="https://pypi.python.org/pypi/analytix"><img alt="PyPI - Implementation" src="https://img.shields.io/pypi/implementation/analytix"></a>
<hr />
</div>

## Features

* Pythonic syntax lets you feel right at home
* Dynamic error handling saves hours of troubleshooting and makes sure only valid requests count toward your API quota
* A clever interface allows you to make multiple requests across multiple sessions without reauthorising
* Extra support enables you to export reports in a variety of filetypes and to a number of DataFrame formats
* Easy enough for beginners, but powerful enough for advanced users

## Installation

### Installing analytix

To install the latest stable version of analytix, use the following command:

```sh
pip install analytix
```

You can also install the latest development version using the following command:

```sh
pip install git+https://github.com/parafoxia/analytix
```

You may need to prefix these commands with a call to the Python interpreter depending on your OS and Python configuration.

## OAuth authentication

All requests to the YouTube Analytics API need to be authorised through OAuth 2.
In order to do this, you will need a Google Developers project with the YouTube Analytics API enabled.
You can find instructions on how to do that in the [API setup guide](https://parafoxia.github.io/analytix/starting/googleapp/).

Once a project is set up, analytix handles authorisation — including token refreshing — for you.

More details regarding how and when refresh tokens expire can be found on the [Google Identity documentation](https://developers.google.com/identity/protocols/oauth2#expiration).

## Usage

This is an alpha version, and is subject to change.

## Compatibility

Python 3.11 or above is required.
The CPython and PyPy implementations are both officially supported.
Windows, MacOS, and Linux are all supported.

Support for other configurations or functionality requiring optional libraries cannot be guaranteed.

## Contributing

Contributions are very much welcome! Have a look at the [contributing guide](https://github.com/parafoxia/analytix/blob/main/CONTRIBUTING.md) to get started.

## License

This project is licensed under the [BSD 3-Clause "New" or "Revised" License](https://github.com/parafoxia/analytix/blob/main/LICENSES/BSD-3-Clause.txt).
