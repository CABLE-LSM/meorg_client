# API Client for ModelEvaluation.org (ACME)

This is the repository for the Python client under development for interacting with the ME.org service.

## Example usage

```python
# import the library
from acme.client import Client

# Set some details
base_url = 'https://modelevaluation.org/api'
email = os.getenv('MEORG_EMAIL') # good practice
password = os.getenv('MEORG_PASSWORD') # good practice

# Instantiate the client and connect
client = Client(
    base_url=base_url,
    email=email,
    password=password
)

# ... interact with ME.org.
```

## COPYRIGHT 

&copy; 2023 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
SPDX-License-Identifier: Apache-2.0