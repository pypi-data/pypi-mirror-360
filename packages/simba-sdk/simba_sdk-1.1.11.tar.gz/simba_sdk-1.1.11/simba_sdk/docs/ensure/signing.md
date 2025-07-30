Interacting with the Ensure platform very often involves making transactions on a blockchain and signing messages.
While these can be handled with a Custodial Account managed by SIMBAChain It is also possible to use non-custodial Accounts.
Non-custodial Accounts are accounts that you yourself manage the public and private keys for.
The main difference between behaviours is that with a non-custodial Account, you will need to sign data yourself before they can be added to the chain.
We recommend you do this via the SDK's Signer class.

## Use cases
Generally any Smart Contract method call that is not a GET needs to be signed.
Below are the scenarios in which a non-custodial Account user will need to sign data:
- Updating/revoking a DID.
- Signing a VC proof.
- Revoking a VC.
- Signing a VP proof.

## Configuration
The Credential service will usually automatically sign transactions for you.

## Getting a transaction
A key example of a transaction is when updating a DID.
Here is the flow for updating a self-signing DID:
```python
import uuid
import time

from simba_sdk import EnsureClient
from simba_sdk.ensure.client import credential_schemas as cs
from simba_sdk.ensure.client import credential_queries as cq


signer = EthereumSigner(private_key="...") # Assuming you have your private key available for a non-custodial Ethereum account

client: EnsureClient = EnsureClient()

... # common setup: set_domain, set_account etc.

self_signing_issuer_did = cs.CreateDidHttp(
    trust_profile="...",
    account=cs.PubKeyAccountInfo(
        public_key=signer.public_key,
    ),
    permission=cs.DidPermission.ISSUER,
    alias="my_test_issuer_did",
    nickname="My Issuer DID",
    public_name=cs.PublicName(f"{client.user.profile.first_name}'s ISSUER DID"),
    seed = str(uuid.uuid4())
)

task_id = await(client.create_did(createdidhttp=self_signing_issuer_did))
```

This looks **very** similar to the [example](ensure.md#create-a-did) in our usage docs, and that's because it is! In fact the only thing you need to remember for creating self-signing DIDs is to omit the alias from the account structure in the input, in other words **only provide the public key**.
And of course, the public key you provide should be that of your non-custodial Account.
If the API receives a CreateDidHttp payload with no account alias it will remember in future not to sign transactions for that DID.

## Signing a DID update
Now that we have the `task_id` for our DID creation, we can get the status on the DID creation via `task = await client.credential_get_task(task_id)`. This should happen quite fast but keep polling the endpoint until `task.status` is `COMPLETED`.
Once it is completed, we can update the DID which is where we'll need to sign locally.

An example of a neat update we can use is adding an account to the DID:
```python
task_id = await client.update_did(
    did_id=my_did_id,
    updatedidhttp=cs.UpdateDidHttp(
        method_spec_updates=cs.MethodSpecUpdate(
            add_account=cs.AddAccount(
                address=my_other_account_address, # This can be a public key from a custodial or non-custodial account (Just not the one you used to create the did)
                transfer=False
            )
        )
    )
)
```

We can use the task ID to check if the update has been carried out but realistically the next step only requires that we know the DID ID. We use it to get any pending transactions for the DID, of which there'll be one, pertaining to the update we just made.
From this pending transaction object we can obtain the raw transaction which we'll use with our signer to sign before sending back to the API.

```python
pending = await client.get_pending_did_txn(did_id=did_id)
signed = signer.sign_transaction(pending)
await client.submit_signed_did_transaction(did_id=did_id, didsignedtxn=cs.DIDSignedTxn(signed_txn=signed))
```

All done! you can double check by getting the DID:

```python
did = await client.get_did(did_id=did_id)
print(did.added_accounts) # If the update and signing worked, this list will contain the public key you added.
```
