# AWS data.all SDK (dataall-sdk)

> An [AWS Professional Service](https://aws.amazon.com/professional-services/) open source initiative | aws-proserve-opensource@amazon.com

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
![Static Checking]()
[![Documentation Status]()


## Table of contents

- [Quick Start](#quick-start)
- [Read The Docs](#read-the-docs)
- [Getting Help](#getting-help)

## Quick Start

Installation command: `pip install dataall_sdk`

```py3
import dataall_sdk

# Profile w/ UserA (assuming UserA profile configured in ~/.dataall/config.yaml)
da_client = dataall.client(profile="UserA") 

list_org_response = da_client.list_organizations()
print(list_org_response)
```

## [Read The Docs](./docs/build/html/index.html)

- [**Tutorials**](./tutorials/)
  - Coming Soon
- [**API Reference**](./docs/build/html/api.html)
  - Coming Soon
- [**License**](../LICENSE)
- [**Contributing**](../CONTRIBUTING.md)


