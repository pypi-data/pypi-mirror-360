Cisco Catalyst WAN SDK 2.0
==========================

Welcome to the official documentation for the Cisco Catalyst WAN SDK, a package designed for creating simple and parallel automatic requests via the official SD-WAN Manager API.

Overview
--------

Cisco Catalyst WAN SDK serves as a multiple session handler (provider, provider as a tenant, tenant) and is environment-independent. You just need a connection to any SD-WAN Manager.

Supported Catalystwan WAN Server Versions
-----------------------------------------

- 20.15
- 20.16

Cisco Catalyst WAN SDK – Early Access Release
---------------------------------------------

We are excited to introduce the Cisco Catalyst WAN SDK in its early access release phase,
marking an important step in enabling developers to harness the full potential of Cisco's
networking solutions. This release provides a unique opportunity to explore and experiment
with the SDK's capabilities as we continue to refine and enhance its features.

As this version is part of an early development stage, it is provided "as is" and is still
undergoing active testing and iteration. While we are committed to supporting your experience
on a best-effort basis, we recommend exercising caution and conducting thorough testing before
deploying it in a production environment.

Your feedback during this phase is invaluable in shaping the SDK to meet the needs of our developer
community. Thank you for partnering with us on this journey to innovate and advance networking automation.

Supported Python Versions
-------------------------

Python >= 3.8

> If you don't have a specific version, you can just use [Pyenv](https://github.com/pyenv/pyenv) to manage Python versions.


Installation
------------

To install the SDK, run the following command:

```bash
pip install catalystwan==2.0.0a0
```

To manually install the necessary Python packages in editable mode, you can use the `pip install -e` command.

```bash
pip install -e ./packages/catalystwan-types \
            -e ./packages/catalystwan-core \
            -e ./versions/catalystwan-v20_15 \
            -e ./versions/catalystwan-v20_16
```


Getting Started
---------------

To execute SDK APIs, you need to create a `ApiClient`. Use the `create_client()` method to configure a session, perform authentication, and obtain a `ApiClient` instance in an operational state.

### Example Usage

Here's a quick example of how to use the SDK:

```python
from catalystwan.core import create_client

url = "example.com"
username = "admin"
password = "password123"

with create_client(url=url, username=username, password=password) as client:
    result = client.health.devices.get_devices_health()
    print(result)
```

If you need to preform more complex operations that require models, they can utilize an alias: `m`.
```python

with create_client(...) as client:
    result = client.admin.aaa.update_aaa_config(
        client.admin.aaa.m.Aaa(
            accounting: True,
            admin_auth_order: False,
            audit_disable: False,
            auth_fallback: False,
            auth_order: ["local"]
        )
    )
    print(result)
```

Using an alias allows for easier access and management of models, simplifying workflows and improving efficiency. This approach helps streamline operations without requiring direct integration with underlying models, making them more user-friendly and scalable.
