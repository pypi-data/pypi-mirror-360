# Introduction

Dash authorization using Microsoft Azure Active Directory and QDT Authentication framework.
This projects requires the authentication service running.

## Installation

Install the package using pip:

```bash
pip install scda_dash_auth
```

## Usage

To add authentication, add the following to your Dash app:

```python
from scda_dash_auth import SCDAAuth

auth = SCDAAuth(
    app,
    app_name = 'my-app',
    secret_key = 'some-secret-key-for-session',
    auth_url = 'http://0.0.0.0:8000',
)
```

This will add the authentication to your Dash app. The `auth_url` should point to the authentication service.
