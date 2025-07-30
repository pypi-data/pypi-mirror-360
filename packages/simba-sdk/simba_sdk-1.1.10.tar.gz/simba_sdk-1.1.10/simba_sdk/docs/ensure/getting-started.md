The first thing to check is authorisation. If you can authorise via the members service, and set a Domain, your config is working and you should theoretically be able to interact with any of the APIs.
```python
from simba_sdk import EnsureClient

DOMAIN = "my_domain"

# initialise a new client
# your auth credentials will be picked up by the settings object under the hood
client = EnsureClient()

# The client has a few helper properties that get set the first time you authorise.
# You can authorise manually
await client.authorise()

# or call any of the endpoints to do so automatically.
await client.set_domain(DOMAIN)

# any problems with authorisation will raise an exception, but just to double-check nothing's failing silently,
# we can now check our user profile from within the client.
print(client.user)
```

The result should be a schema containing your profile, id, email etc. The information is obtained from the member service so it should be identical to a payload you get from the member service directly.


## Ensure Client

SIMBA Ensure's use-cases are *domain* scoped. This is a namespace that contains your organisation's trust profile, storage configuration, and VP schemas.

You also need to be able to make transactions on a blockchain (which SIMBA handles for you). If you do not already have an account setup with simba, you must use `EnsureClient.create_custodial_account` to create a custodial account.

This code snippet runs through a "cold start":

```python
from simba_sdk import EnsureClient
from simba_sdk.ensure.client import credential_schemas as cs

DOMAIN, BLOCKCHAIN = "my-domain", "my-blockchain"  # provided by your domain admin


async def setup() -> EnsureClient:
    client = EnsureClient()
    await client.set_domain(DOMAIN)
    try:
        account = await client.get_default_account()
    except:
        account = await client.create_custodial_account(
            cs.CreateAccountHttp(nickname="my-test-account", domain=DOMAIN)
        )
    await client.set_account(network=BLOCKCHAIN, alias=account.alias)

    return client


authenticated_client = await setup()
```

If you get an `EnsureClient` object returned successfully, then you should be ready to get started. Continue on to [Usage](ensure.md) to see how this client can be used to interact with the SIMBA Ensure product.

## Troubleshooting

The ensure client uses a simple exception structure that wraps around the request exceptions raised by the service clients. This means that there should be some plain description as to what's gone wrong, but also the response itself from the API if you need to do any further digging.
