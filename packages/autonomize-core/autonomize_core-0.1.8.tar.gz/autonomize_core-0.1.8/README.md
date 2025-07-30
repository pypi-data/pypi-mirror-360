# Autonomize Core

![Python Version](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python)
![PyPI Version](https://img.shields.io/pypi/v/autonomize-core?style=for-the-badge&logo=pypi)
![Code Formatter](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)
![Code Linter](https://img.shields.io/badge/linting-pylint-green.svg?style=for-the-badge)
![Code Checker](https://img.shields.io/badge/mypy-checked-blue?style=for-the-badge)
![Code Coverage](https://img.shields.io/badge/coverage-100%25-a4a523?style=for-the-badge&logo=codecov)

## Overview

Autonomize Core houses the core functionality about authentication of our in-house platform.

## Features

- **Authentication**: The SDK allows you to authenticate tokens for Modelhub.
- **High scalability**: Built to handle large-scale data retrieval and generation, enabling robust, production-ready applications.

## Installation

1. Create a virtual environment, we recommend [Miniconda](https://docs.anaconda.com/miniconda/) for environment management:
    ```bash
    conda create -n autocore python=3.12
    conda activate autocore
    ```
2. Install the package:
    ```bash
    pip install autonomize-core
    ```

To install with optional dependencies like Qdrant, Huggingface, OpenAI, Modelhub, etc., refer to the [Installation Guide](INSTALL.md).


## Usage

### Sync Usage

```python
import os
from autonomize.core.credential import ModelhubCredential

cred = ModelhubCredential(
    modelhub_url=MODELHUB_URI,
    client_id=MODELHUB_AUTH_CLIENT_ID,
    client_secret=MODELHUB_AUTH_CLIENT_SECRET,
)

token = cred.get_token()
```

### Async Usage

Simply use sync methods with `a` prefix and use `await` for each call. Example: `cred.get_token()` becomes `await cred.aget_token()` and everything else remains the same.

```python
import os
from autonomize.core.credential import ModelhubCredential

cred = ModelhubCredential(
    modelhub_url=MODELHUB_URI,
    client_id=MODELHUB_AUTH_CLIENT_ID,
    client_secret=MODELHUB_AUTH_CLIENT_SECRET,
)

token = await cred.aget_token()
```

## Contribution

To contribute in our Autonomize Core SDK, please refer to our [Contribution Guidelines](CONTRIBUTING.md).

## License
Copyright (C) Autonomize AI - All Rights Reserved

The contents of this repository cannot be copied and/or distributed without the explicit permission from Autonomize.ai

# New preferred environment variables:
MODELHUB_URI=https://your-modelhub.com
MODELHUB_AUTH_CLIENT_ID=your_client_id
MODELHUB_AUTH_CLIENT_SECRET=your_secret
GENESIS_CLIENT_ID=your_genesis_client
GENESIS_COPILOT_ID=your_copilot

# Old environment variables (still work for backward compatibility):
MODELHUB_BASE_URL=https://your-modelhub.com
MODELHUB_CLIENT_ID=your_client_id
MODELHUB_CLIENT_SECRET=your_secret
CLIENT_ID=your_client
COPILOT_ID=your_copilot
