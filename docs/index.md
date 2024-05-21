# MEORG-CLIENT

## Usage

### Authentication

Authentication with the ME.org service requires a valid registration. In particular, the email address and password used to log into the dashboard.

It is good practice to keep these details out of your scripts and set in environment variables as per the example below.

```python
import os
from meorg_client import Client
client = Client(
    email=os.getenv('MEORG_EMAIL'),
    password=os.getenv('MEORG_PASSWORD')
)
```

The `client` object will now be authenticated and can be used to perform the various implemented functions.

ME.org will invalidate any stale sessions after a time, however, to explicitly log out of the service, you can use the `logout` method on the client.

```python
# Log out of the service.
client.logout()
```