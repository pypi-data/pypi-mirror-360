This page covers the most common use-cases for the SIMBA Ensure product:

[TOC]

Here we assume that the ensure client has been setup. If you missed this step, please follow the outline in [Ensure Client](getting-started.md#ensure-client).

## Create a DID
**Decentralised Identifiers** (DIDs) are an on chain way of representing a single entity (user, organisation etc.). A **HOLDER** DID can hold various credentials, which are issued to it by an **ISSUER** DID.

```python
import uuid
import time

from simba_sdk import EnsureClient
from simba_sdk.ensure.client import credential_schemas as cs
from simba_sdk.ensure.client import credential_queries as cq

client: EnsureClient = ...  # assuming common setup from above
list_profiles_query = cq.ListTrustProfilesQuery(page=1, size=5)
trust_profiles_response = await client.list_trust_profiles(list_profiles_query)
trust_profile = trust_profiles_response.items[0]

new_issuer_did = cs.CreateDidHttp(
    trust_profile=trust_profile.name,
    account=cs.PubKeyAccountInfo(
        public_key=client.account.public_key,
        alias=client.account.alias
    ),
    permission=cs.DidPermission.ISSUER,
    alias="my_test_issuer_did",
    nickname="My Issuer DID",
    public_name=cs.PublicName(f"{client.user.profile.first_name}'s ISSUER DID"),
    seed=str(uuid.uuid4())
)

task_id = await(client.create_did(createdidhttp=new_issuer_did))

# This creates a task to publish the DID, here we are using a while loop to poll the
# server until the task is complete.
task: cs.Task = await(client.credential_get_task(task_id))
while task.status != cs.TaskStatus.COMPLETED:
    await asyncio.sleep(1)
    task: cs.Task = await(client.credential_get_task(task_id))

# We can double-check as well
did: cs.DIDResponseModel = await client.get_did(did_id=task.object_id)
print(did)
```

N.B. The process is near identical for HOLDER dids, just change 'ISSUER' to 'HOLDER' in the input payload.

## Issue a VC
One DID can _issue_ a **Verifiable Credential**(VC) to another DID. This is essentially the issuer making a claim about the holder, i.e. that they hold a Bachelors Degree from the Issuer's University. VCs follow a pattern known as a schema which defines what attributes the claim is actually attributing to the Holder.

```python
from datetime import datetime, timedelta

from simba_sdk.ensure.client import credential_queries as cq
from simba_sdk.ensure.client import credential_schemas
from simba_sdk.ensure.client import EnsureClient

# See "Getting Started" and "Create a DID" for details on creating these
client: EnsureClient = ...
issuer_did: credential_schemas.DID = ...
holder_did: credential_schemas.DID = ...

my_schemas = await client.get_schema_registry()
my_schema = list(my_schemas.schemas.values())[0]

# vc
my_new_vc = credential_schemas.CreateVCHttp(
    issuer=issuer_did.did_document["id"],
    subject=holder_did.did_document["id"],
    valid_from=datetime.now() - timedelta(days=1),  # yesterday
    valid_until=datetime.now() + timedelta(days=365),  # this time next year
    material={"circom_circuit": "SMTInclusionSingleClaim"},
    # this is how the claims will be verified against the holder on chain
    claims={
        # The schema comes back in the form link#schema_name. Using this information we are dynamically constructing a valid claim
        my_schema.id[:my_schema.id.find("#")]: {
            my_schema.name: {  # this is schema_name
                # a reliable way to make a verifiable claim.
                my_schema.attributes[0].name: my_schema.attributes[0].suggestedValues[0],
            }
        }
    },
    tags=["sdk", "test", "ensure"]

)

# assuming this is an asynchronous function, we can use await instead of asyncio.run()
vc_id = await client.create_vc(createvchttp=my_new_vc)

vc = await client.get_vc(vc_id=vc_id)

# Verify the VC
result = await client.verify_vc(body=vc.model_dump_json())
if not result.success:
    raise Exception("The VC is invalid for some reason.")

await client.accept_vc(vc_id=vc_id,
                       query_arguments=cq.AcceptVcQuery(accept=True))  # the Holder needs to accept the credentials
```

## Publish a resource
The resource service provides a use case for DIDs with VCs. To gain access to resources, represented by **Bundles**, an entity can use a VP. You can use the SDK to create a bundle, populate it with files, and publish it to make it visible and accessible.

```python
import time

from simba_sdk.ensure.client import resource_schemas, resource_queries
from simba_sdk.ensure.client import EnsureClient
from simba_sdk.ensure.client import credential_schemas as cs

client: EnsureClient = ...

storages = await client.get_storages(query_arguments=resource_queries.GetStoragesQuery(page=1, size=100))

# whatever storage you want
storage = storages.items[0]

my_new_bundle = resource_schemas.CreateResourceBundleRequest(
    name="mybundle",
    storage_name=storage.name,
    tags=["test", "ensure", "sdk"],
)
bundle = await client.create_bundle(createresourcebundlerequest=my_new_bundle)

upload = await client.upload_files(uid=bundle.id, file_url="./my_secure_bundle_data.zip")

# Same as the DID, we need to wait for this task to complete before we publish
upload_task = await client.resource_get_task(uid=bundle.id, task_id=upload.id)

while upload_task.status != cs.TaskStatus.COMPLETED:
    await asyncio.sleep(1)
    upload_task = await client.resource_get_task(uid=bundle.id, task_id=upload_task.id)

# The bundle contains your data
publicationrequest = resource_schemas.PublicationRequest(
    action=resource_schemas.Action.publish,
    account=client.account.model_dump()
)
publish = await client.publish_action(uid=bundle.id, publicationrequest=publicationrequest)

publish_task = await client.resource_get_task(uid=bundle.id, task_id=publish.id)

while publish_task.status != cs.TaskStatus.COMPLETED:
    await asyncio.sleep(1)
    publish_task = await client.resource_get_task(uid=bundle.id, task_id=publish.id)

# The bundle is now visible and accessible on the chain. Entities can request access to it now.
# If we want to control access we must add access policies to be tested against Holder VCs.
my_schema: cs.CredentialSchema = ...
new_policy = resource_schemas.Policy(
    identifier=my_schema.attributes[0].hash,  # the schema we used to define our VC
    junction=resource_schemas.Junction.AND,
    dataType=resource_schemas.DataType.STR,
    criteria=[
        {
            "op": resource_schemas.Op.EQ,
            "value": my_schema.attributes[0].suggestedValues[0],
            # this should be whatever value you want to restrict access by
        }
    ]

)
policy = await client.add_policy(uid=bundle.id, policy=new_policy)
```


## Create a VP
A **Verifiable Presentation** (VP) is a secure presentation of a VC. It allows entities to verify an entity holds a VC without exposing knowledge about the entity or the VC.

```python
import json
import datetime

from simba_sdk.ensure.client import credential_schemas
from simba_sdk.ensure.client import EnsureClient

client: EnsureClient = ...
my_trust_profile: credential_schemas.TrustProfile = ...

ADDRESS_FOR_YOUR_CREDENTIAL_DOMAIN = my_trust_profile.config.registrar_address

vc_id: str = ...  # result from client.create_vc above

my_new_vp = credential_schemas.CreateVPHttp(
    vc_id=vc_id,
    proof_type="SMTInclusionProof",
    material={
        "challenge": "0x18",
        "domain": f"{ADDRESS_FOR_YOUR_CREDENTIAL_DOMAIN}",
        "presentation_time": int(datetime.timestamp(datetime.now()))
    }
)

vp_id = await client.create_vp(createvphttp=my_new_vp)

vp = await client.get_vp(vp_id=vp_id)

result = await client.verify_vp(body=json.dumps(vp.vp))
```

## Request access

As the holder of a DID with VCs, you can use VPs of that VC to request access to bundles. The claims you hold within your VC will be matched against policies for that bundle. If you holdthe required attributes, you can access that bundle.

```python
import time
import json
from simba_sdk.ensure.client import credential_schemas as cs

vp = ...  # VP from "Create a VP"
bundle = ...  # bundle from "Publish a resource"

vp_data = vp.model_dump_json()
vp_data = json.loads(vp_data)["vp"]
vp_data = json.dumps(vp_data)  # we need to do this to deserialise the VP properly

resource_token = await client.request_access(resource_id=bundle.resource_id, body=vp_data)

await asyncio.sleep(10)  # wait for the token to become valid
with open("./test_download.tar.gz",
          "wb") as f:  # the resource service will tarball your data for you to send over a connection
    await client.get_access(output_stream=f,
                            token=resource_token.value)  # this function takes any writable IO stream, not just files!
```
