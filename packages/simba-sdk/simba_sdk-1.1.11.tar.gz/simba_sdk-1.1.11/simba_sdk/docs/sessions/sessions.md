The `XSession` class is an asynchronous context manager through which you can interact with the entity `X`. Some Sessions can generate new child Sessions, leading to a nested structure, with increasingly specific scope.
For instance, the `UserSession` is probably the most general layer, as most everything you do within a session will be via your user profile in some way. However, the`UserSession` can provide a `DomainSession` which narrows the scope to a specific `Domain` and so on and so forth.
Each `Session` contains various methods for interacting with a particular scope of the Ensure framework, as well as a dataclass containing metadata for that scope (often a one-to-one relationship with a database entity on an API).
The `XSession` and `X` classes can both most likely be found in a file `x.py` (e.g. `user.py` contains the `User` dataclass and `UserSession` context manager.)

## Dataclasses
As previously stated these classes contain metadata for reference and convenience while interacting with the corresponding entity on the Ensure system. As dataclasses they are effectively free of any logic, and can be used interchangeably with dictionaries.
The most common way to construct one is as follows:
```python
from simba_sdk.sessions.base import Base

new_entity = Base.from_dict(
    field=value
)
```

You will also commonly see the `from_dict` method, this allows you to initialise a dataclass from kwargs without raising exceptions from any unexpected arguments.

```python
new_entity = Base.from_dict(
    {
        "field":"value"
        "not a field": "irrelevant value" # Will still initialise and this field will be discarded.
    }
)
```

Where possible we try to keep the fields of these dataclasses to primitive types, although where it seems more convenient we have some dataclasses with fields that are also dataclasses.

## Sessions
The Session class itself is primarily used within an `async with` block. You can instantiate one directly or retrieve one from another related session. The Session classes rely on a `Settings` object that contains relevant config. If this is not passed to your `Session` it will be created for you from .env files and/or env vars.
```python
from simba_sdk.config import Settings
from simba_sdk.sessions.user import UserSession
from simba_sdk.sessions.domain import DomainSession

settings = Settings(client_id=..., client_secret=...)
async with UserSession(settings=settings) as user_session:
    print(user_session.user)
    domain_session = await user_session.set_domain("my-domain") # The DomainSession will inherit its Settings from the UserSession
    async with domain_session:
        print(domain_session.domain)
async with DomainSession(name="my-domain", settings=settings) as domain_session:
    print(domain_session.domain)
```

You can create entities on an API from a dataclass you've instantiated, via the given method. These methods can either take a pre-existing dataclass instance, or the fields to instantiate one for you:
```python
from sessions.did import DIDSession
from sessions.vc import VC
vc_fields = {...}
vc = VC(
    **vc_fields
)
async with DIDSession(...) as did_session:
    await did_session.create_vc(vc=vc)
    # and
    await did_session.create_vc(**vc_fields)
    # are functionally identical
```

## E2E Example

Below is a generic example of a common use case within the Ensure framework: accessing and downloading a resource.
```python
from simba_sdk.sessions.user import UserSession

async def main():
    async with (UserSession(client_id=...,
                            client_secret=...) as user_session):
        domain_session = await user_session.set_domain(..., account=UUID(...))
        async with domain_session:
            did_session = await domain_session.create_did(trust_profile=..., permission=..., seed=..., alias=..., nickname=..., public_name=...)
            holder_session = await domain_session.create_did(trust_profile=..., permission=..., seed=..., alias=..., nickname=..., public_name=...)
            async with holder_session:
                holder_did = holder_session.did.did
            async with did_session:
                print(did_session.did)
                registry_session = await domain_session.get_schema_registry()
                async with registry_session:
                    print(registry_session.registry)
                    if len(registry_session.registry.values()) == 0:
                        await registry_session.create_schema(name=..., attributes=[...])
                    schema = list(registry_session.registry.values())[0]
                vc = VC.from_dict(
                    {
                        "tags"...,
                        "context"...,
                        "issuer"...,
                        "valid_from"...,
                        "valid_until"...,
                        "material"...,
                        "subject"...,
                        "claims": {
                            ...
                        }
                    }
                )
                vc_session = await did_session.create_vc(vc)
                async with vc_session:
                    print(vc_session.vc)
                    await vc_session.verify_vc()
                    await vc_session.accept_vc()
                    vp = VP.from_dict(
                        {
                            "vc_id"...,
                            "proof":
                                {...},
                            "material": {
                                ...
                            }
                        }
                    )
                    vp_session = await vc_session.create_vp(vp=vp)
                    async with vp_session:
                        print(vp_session.vp)
                        await vp_session.verify_vp()
                        resource_session = await domain_session.create_resource(name=..., storage=..., tags=[...])
                        async with resource_session:
                            print(resource_session.resource)
                            sstream = BytesIO()
                            sstream.write("This is a test".encode("utf-8"))
                            await resource_session.upload(stream=sstream)
                            await resource_session.add_policy(identifier=..., criteria=[...])
                            await resource_session.publish(public_key=..., alias=domain_session.account.alias)
                            token = await vp_session.request_access(resource_id=resource_session.resource_id)
                            with open("test.tar.gz", "wb") as f:
                                await resource_session.download(token=token, out_stream=f)
```
