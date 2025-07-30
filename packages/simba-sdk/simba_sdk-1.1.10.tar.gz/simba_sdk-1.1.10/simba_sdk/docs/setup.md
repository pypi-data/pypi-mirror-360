Install the latest version of the SDK via pip:
```
pip install simba-sdk
```
The SIMBA SDK Clients rely on a Pydantic Settings object that contains the various URLs etc. necessary to establish a connection with their respective API. To instantiate a Client, you will need the following variables, in your environment, in a .env file, or otherwise directly passed into the Settings object.

```.dotenv
CLIENT_ID=
CLIENT_SECRET=
TOKEN_URL=https://simba-sbx-members-service-validator.blocks.simbachain.com
BASE_URL=https://simba-dev-{}.blocks.simbachain.com
```

These are further described in `simba_sdk/config.py`

## Check your details

Here we'll validate your generated authentication credentials. This section assumes that you have the required config in your environment variables.

Write the following code either in a script or an interactive python shell that has the SIMBA SDK installed:
```python
from simba_sdk.sessions.user import UserSession

async with UserSession() as user_session:
    print(user_session)
```

You should get back a dataclass containing information about your user profile on the Members service. Continue on to [Sessions/Usage](sessions/sessions.md) to learn more about the Sessions classes and what you can do with them (recommended), or to [Ensure/Getting started](ensure/getting-started.md) for lower-level, more direct interactions with the SDK.
