# edwh-server-provisioning-plugin

[![PyPI - Version](https://img.shields.io/pypi/v/edwh-server-provisioning-plugin.svg)](https://pypi.org/project/edwh-server-provisioning-plugin)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/edwh-server-provisioning-plugin.svg)](https://pypi.org/project/edwh-server-provisioning-plugin)

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)
- [Changelog](#changelog)

## Installation

```console
pip install edwh-server-provisioning-plugin
```

But probably you want to install the whole edwh package:

```console
pipx install edwh[server-provisioning]
# or
pipx install edwh[plugins,omgeving]
```

## Usage

When the `edwh` package is installed, this package lives under the 'remote' namespace. Example:

```console
edwh -H user@some-host.tld remote.connect-postgres
```

## License

`edwh-bundler-plugin` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Changelog

[See CHANGELOG.md](CHANGELOG.md)