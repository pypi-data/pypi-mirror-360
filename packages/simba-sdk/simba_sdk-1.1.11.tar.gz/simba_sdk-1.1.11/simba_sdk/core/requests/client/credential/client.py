from dataclasses import asdict
from typing import Any, Dict

import pydantic_core
from pydantic import BaseModel

from simba_sdk.core.requests.client.base import Client
from simba_sdk.core.requests.client.credential import queries as credential_queries
from simba_sdk.core.requests.client.credential import schemas as credential_schemas
from simba_sdk.core.requests.exception import EnsureException


class CredentialClient(Client):
    """
    This client is used as a context manager to interact with one of the SIMBAChain service APIs.
    e.g.
    ```
    my_dids: List[DidResponse] = await credential_client.dids_get_dids()
    ```
    Clients are generated with methods that have a 1:1 relationship with endpoints on the service's API. You can find the models from the api in ./schemas.py
    and query models in ./queries.py
    """

    async def whoamai(
        self,
    ) -> credential_schemas.User:
        """
        Shows how to get the currently logged-in user from the token
        """

        path_params: Dict[str, Any] = {}
        resp = await self.get("/admin/whoami/", params=path_params)

        try:
            resp_model = credential_schemas.User.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def admin_list_vcs(
        self,
        query_arguments: credential_queries.AdminListVcsQuery,
        domain_name: str,
    ) -> credential_schemas.PageVerifiableCredential:
        """
                ## LIST VCs

        Args:
        - `domain`: The Domain name.

        - `vc_filter`: Filtering parameters, encapsulated by the VCFilter.

          - Note: User-ID fields accept ObjectID or simba_id as input.

        Returns:
        - `Page[models.VC]`: A page of VC objects retrieved from the specified Domain.

        ### Filters:
        For a detailed description and usage examples of the `VCFilter` parameters, please refer to the
        `VCFilter` model defined in the OpenAPI schema section of this documentation.

        - `__ilike`: Used for case-insensitive pattern matching. For example, `alias__ilike` would be used to search for
        aliases that match a specified pattern, ignoring case.

        - `__in`: Used to filter data that matches any value in a provided list. For example, `tags__in` filters for records
        where the tags attribute matches any value in the given list.

          - **A comma separated list, no spaces and no quotes.**
        - `__lte`: "less than or equal to". For example, `created_at__lte` would filter for records created at or before a
        specified date.

        - `__gte`: "greater than or equal to". For example, `created_at__gte` would filter for records created at or after a
        specified date.

        - `__fields`: (List[str]) This filter allows searching on arbitrary field names using an `$or` clause.
        Enter the dot separated keys path and, if required, a $-delimited value.

          - `metadata__or_fields` allows searching any metadata field using `or`, for example,

            - Example1: `owner$u_19241a37-7ee0-4d4b-8487-825f5a984692, holder$u_19241a37-7ee0-4d4b-8487-825f5a984692`,

              where the specified `simba_id` user is the `issuer` or `credentialSubject` of a VC.

          - For the VC credential, this filter is used to match on claims. Enter the dot separated keys path and, if required, a $-delimited value.

            - Example1: `degree` will find VCs having claim attribute`vc.credentialSubject.degree`.

            - Example2: `degree.type, groupMembership.group` will find VCs having attribute `vc.credentialSubject.degree.type`
            or `vc.credentialSubject.groupMembership.group`.

            - Example3: `degree.name$Bachelor of Science Optometry` finds claims where
              `vc.credentialSubject.degree.name=="Bachelor of Science Optometry"`.

            - Example4: `degree.name$Bachelor of Science Optometry, groupMembership.group$maintenance` finds claims where

              `vc.credentialSubject.degree.name=="Bachelor of Science Optometry"` or `groupMembership.group=="maintenance"`.
        """

        # get rid of items where None
        query_params = {
            k: v for k, v in asdict(query_arguments).items() if v is not None
        }

        path_params: Dict[str, Any] = {
            "domain_name": domain_name,
        }
        resp = await self.get(
            f"/admin/domains/{domain_name}/vcs/", params=path_params | query_params
        )

        try:
            resp_model = credential_schemas.PageVerifiableCredential.model_validate(
                resp.json()
            )
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def admin_list_vps(
        self,
        query_arguments: credential_queries.AdminListVpsQuery,
        domain_name: str,
    ) -> credential_schemas.PageVerifiablePresentation:
        """
                ## LIST VPs

        Args:
        - `domain`: The Domain name.

        - `vp_filter`: Filtering parameters, encapsulated by the VPFilter.

          - Note: User-ID fields accept ObjectID or simba_id as input.

        Returns:
        - `Page[models.VP]`: A page of VP objects retrieved from the specified Domain.

        ### Filters:
        For a detailed description and usage examples of the `VCFilter` parameters, please refer to the
        `VCFilter` model defined in the OpenAPI schema section of this documentation.

        - `__ilike`: Used for case-insensitive pattern matching. For example, `alias__ilike` would be used to search for
        aliases that match a specified pattern, ignoring case.

        - `__in`: Used to filter data that matches any value in a provided list. For example, `tags__in` filters for records
        where the tags attribute matches any value in the given list.

        - `__lte`: "less than or equal to". For example, `created_at__lte` would filter for records created at or before a
        specified date.

        - `__gte`: "greater than or equal to". For example, `created_at__gte` would filter for records created at or after a
        specified date.
        """

        # get rid of items where None
        query_params = {
            k: v for k, v in asdict(query_arguments).items() if v is not None
        }

        path_params: Dict[str, Any] = {
            "domain_name": domain_name,
        }
        resp = await self.get(
            f"/admin/domains/{domain_name}/vps/", params=path_params | query_params
        )

        try:
            resp_model = credential_schemas.PageVerifiablePresentation.model_validate(
                resp.json()
            )
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def admin_list_tasks(
        self,
        query_arguments: credential_queries.AdminListTasksQuery,
        domain_name: str,
    ) -> credential_schemas.PageTask:
        """
                ## List Tasks created by this user.
        Args:
        - `task_filter`: Filtering parameters encapsulated by the `TaskFilter`

          - Note: User-ID fields accept ObjectID or simba_id as input.

        Returns:
        - `Page[Task]`: A page of Task objects that belong to the current user.

        Filters:
        - `id`: The ObjectId of a task.

        - `order_by`: a list of attributes on which to sort, for example  `created_at`

        - `__in`: Used to filter data that matches any value in a provided list. For example, `tags__in` filters for records
        where the tags attribute matches any value in the given list.

        - `__lte`: "less than or equal to". For example, `created_at__lte` would filter for records created at or before a
        specified date.

        - `__gte`: "greater than or equal to". For example, `created_at__gte` would filter for records created at or after a
        specified date.
        """

        # get rid of items where None
        query_params = {
            k: v for k, v in asdict(query_arguments).items() if v is not None
        }

        path_params: Dict[str, Any] = {
            "domain_name": domain_name,
        }
        resp = await self.get(
            f"/admin/domains/{domain_name}/tasks/", params=path_params | query_params
        )

        try:
            resp_model = credential_schemas.PageTask.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def get_domain_configuration(
        self,
        domain_name: str,
    ) -> credential_schemas.AdminDomain:
        """ """

        path_params: Dict[str, Any] = {
            "domain_name": domain_name,
        }
        resp = await self.get(
            f"/admin/configuration/domains/{domain_name}", params=path_params
        )

        try:
            resp_model = credential_schemas.AdminDomain.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def configure_domain(
        self,
        domain_name: str,
        domainconfigurationrequest: credential_schemas.DomainConfigurationRequest,
    ) -> credential_schemas.AdminDomain:
        """ """

        path_params: Dict[str, Any] = {
            "domain_name": domain_name,
        }
        resp = await self.put(
            f"/admin/configuration/domains/{domain_name}",
            data=str(domainconfigurationrequest)
            if not issubclass(type(domainconfigurationrequest), BaseModel)
            else domainconfigurationrequest.model_dump_json(),  # type: ignore
            params=path_params,
        )

        try:
            resp_model = credential_schemas.AdminDomain.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def admin_create_did(
        self,
        domain_name: str,
        admincreatedidhttp: credential_schemas.AdminCreateDidHttp,
    ) -> str:
        """
                ## Create DID
        This Admin endpoint creates a `DID` for a specified user, the `target_owner`. See `DID` in the OpenAPI schema section of this
        documentation.

        Args:
        - `domain`: Domain name where the TrustProfile is to be created.

        - `did_http`: The input model `AdminCreateDidHttp`

        Returns:
        - `TaskId`: The MongoDB ObjectID of the newly created DID Task. Use `/admin/domains/{domain_name}/tasks/` to get the `task` since it will be owned by `target_owner`. <br><br>


        ### AdminCreateDIDHttp detail:
        - **target_owner**: The `simba_id` of the intended owner of this `DID`.

        - **trust_profile**: TrustProfile name, determines the type of DID created and controls subsequent DID operations on
        DIDS, VCs and VPs. Available types: SMB1-STD, SMB1-NFT
          - Example: `"SMB1-STD"`

        - **account**: PubKeyAccountInfo object containing `public_key`, `alias` and `org` (optional). `org` should be defined for an org scoped account.

          - The `alias` field, if omitted, will create a client-side-signing DID. if `alias` is defined, then a server-side-signing DID is created

          - Example of input for server-side-signing DID:
            ```
            {
              "public_key": "0xd4039eB67CBB36429Ad9DD30187B94f6A5122215",
              "alias": "george-wallet-alias"
            }
            ```

          - Example of input for client-side-signing DID:
            ```
            {
              "public_key": "0xd4039eB67CBB36429Ad9DD30187B94f6A5122215",
            }
            ```
            or
            ```
            {
              "public_key": "0xa508dD875f10C33C52a8abb20E16fc68E981F186",
              "public_key_multicodec": "zQ3shimdW4hBJNu19cyjVdYpzzAagjQB1eFZPofv22uSruHjZ"
            }
            ```

        - **permission**: Defines the DID's capabilities. An ISSUER DID can be used to create VCs. A HOLDER DID can be used as the credentialSubject in a VC.
          - Example: `"HOLDER" | "ISSUER"`

        - **alias**: Allows a user to own multiple DIDs within the same Domain. The _**alias**_ of a _**DID**_ owned by the logged in user.
          - Example: `"joe@bloggs.com" | "my-work-did"`

        - **nickname**:  Owner's familiar DID name. Must be case-insensitive unique for this user.
          - Example: `"Molly dog cert"`

        - **public_name**: The public name of the entity represented by this DID. Must be case-insensitive unique for this user.
          - Example: `"Certificate of Pedigree""`

        - **seed**: A user-defined seed to enhance DID uniqueness. Allows multiple DIDs per user+alias within this domain. Could be a document ID or part-number.
          - Example: `document_id | part-number`

        - **tags** (Optional): Keywords for easy searching or identification of the DID.
          - Example: `["dog", "cat"]`

        - **did_doc_creation_params**: Optional for GitHub DIDs and not required for creating an SMB1 DID with the STD
        registry, unless specifying a controller. Required for all other DID methods and registry smart contract combinations.
          - Note: A **controller** refers to an existing **DID.id** that authorizes changes to this new DID/DIDDocument.


        See examples below:
          - Examples:

            ### Optional GitHub did_doc_creation_params

            ```
            {
                "controller": "did:web:SIMBAChain.github.io:context:diddoc:5fb976f5697fe769a054f516377491c1eadd0f3e51bb58f26990035afa474465",
                "aka": "did is also known as",
                "key_name": "public key name to use. Default = #1"
            }
            ```

            ### Optional SMB1-STD did_doc_creation_params

            ```
            {
                "controller": "did:smb1:1337:0xfc98c982ca22ea0141c3452325c372ff728e9ccd:39517405560208510513658073967297468008711112795722749167466577185994559263742"
            }
            ```

            ### Required SMB1-NFT DID did_doc_creation_params
            ```
            {
                "collection": "0x2e3e124bc2Cc43Bc3A8FA8D87322057eD3bB4a5f",
                "token_id": 1234
            }
            ```

            ### Required SMB1-MSC Multi-sig  did_doc_creation_params

            ```
            {
                "signers": [
                    "0xd4039eB67CBB36429Ad9DD30187B94f6A5122215",
                    "0x7633Fe8542c2218B5A25777477F63D395aA5aFB4",
                    "0xd5cC383881D6d9A7dc1891A0235E11D03Cb992d3"
                ],
                "threshold": 2
            }
            ```

        ## Full payload examples
        Below are full payload examples. You must set the following fields (see above descriptions of the fields):

        - `"trust_profile":` ...

        - `"account.public_key":` ...

        - `"account.alias":` ...

        - `"alias":` ...

        - `"seed:` ...

            - Update or delete `tags`.

        ### Example GitHub DID
        ```
        {
          "trust_profile": "SIMBAWEB",
          "account": {
            "alias": "george-wallet-alias",
            "public_key": "0xd9dE3dC135f5264Ff159B662442dd8A589AC6040"
          },
          "permission": "ISSUER",
          "alias": "emloyee.123@simbachain.com",
          "nickname": "Me",
          "public_name": "Head HR Simbachain",
          "seed": "fwoipxcnmw",
          "tags": [
            "HR", "operations", "planning"
          ]
        }
        ```

        ### Example SMB1 Standard DID
        ```
        {
          "trust_profile": "SMB1-STD",
          "account": {
            "alias": "george-wallet-alias",
            "public_key": "0xd9dE3dC135f5264Ff159B662442dd8A589AC6040"
          },
          "permission": "ISSUER",
          "alias": "emloyee.123@simbachain.com",
          "nickname": "Me",
          "public_name": "Head HR Simbachain",
          "seed": "fwoipxcnmw",
          "tags": [
            "HR", "operations", "planning"
          ]
        }
        ```

        ### Example SMB1-NFT Standard DID
        ```
        {
          "trust_profile": "SMB1-NFT",
          "account": {
            "alias": "george-wallet-alias",
            "public_key": "0xd9dE3dC135f5264Ff159B662442dd8A589AC6040"
          },
          "permission": "HOLDER",
          "alias": "emloyee.123@simbachain.com",
          "nickname": "ops work",
          "public_name": "Operations Plan",
          "seed": "doc#678921456",
          "tags": [
            "Work", "operations", "planning"
          ]
          "did_doc_creation_params": {
            "collection": "0x2e3e124bc2Cc43Bc3A8FA8D87322057eD3bB4a5f",
            "token_id": 1234
          }
        }
        ```

        ### Example SMB1-MSC DID
        ```
        {
          "trust_profile": "SMB1-MSC",
          "account": {
            "alias": "george-wallet-alias",
            "public_key": "0xd9dE3dC135f5264Ff159B662442dd8A589AC6040"
          },
          "permission": "HOLDER",
          "alias": "emloyee.123@simbachain.com",
          "nickname": "ops work",
          "public_name": "Operations Plan",
          "seed": "doc#678921456",
          "tags": [
            "Work", "operations", "planning"
          ]
          "did_doc_creation_params": {
              "signers": [
                  "0xd4039eB67CBB36429Ad9DD30187B94f6A5122215",
                  "0x7633Fe8542c2218B5A25777477F63D395aA5aFB4",
                  "0xd5cC383881D6d9A7dc1891A0235E11D03Cb992d3"
              ],
              "threshold": 2
          }
        }
        ```
        """

        path_params: Dict[str, Any] = {
            "domain_name": domain_name,
        }
        resp = await self.post(
            f"/admin/domains/{domain_name}/dids/",
            data=str(admincreatedidhttp)
            if not issubclass(type(admincreatedidhttp), BaseModel)
            else admincreatedidhttp.model_dump_json(),  # type: ignore
            params=path_params,
        )

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def list_did_strings(
        self,
        query_arguments: credential_queries.ListDidStringsQuery,
    ) -> str:
        """
                ## List registered DID strings.
        This endpoint returns a list of DID-Strings from the DB. Only DIDs that are in a valid published state are returned.

        Args:
        - `diddoc_filter`: Filtering parameters, encapsulated by the DIDFilterUnscopedDIDs.

        Returns:
        - `Page[str]`: A page of DID-id strings.

        ### Filters:
        For a detailed description and usage examples of the `DIDFilterUnscopedDIDs` parameters, please refer to the
        `DIDFilterUnscopedDIDs` model defined in the OpenAPI schema section of this documentation.

        - `__like`: Used for case-sensitive pattern matching. For example, `id__like` would be used to search for
        dids having an `id` that matches a specified pattern.

        - `__startswith`: Matches to the start of a string field. For example, `id__startswith` could be used to search for
        a `did_document.id` that starts with the specified string pattern.
        """

        # get rid of items where None
        query_params = {
            k: v for k, v in asdict(query_arguments).items() if v is not None
        }

        path_params: Dict[str, Any] = {}
        resp = await self.get("/dids/", params=path_params | query_params)

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def get_did_document(
        self,
        query_arguments: credential_queries.GetDidDocumentQuery,
        did_id: str,
    ) -> credential_schemas.DIDDocument:
        """
                ## GET DID
        This endpoint retrieves a DID by DIDDocument.id.

        Args:
        - `did_id`: The `id` string of the DIDDocument (did_document.id).

        - `force_resolve`: When True, the resolver is used to look up from the public registry. False returns the DB cache
        of the DIDDocument.

        Returns:
        - A JSON-LD `DIDDocument`.

        Raises:
        - NotFoundException if the DID cannot be found.
        """

        # get rid of items where None
        query_params = {
            k: v for k, v in asdict(query_arguments).items() if v is not None
        }

        path_params: Dict[str, Any] = {
            "did_id": did_id,
        }
        resp = await self.get(f"/dids/{did_id}", params=path_params | query_params)

        try:
            resp_model = credential_schemas.DIDDocument.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def resolve_did(
        self,
        seed_hash: str,
    ) -> credential_schemas.DIDDocument:
        """
                This endpoint is called when one of our local cred service dids is resolved.

        For example, did:web:localhost:web:8d70849aa2d7fbe1474309b5c306608efee3ac8533ca5861a9866baad2aebf9b would be transformed
        into https://localhost/dids/web/8d70849aa2d7fbe1474309b5c306608efee3ac8533ca5861a9866baad2aebf9b/did.json
        which would call this endpoint.

        We want to transform it back into a DID and then look up in the db using the did_str

        Args:
        - seed_hash: value at the end of the did string e.g. 8d70849aa2d7fbe1474309b5c306608efee3ac8533ca5861a9866baad2aebf9b

        Returns:
        - A JSON-LD `DIDDocument`.
        """

        path_params: Dict[str, Any] = {
            "seed_hash": seed_hash,
        }
        resp = await self.get(f"/dids/web/{seed_hash}/did.json/", params=path_params)

        try:
            resp_model = credential_schemas.DIDDocument.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def list_custodial_accounts(
        self,
        query_arguments: credential_queries.ListCustodialAccountsQuery,
    ) -> credential_schemas.ListAccounts:
        """
                ## List SIMBA Blocks accounts owned by the logged-in is user.

        Args:
        - `domain`: Domain name to be used to list the accounts.

        - `trust_profile`: Optional TrustProfile name to be used to list the accounts.
          - Note: Domain name is required when specifying a TrustProfile name.


        Returns:
        - `models.ListAccounts`: A page of containing a list of accounts.
        """

        # get rid of items where None
        query_params = {
            k: v for k, v in asdict(query_arguments).items() if v is not None
        }

        path_params: Dict[str, Any] = {}
        resp = await self.get("/users/accounts/", params=path_params | query_params)

        try:
            resp_model = credential_schemas.ListAccounts.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def create_custodial_account(
        self,
        createaccounthttp: credential_schemas.CreateAccountHttp,
    ) -> credential_schemas.BlocksAccount:
        """
                ## Create a SIMBA Blocks account owned by the logged-in is user.
        The `domain` and optional `trust_profile` are used to identify the blockchain on which the account will be created.

        Args:
        - `domain`: Domain name to be used to look up the blockchain.

        - `trust_profile`: Optional TrustProfile name to be used to look up the blockchain..

        - `nickname`: A name for your new account.

        - `alias`: Optional, an alternate name by which this account will be known.

        - `org`: Optional. If set, an Org-account will be created.


        Example:

        ```
        {
          "domain": "dog_domain",
          "nickname": "Cred-Svc-Wallet"
          "alias": "george-wallet-alias",
        }
        ```

        Returns:
        - `models.BlocksAccount`: A blocks account object.
        """

        path_params: Dict[str, Any] = {}
        resp = await self.post(
            "/users/accounts/",
            data=str(createaccounthttp)
            if not issubclass(type(createaccounthttp), BaseModel)
            else createaccounthttp.model_dump_json(),  # type: ignore
            params=path_params,
        )

        try:
            resp_model = credential_schemas.BlocksAccount.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def get_public_vc(
        self,
        query_arguments: credential_queries.GetPublicVcQuery,
    ) -> None:
        """
                ## GET VC Document

        This will only work for public VCs since this is a public endpoint.

        Args:
        - `vc_id`: The ID of the VC e.g. VC.id

        Returns:
        - Either a `VC` document model or a `DigitalProductPassport` model, see the OpenAPI schema section of this
        documentation.
        """

        # get rid of items where None
        query_params = {
            k: v for k, v in asdict(query_arguments).items() if v is not None
        }

        path_params: Dict[str, Any] = {}
        await self.get("/vcs/", params=path_params | query_params)

        return

    async def list_trust_profiles(
        self,
        query_arguments: credential_queries.ListTrustProfilesQuery,
        domain_name: str,
    ) -> credential_schemas.PageTrustProfile:
        """
                ## List TrustProfiles
        This endpoint retrieves a list of TrustProfiles scoped by Domain.

        Args:
        - `domain`: The Domain name.

        - `trustprofile_filter`: Filtering parameters, encapsulated by the TrustProfileFilter.

        Returns:
        - `Page[models.TrustProfile]`: A page of TrustProfile objects defined for the specified Domain.

        ### Filters:
        For a detailed description and usage examples of the `TrustProfileFilter` parameters, please refer to the
        `TrustProfileFilter` model defined in the OpenAPI schema section of this documentation.


        - `__ilike`: Used for case-insensitive pattern matching. For example, `alias__ilike` would be used to search for
        aliases that match a specified pattern, ignoring case.

        - `__in`: Used to filter data that matches any value in a provided list. For example, `tags__in` filters for records
        where the tags attribute matches any value in the given list.

        - `__lte`: "less than or equal to". For example, `created_at__lte` would filter for records created at or before a
        specified date.

        - `__gte`: "greater than or equal to". For example, `created_at__gte` would filter for records created at or after a
        specified date.
        """

        # get rid of items where None
        query_params = {
            k: v for k, v in asdict(query_arguments).items() if v is not None
        }

        path_params: Dict[str, Any] = {
            "domain_name": domain_name,
        }
        resp = await self.get(
            f"/domains/{domain_name}/trustprofiles/", params=path_params | query_params
        )

        try:
            resp_model = credential_schemas.PageTrustProfile.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def create_trust_profile(
        self,
        domain_name: str,
        createtrustprofileinput: credential_schemas.CreateTrustProfileInput,
    ) -> str:
        """
                ## Create TrustProfile
        TrustProfiles are scoped by `Domain` and define the type of DID created and control subsequent operations on the
        DID/DIDDocument, VCs and VPs.

        Args:
        - `trustprofile_input`: Input model, see  `CreateTrustProfileInput` in the OpenAPI schema section of this
        documentation.

        - `domain`: Domain name where the TrustProfile is to be created.

        ## Example Configs
        Blockchain

            {
                "max_create_wait_time": 90,
                "interval_wait_time": 1,
                "config_type": "blockchain",
                "org": "trust",
                "app": "registry",
                "contract_api": "std-2025-4",
                "blockchain": "quorum-impartial-reindeer",
                "blockchain_type": "ethereum",
                "blockchain_subtype": "quorum",
                "registrar_address": "0xD2688B20ee5e0742c9419f262390Dbea4b60a728",
                "registrar_alias": "QuorumDevNewCopy-tsqaYmqp",
                "registry_type": "STDRegistry"
            },

        Web

            {
                "secondary_method": "local",
                "max_create_wait_time": 90,
                "interval_wait_time": 1,
                "config_type": "web"
            }

        Returns:
        - `DocumentId`: The MongoDB ObjectID of the newly created Document.
        """

        path_params: Dict[str, Any] = {
            "domain_name": domain_name,
        }
        resp = await self.post(
            f"/domains/{domain_name}/trustprofiles/",
            data=str(createtrustprofileinput)
            if not issubclass(type(createtrustprofileinput), BaseModel)
            else createtrustprofileinput.model_dump_json(),  # type: ignore
            params=path_params,
        )

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def get_trust_profile(
        self,
        trustprofile: str,
        domain_name: str,
    ) -> credential_schemas.TrustProfile:
        """
                ## GET TrustProfile
        This endpoint retrieves a named `TrustProfile` scoped by Domain.

        Args:
        - `trustprofile`: Name of the `TrustProfile` to retrieve.

        - `domain`: Name of the `Domain` where the TrustProfile is to be created.

        Returns:
        - A `TrustProfile`.
        """

        path_params: Dict[str, Any] = {
            "trustprofile": trustprofile,
            "domain_name": domain_name,
        }
        resp = await self.get(
            f"/domains/{domain_name}/trustprofiles/{trustprofile}", params=path_params
        )

        try:
            resp_model = credential_schemas.TrustProfile.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def update_trust_profile(
        self,
        trustprofile: str,
        domain_name: str,
        updatetrustprofileinput: credential_schemas.UpdateTrustProfileInput,
    ) -> str:
        """
                ## Update TrustProfile

        Args:
        - `domain`: Domain name where the TrustProfile is located.

        - `trustprofile`:  Name of the `TrustProfile` to be updated.

        - `trustprofile_input`: Input model, see  `UpdateTrustProfileInput` in the OpenAPI schema section of this
        documentation.

        Returns:
        - `DocumentId` The MongoDB ObjectID of the updated Document.
        """

        path_params: Dict[str, Any] = {
            "trustprofile": trustprofile,
            "domain_name": domain_name,
        }
        resp = await self.put(
            f"/domains/{domain_name}/trustprofiles/{trustprofile}",
            data=str(updatetrustprofileinput)
            if not issubclass(type(updatetrustprofileinput), BaseModel)
            else updatetrustprofileinput.model_dump_json(),  # type: ignore
            params=path_params,
        )

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def get_schema_registry(
        self,
        domain_name: str,
    ) -> credential_schemas.DomainRegistry:
        """
                Get the claim schema registry for a particular domain.

        Args:
        - `domain`: the name of the domain

        - `schema_reg`: injected dependency

        Returns: `DomainRegistry`
        """

        path_params: Dict[str, Any] = {
            "domain_name": domain_name,
        }
        resp = await self.get(f"/domains/{domain_name}/schemas/", params=path_params)

        try:
            resp_model = credential_schemas.DomainRegistry.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def create_schema(
        self,
        domain_name: str,
        createschemahttp: credential_schemas.CreateSchemaHttp,
    ) -> credential_schemas.Task:
        """
                Create a claim schema and publish it to the registry.

        Args:
        - `schema`: the payload

        - `domain`: the domain

        - `github_publisher`: injected GitHub Publisher

        - `path_handler`: injected GitHub Path handler

        Returns: `models.Task`

        Example payload:

        ```
        {
            "schema_name": "favouriteMusic",
            "schema_description": "Your favorite music.",
            "attributes": {
                "genre": {
                    "schema_type": "string",
                    "description": "Music genre",
                    "suggested_values": [
                        "Blues",
                        "Rock",
                        "Techno",
                        "Pop",
                        "Country",
                        "Hip Hop"
                    ]
                }
            }
        }
        ```
        """

        path_params: Dict[str, Any] = {
            "domain_name": domain_name,
        }
        resp = await self.post(
            f"/domains/{domain_name}/schemas/",
            data=str(createschemahttp)
            if not issubclass(type(createschemahttp), BaseModel)
            else createschemahttp.model_dump_json(),  # type: ignore
            params=path_params,
        )

        try:
            resp_model = credential_schemas.Task.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def delete_schema(
        self,
        schema_name: str,
        domain_name: str,
    ) -> credential_schemas.Task:
        """
                Delete a claim schema from the registry.

        Args:
        - `schema_name`: the name of the schema to delete

        - `domain`: the name of the domain the schema exists in

        - `github_publisher`: injected GitHub Publisher

        Returns: `models.Task`
        """

        path_params: Dict[str, Any] = {
            "schema_name": schema_name,
            "domain_name": domain_name,
        }
        resp = await self.delete(
            f"/domains/{domain_name}/schemas/{schema_name}", params=path_params
        )

        try:
            resp_model = credential_schemas.Task.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def list_dids(
        self,
        query_arguments: credential_queries.ListDidsQuery,
        domain_name: str,
    ) -> credential_schemas.PageDIDResponseModel:
        """
                ## List DIDs

        Args:
        - `request`: The request object.

        - `domain`: You can scope the request by domain.

        - `simba_id`: List the DIDs of a specific user. Can be used to see your own DIDs.

        - `output_format`: "SIMPLE" | "DETAILED".

        - `include_stats`: bool, True=show usage counts, False (default).

        - `diddoc_filter`: Filtering parameters, encapsulated by the DIDFilter.

        Returns:
        - `Page[models.DID]`: A page of DID objects that belong to the current user.

        ### Filters:
        For a detailed description and usage examples of the `DIDFilter` parameters, please refer to the `DIDFilter` model
        defined in the OpenAPI schema section of this documentation.

        - `__search`: Used for case-insensitive pattern matching on multiple fields using an `OR` clause. For `DID.metadata`
        the search fields are:

            - `["nickname", "public_name", "tags", "permission", "trust_profile"]`.

            - Note: Specifying `metadata__nickname__ilike` restricts the query to the owners DIDs only.


        - `__ilike`: Used for case-insensitive pattern matching. For example, `alias__ilike` would be used to search for
        aliases that match a specified pattern, ignoring case.

        - `__in`: Used to filter data that matches any value in a provided list. For example, `tags__in` filters for records
        where the tags attribute matches any value in the given list.

        - `__lte`: "less than or equal to". For example, `created_at__lte` would filter for records created at or before a
        specified date.

        - `__gte`: "greater than or equal to". For example, `created_at__gte` would filter for records created at or after a
        specified date.

        - `order_by`: a list of prefixed attributes on which to sort, for example  `metadata.created_at, metadata.name`
        """

        # get rid of items where None
        query_params = {
            k: v for k, v in asdict(query_arguments).items() if v is not None
        }

        path_params: Dict[str, Any] = {
            "domain_name": domain_name,
        }
        resp = await self.get(
            f"/domains/{domain_name}/dids/", params=path_params | query_params
        )

        try:
            resp_model = credential_schemas.PageDIDResponseModel.model_validate(
                resp.json()
            )
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def create_did(
        self,
        domain_name: str,
        createdidhttp: credential_schemas.CreateDidHttp,
    ) -> str:
        """
                ## Create DID
        This endpoint creates a `DID` for the logged-in user. See `DID` in the OpenAPI schema section of this
        documentation.

        Args:
        - `domain`: Domain name where the TrustProfile is to be created.

        - `did_http`: The input model `CreateDidHttp`

        Returns:
        - `TaskId`: The MongoDB ObjectID of the newly created DID Task.<br><br>


        ### CreateDIDHttp detail:
        - **trust_profile**: TrustProfile name, determines the type of DID created and controls subsequent DID operations on
        DIDS, VCs and VPs. Available types: SMB1-STD, SMB1-NFT
          - Example: `"SMB1-STD"`

        - **account**: PubKeyAccountInfo object containing `public_key`, `alias` and `org` (optional). `org` should be defined for an org scoped account.

          - The `alias` field, if omitted, will create a client-side-signing DID. if `alias` is defined, then a server-side-signing DID is created

          - Example of input for server-side-signing DID:
            ```
            {
              "public_key": "0xd4039eB67CBB36429Ad9DD30187B94f6A5122215",
              "alias": "george-wallet-alias"
            }
            ```

          - Example of input for client-side-signing DID:
            ```
            {
              "public_key": "0xd4039eB67CBB36429Ad9DD30187B94f6A5122215",
            }
            ```
            or
            ```
            {
              "public_key": "0xa508dD875f10C33C52a8abb20E16fc68E981F186",
              "public_key_multicodec": "zQ3shimdW4hBJNu19cyjVdYpzzAagjQB1eFZPofv22uSruHjZ"
            }
            ```

        - **permission**: Defines the DID's capabilities. An ISSUER DID can be used to create VCs. A HOLDER DID can be used as the credentialSubject in a VC.
          - Example: `"HOLDER" | "ISSUER"`

        - **alias**: Allows a user to own multiple DIDs within the same Domain. The _**alias**_ of a _**DID**_ owned by the logged in user.
          - Example: `"joe@bloggs.com" | "my-work-did"`

        - **name**: The name of the entity represented by this DID. Must be case-insensitive unique for this user.
          - Example: `"Certificate of Pedigree""`

        - **seed**: A user-defined seed to enhance DID uniqueness. Allows multiple DIDs per user+alias within this domain. Could be a document ID or part-number.
          - Example: `document_id | part-number`

        - **tags** (Optional): Keywords for easy searching or identification of the DID.
          - Example: `["dog", "cat"]`

        - **did_doc_creation_params**: Optional for GitHub DIDs and not required for creating an SMB1 DID with the STD
        registry, unless specifying a controller. Required for all other DID methods and registry smart contract combinations.
          - Note: A **controller** refers to an existing **DID.id** that authorizes changes to this new DID/DIDDocument.


        See examples below:
          - Examples:

            ### Optional GitHub did_doc_creation_params

            ```
            {
                "controller": "did:web:SIMBAChain.github.io:context:diddoc:5fb976f5697fe769a054f516377491c1eadd0f3e51bb58f26990035afa474465",
                "aka": "did is also known as",
                "key_name": "public key name to use. Default = #1"
            }
            ```

            ### Optional SMB1-STD did_doc_creation_params

            ```
            {
                "controller": "did:smb1:1337:0xfc98c982ca22ea0141c3452325c372ff728e9ccd:39517405560208510513658073967297468008711112795722749167466577185994559263742"
            }
            ```

            ### Required SMB1-NFT DID did_doc_creation_params
            ```
            {
                "collection": "0x2e3e124bc2Cc43Bc3A8FA8D87322057eD3bB4a5f",
                "token_id": 1234
            }
            ```

            ### Required SMB1-MSC Multi-sig  did_doc_creation_params

            ```
            {
                "signers": [
                    "0xd4039eB67CBB36429Ad9DD30187B94f6A5122215",
                    "0x7633Fe8542c2218B5A25777477F63D395aA5aFB4",
                    "0xd5cC383881D6d9A7dc1891A0235E11D03Cb992d3"
                ],
                "threshold": 2
            }
            ```

        ## Full payload examples
        Below are full payload examples. You must set the following fields (see above descriptions of the fields):

        - `"trust_profile":` ...

        - `"account.public_key":` ...

        - `"account.alias":` ...

        - `"alias":` ...

        - `"seed:` ...

            - Update or delete `tags`.

        ### Example GitHub DID
        ```
        {
          "trust_profile": "SIMBAWEB",
          "account": {
            "alias": "george-wallet-alias",
            "public_key": "0xd9dE3dC135f5264Ff159B662442dd8A589AC6040"
          },
          "permission": "ISSUER",
          "alias": "emloyee.123@simbachain.com",
          "name": "Head HR Simbachain",
          "seed": "fwoipxcnmw",
          "tags": [
            "HR", "operations", "planning"
          ]
        }
        ```

        ### Example SMB1 Standard DID
        ```
        {
          "trust_profile": "SMB1-STD",
          "account": {
            "alias": "george-wallet-alias",
            "public_key": "0xd9dE3dC135f5264Ff159B662442dd8A589AC6040"
          },
          "permission": "ISSUER",
          "alias": "emloyee.123@simbachain.com",
          "name": "Head HR Simbachain",
          "seed": "fwoipxcnmw",
          "tags": [
            "HR", "operations", "planning"
          ]
        }
        ```

        ### Example SMB1-NFT Standard DID
        ```
        {
          "trust_profile": "SMB1-NFT",
          "account": {
            "alias": "george-wallet-alias",
            "public_key": "0xd9dE3dC135f5264Ff159B662442dd8A589AC6040"
          },
          "permission": "HOLDER",
          "alias": "emloyee.123@simbachain.com",
          "name": "Operations Plan",
          "seed": "doc#678921456",
          "tags": [
            "Work", "operations", "planning"
          ]
          "did_doc_creation_params": {
            "collection": "0x2e3e124bc2Cc43Bc3A8FA8D87322057eD3bB4a5f",
            "token_id": 1234
          }
        }
        ```

        ### Example SMB1-MSC DID
        ```
        {
          "trust_profile": "SMB1-MSC",
          "account": {
            "alias": "george-wallet-alias",
            "public_key": "0xd9dE3dC135f5264Ff159B662442dd8A589AC6040"
          },
          "permission": "HOLDER",
          "alias": "emloyee.123@simbachain.com",
          "nickname": "ops work",
          "public_name": "Operations Plan",
          "seed": "doc#678921456",
          "tags": [
            "Work", "operations", "planning"
          ]
          "did_doc_creation_params": {
              "signers": [
                  "0xd4039eB67CBB36429Ad9DD30187B94f6A5122215",
                  "0x7633Fe8542c2218B5A25777477F63D395aA5aFB4",
                  "0xd5cC383881D6d9A7dc1891A0235E11D03Cb992d3"
              ],
              "threshold": 2
          }
        }
        ```
        """

        path_params: Dict[str, Any] = {
            "domain_name": domain_name,
        }
        resp = await self.post(
            f"/domains/{domain_name}/dids/",
            data=str(createdidhttp)
            if not issubclass(type(createdidhttp), BaseModel)
            else createdidhttp.model_dump_json(),  # type: ignore
            params=path_params,
        )

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def get_did(
        self,
        did_id: str,
        domain_name: str,
    ) -> credential_schemas.DID:
        """
                ## GET DID

        Args:
        - `did_id`: The MongoDB ObjectID or the `id` string of the DIDDocument (did_document.id).

        - `domain`: Name of the `Domain` where the `DID` is located.

        Returns:
        - A `DID` model, see the OpenAPI schema section of this documentation.
        """

        path_params: Dict[str, Any] = {
            "did_id": did_id,
            "domain_name": domain_name,
        }
        resp = await self.get(
            f"/domains/{domain_name}/dids/{did_id}", params=path_params
        )

        try:
            resp_model = credential_schemas.DID.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def update_did(
        self,
        did_id: str,
        domain_name: str,
        updatedidmetadatafromuser: credential_schemas.UpdateDIDMetadataFromUser,
    ) -> str:
        """
                ## Update DID
        The owner of a DID is allowed to update the fields listed. If submitting a method_spec_updates object with did_http, then the pending_transaction must be retrieved from did.metadata.pending_transaction, signed, and then submitted to /{did_id}/submit_signed_txn/

        Args:
        - `domain`: Domain name where the TrustProfile is to be created.

        - `did_http`: The input model `UpdateDidHttp`

        Returns:
        - `DocumentId`: The MongoDB ObjectID of the newly created Document.<br><br>


        ### CreateDIDHttp detail:
        - **tags** (Optional): Keywords for easy searching or identification of the DID.
          - Example: `["dog", "cat"]`

        - **name**: The name of the entity represented by this DID. Must be case-insensitive unique for this user.
          - Example: `"Certificate of Pedigree""`

        ## Full payload example
        Below is a full payload example.

        ```
        {
          "metadata": {
            "tags": [
              "ping", "pong"
            ],
            "name": "Bat fun",
          }
        }
        ```
        """

        path_params: Dict[str, Any] = {
            "did_id": did_id,
            "domain_name": domain_name,
        }
        resp = await self.put(
            f"/domains/{domain_name}/dids/{did_id}/metadata/",
            data=str(updatedidmetadatafromuser)
            if not issubclass(type(updatedidmetadatafromuser), BaseModel)
            else updatedidmetadatafromuser.model_dump_json(),  # type: ignore
            params=path_params,
        )

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def revoke_did(
        self,
        did_id: str,
        domain_name: str,
    ) -> str:
        """
                ## revoke a DID

        The owner of a DID is allowed to update the fields listed. Not all DID methods are supported, but currently smb1 and web are supported. Only smb1 currently supports self-sign revocation. If this endpoint is hit with a self-sign DID, then the raw transaction can be obtained for signing at DID.metadata.pending_transaction

        Args:
        - `did_id`: ID of the DID to be revoked

        - `domain`: Domain the DID resides in

        Returns:
        - `ObjectID`: ID of the DID being revoked
        """

        path_params: Dict[str, Any] = {
            "did_id": did_id,
            "domain_name": domain_name,
        }
        resp = await self.delete(
            f"/domains/{domain_name}/dids/{did_id}/revoke/", params=path_params
        )

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def submit_signed_did_transaction(
        self,
        did_id: str,
        domain_name: str,
        didsignedtxn: credential_schemas.DIDSignedTxn,
    ) -> str:
        """
                ## Submit a signed DID transaction.

        Hit this endpoint with a signed transaction after a DID update was initiated with a self-signing DID.

        Args:
        - `did_id`: ID of the DID for which a signed transaction is being submitted

        - `domain`: Domain the DID resides in

        - `did_txn`: DIDSignedTxn object, which contains signed_txn and optional txn_id.

            - Example:
              ```
              {
                  "signed_txn": {
                      "raw_transaction": "0xf8a982010a808301c88c941e1a08635650ba7dbf50e288ec6fe1f0cdd589c880b8445128d9287418cfa4ac1e82b48a5dce5c0cfc726f871f0323675fd72884e4ca2ef01bd001119a4974372b9604ed760b5e07d3ec68470c64a8ac8d930c195123596d6d9279820a96a0447ea6baf2939f2715ed495a005943707e49f2dc2a5a7f1c9a0461f914b0332aa009cf2a53418be966d64b0f88b3c8d12c6c2e507e653d93a93ffe2b129eeacabc",
                      "hash": "0x74bbb09f644b525471fa01649c3fcfa9041e5666380cbed89b9ab19790f901a9",
                      "r": 30981047163814140783287298754053747282814365915322052127397526155826671137578,
                      "s": 4436845097583516932672107757708642469205335746548505565616760742112783944380,
                      "v": 2710,
                  },
              }
              ```

        Returns:
        - `ObjectID`: ID of the DID being revoked
        """

        path_params: Dict[str, Any] = {
            "did_id": did_id,
            "domain_name": domain_name,
        }
        resp = await self.put(
            f"/domains/{domain_name}/dids/{did_id}/pending-txn/submit-signed/",
            data=str(didsignedtxn)
            if not issubclass(type(didsignedtxn), BaseModel)
            else didsignedtxn.model_dump_json(),  # type: ignore
            params=path_params,
        )

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def get_pending_did_txn(
        self,
        did_id: str,
        domain_name: str,
    ) -> credential_schemas.PendingTxn:
        """
                ## Get a pending DID txn

        After update_did or revoke_did was called with a self-signing DID, you can retrieve the pending txn for signing here

        Args:
        - `did_id`: ID of the DID for which a signed transaction is being submitted

        Returns:
        - `PendingTxn`: PendingTxn object that contains txn_id and raw_txn. raw_txn is what gets signed and then submitted to complete the DID update txn

            - Example:

                ```
                {
                    "txn_id": "0ad500e8-c689-4b4e-8b74-d63e9b9d027b",
                    "raw_txn": {
                        "chainId": "1337",
                        "data": "0x7bf5a7b2000000000000000000000000000000000000000000000000000000000000006000000000000000000000000018636c2d650c9f7507da23d7aa5cb587424f4fe700000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000041736d62313a746573742d646f6d61696e2d313a63687269732e73696d706b696e4073696d6261636861696e2e636f6d3a4353696d6d6f2d706572663a766f6d777000000000000000000000000000000000000000000000000000000000000000",
                        "from": "0x879973f65187A6699db7034e784E45c3b324feCF",
                        "gas": "0x74c08",
                        "gasPrice": "0x0",
                        "nonce": "0x1be1",
                        "to": "0x1E1a08635650Ba7dbF50e288Ec6fE1f0CdD589c8",
                        "value": "0x0"
                    }
                }
                ```
        """

        path_params: Dict[str, Any] = {
            "did_id": did_id,
            "domain_name": domain_name,
        }
        resp = await self.get(
            f"/domains/{domain_name}/dids/{did_id}/pending-txn/", params=path_params
        )

        try:
            resp_model = credential_schemas.PendingTxn.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def delete_pending_did_txn(
        self,
        did_id: str,
        domain_name: str,
    ) -> str:
        """
                ## Delete a pending DID txn

        After update_did or revoke_did was called with a self-signing DID, you can clear that pending txn here. We use this endpoing because only one pending DID txn is allowed at any given time, so if the user wants to initiate a new txn, and cancel the previous txn, they would hit this endpoint.

        Args:
        - `did_id`: ID of the DID for which a signed transaction is being submitted

        Returns:
        - `ObjectID`: ID of the DID whose pending txn is being deleted
        """

        path_params: Dict[str, Any] = {
            "did_id": did_id,
            "domain_name": domain_name,
        }
        resp = await self.delete(
            f"/domains/{domain_name}/dids/{did_id}/pending-txn/", params=path_params
        )

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def list_public_vcs(
        self,
        query_arguments: credential_queries.ListPublicVcsQuery,
        domain_name: str,
    ) -> credential_schemas.PageVerifiableCredential:
        """
                ## List public VCs in a given domain.

        Args:
        - `domain`: You can scope the request by domain.

        - `vc_filter`: Filtering parameters, encapsulated by the VCFilter.


        Returns:
        - `Page[VerifiableCredential]`: A page of VC objects that belong to the current user.

        ### Filters:
        For a detailed description and usage examples of the `VCFilter` parameters, please refer to the `VCFilter` model
        defined in the OpenAPI schema section of this documentation.

        - `__ilike`: Used for case-insensitive pattern matching. For example, `metadata__alias__ilike` would be used to search for
        aliases that match a specified pattern, ignoring case.

        - `__in`: Used to filter data that matches any value in a provided list. For example,
          - `metadata__tags__in` filters for records where the tags attribute matches any value in the given list.

          - `vc__type__in` will find VCs where the `vc.vc.type` field matches one of the specified strings in the list.

            - **A comma separated list, no spaces and no quotes.**

        - `__lte`: "less than or equal to". For example, `created_at__lte` would filter for records created at or before a
        specified date.

        - `__gte`: "greater than or equal to". For example, `created_at__gte` would filter for records created at or after a
        specified date.

        - `__fields`: (List[str]) For VCs this filter is used to match on claims. Enter the dot separated keys path and, if
        required, a $-delimited value. **__fields**  is a special filter that allows matching on arbitrary document
        subfield keys and values.
          - Example1: `degree` will find VCs having claim attribute`vc.credentialSubject.degree`.

          - Example2: `degree.type, groupMembership.group` will find VCs having attribute `vc.credentialSubject.degree.type`
          or `vc.credentialSubject.groupMembership.group`.

          - Example3: `degree.name$Bachelor of Science Optometry` finds claims where
          `vc.credentialSubject.degree.name=="Bachelor of Science Optometry"`.

          - Example4: `degree.name$Bachelor of Science Optometry, groupMembership.group$maintenance` finds claims where

            `vc.credentialSubject.degree.name=="Bachelor of Science Optometry"` or `groupMembership.group=="maintenance"`.
        """

        # get rid of items where None
        query_params = {
            k: v for k, v in asdict(query_arguments).items() if v is not None
        }

        path_params: Dict[str, Any] = {
            "domain_name": domain_name,
        }
        resp = await self.get(
            f"/domains/{domain_name}/vcs/public-vcs/", params=path_params | query_params
        )

        try:
            resp_model = credential_schemas.PageVerifiableCredential.model_validate(
                resp.json()
            )
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def list_vcs(
        self,
        query_arguments: credential_queries.ListVcsQuery,
        domain_name: str,
    ) -> credential_schemas.PageVerifiableCredential:
        """
                ## List VCs issued or owned by the logged-in is user.
        Args:
        - `domain`: You can scope the request by domain.
        - `my_vcs`: Set to `true` to retrieve VCs that apply to me (where I am the credentialSubject).
        - `issued_vcs`:  Set to `true` to retrieve VCs I have issued as a trusted authority.
            - `Note:` When both `my_vcs` and `issued_vcs` are  `blank` or `false` all VCs related to the user are returned.

        - `vc_filter`: Filtering parameters, encapsulated by the VCFilter.


        Returns:
        - `Page[VerifiableCredential]`: A page of VC objects that belong to the current user.

        ### Filters:
        For a detailed description and usage examples of the `VCFilter` parameters, please refer to the `VCFilter` model
        defined in the OpenAPI schema section of this documentation.

        - `__ilike`: Used for case-insensitive pattern matching. For example, `metadata__alias__ilike` would be used to search for
        aliases that match a specified pattern, ignoring case.

        - `__in`: Used to filter data that matches any value in a provided list. For example,
          - `metadata__tags__in` filters for records where the tags attribute matches any value in the given list.

          - `vc__type__in` will find VCs where the `vc.vc.type` field matches one of the specified strings in the list.

            - **A comma separated list, no spaces and no quotes.**

        - `__lte`: "less than or equal to". For example, `created_at__lte` would filter for records created at or before a
        specified date.

        - `__gte`: "greater than or equal to". For example, `created_at__gte` would filter for records created at or after a
        specified date.

        - `__fields`: (List[str]) For VCs this filter is used to match on claims. Enter the dot separated keys path and, if
        required, a $-delimited value. **__fields**  is a special filter that allows matching on arbitrary document
        subfield keys and values.
          - Example1: `degree` will find VCs having claim attribute`vc.credentialSubject.degree`.

          - Example2: `degree.type, groupMembership.group` will find VCs having attribute `vc.credentialSubject.degree.type`
          or `vc.credentialSubject.groupMembership.group`.

          - Example3: `degree.name$Bachelor of Science Optometry` finds claims where
          `vc.credentialSubject.degree.name=="Bachelor of Science Optometry"`.

          - Example4: `degree.name$Bachelor of Science Optometry, groupMembership.group$maintenance` finds claims where

            `vc.credentialSubject.degree.name=="Bachelor of Science Optometry"` or `groupMembership.group=="maintenance"`.
        """

        # get rid of items where None
        query_params = {
            k: v for k, v in asdict(query_arguments).items() if v is not None
        }

        path_params: Dict[str, Any] = {
            "domain_name": domain_name,
        }
        resp = await self.get(
            f"/domains/{domain_name}/vcs/", params=path_params | query_params
        )

        try:
            resp_model = credential_schemas.PageVerifiableCredential.model_validate(
                resp.json()
            )
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def create_vc(
        self,
        domain_name: str,
        createvchttp: credential_schemas.CreateVCHttp,
    ) -> str:
        """
                ## Create VC

        To create a VC requires two DIDs. Both DIDs must be valid published DIDs. Optional start and end dates can be
        supplied. Parameters that control proof generation must also be supplied.

        Args:

        - `domain`: The Domain name where the `VC` will be created.

        - `vc_http_input`:  The input model `CreateVCHttp`

            - `auto_accept`: If `true` the VC is accepted immediately on behalf of the Holder. Note: setting `true` requires `Admin` permission.

            - `is_public`: Optional, if `true` the VC can be read by anyone with access to the domain.

            - `issuer`: The issuer DID-string ID.

            - `subject`: The `credentialSubject` DID-string ID.

            - `valid_from`: Date-time from which this VC is valid.

            - `valid_until`: Expiry date-time of this VC.

            - `material`: Proof challenge inputs, used to add the proof to the VC:

            - `claims`: is dictionary of `property: values` that represent individual claims about the `credentialSubject`.

            - `proof_in_sig`: when True it makes the proof value part of the data that is used in the proof. Defaults to False.

            - `verification_key`: the verification method you would like to use when creating the VC

        Returns:
        - `DocumentId`: The MongoDB ObjectID of the newly created Document.<br><br>

        ### CreateVCHttp detail:

        - **tags (Optional)**:

          - Description: A list of _**tags**_ attached to the _**VC**_.

          - Example: `<Drivers License>`

        - **auto_accept**:

          - Description: If `true` the VC is accepted immediately on behalf of the Holder. Note: setting `true` requires `Admin` permission.

          - Example: `false`

        - **issuer**:

          - Description: The **DID** representing the issuing authority for this VC (requires DID.permssion==ISSUER).

          - Example: `did:smb1:1337:0xea0fc982ca22ea0141c3452325c372ff728e9ccd:18322500091651578819492444870201097984271428616569706638674662898632050307001`

        - **subject**:

          - Description: The **DID** representing the entity to which the VC applies (the credentialSubject).

          - Example: `did:smb1:1337:0xfc98c982ca22ea0141c3452325c372ff728e9ccd:18322500091651578819492444870201097984271428616569706638674662898632050307982`

        - **valid_from  (Optional)**:

          - Starting date-time that the VC becomes in force.

          - Example: `<2010-06-15T21:24:10.768473>`

        - **valid_until  (Optional)**:

          - Date-time that the VC will become invalid.

          - Example: `<2050-06-15T21:24:10.768473>`

        - **materials**:

          - Proof challenge inputs, used to add the proof to the VC

          - Example: `{"circom_circuit": "SMTInclusionSingleClaim"}`

        - **claims**: The claims being made about the `credentialSubject`.
            ```
            "claims": {
                "https://www.w3.org/2018/credentials/examples/v1": {
                    "degree": {
                        "type": "BachelorDegree",
                        "name": "Bachelor of Science and Arts"
                    }
                }
            }
            ```
            In the example,

            - `"representative"`: is the `claim_schema` property.

            - `"value"`: This can be a `bool`, `int`, `str`, or `dict` based on the *claim_schema* definition.

            - `"claim_schema"`:Is the IRI schema link identifying the schema for the specified claim.

        ## Full payload example
        Below is a full payload example. You must set the following fields (see above for descriptions):

        - `"issuer:` ...

        - `"subject":` ...

            - Update or delete `tags`, `validFrom`, `validUntil`.

            - The `claims` entered must be from a known schema.

                - If `claim_schema` is `null`, the `credential-service`looks for a schema in its known contexts.


        ### Example 1:

                {
                    "tags": ["degree", "bsc"],
                    "@context": ["https://www.w3.org/2018/credentials/v1"],
                    "issuer": "did:smb1:1337:0xfc98c982ca22ea0141c3452325c372ff728e9ccd:39517405560208510513658073967297468008711112795722749167466577185994559263742",
                    "valid_from": "2024-03-08T01:37:35.899Z",
                    "valid_until": "2026-03-08T01:37:35.899Z",
                    "type": ["VerifiableCredential"],
                    "material": {"circom_circuit": "SMTInclusionSingleClaim"},
                    "subject": "did:smb1:1337:0xfc98c982ca22ea0141c3452325c372ff728e9ccd:39517405560208510513658073967297468008711112795722749167466577185994559263742",
                    "claims": {
                        "https://www.w3.org/2018/credentials/examples/v1": {
                            "degree": {
                                "type": "BachelorDegree",
                                "name": "Bachelor of Science and Arts"
                            }
                        }
                    },
                    "verification_key": "#1",
                    "proof_in_sig": True
                }

        ### Example 2:

                {
                    "tags": ["dev1", "fred-holder"],
                    "@context": ["https://www.w3.org/2018/credentials/v1"],
                    "issuer": "did:smb1:1337:0xfc98c982ca22ea0141c3452325c372ff728e9ccd:35658973081941150517877546146441453457835196343845723562092740532250386250123",
                    "valid_from": "2024-03-08T01:37:35.899Z",
                    "valid_until": "2026-03-08T01:37:35.899Z",
                    "type": ["VerifiableCredential"],
                    "material": {"circom_circuit": "SMTInclusionSingleClaim"},
                    "subject": "did:smb1:1337:0xfc98c982ca22ea0141c3452325c372ff728e9ccd:78218754147316378273184740864117609881796548893517659643381541228635294090456",
                    "claims": {
                        "https://simbachain.github.io/context/claims/schema/demo/representative.jsonld": {
                            "representative": {"title": "King"}
                        }
                    },
                    "verification_key": "did:example:123#1"
                }

        ### Example 3:

                {
                    "tags": ["SEE"],
                    "@context": ["https://www.w3.org/2018/credentials/v1"],
                    "issuer": "did:smb1:1337:0xfc98c982ca22ea0141c3452325c372ff728e9ccd:35658973081941150517877546146441453457835196343845723562092740532250386250123",
                    "valid_from": "2024-03-08T01:37:35.899Z",
                    "valid_until": "2026-03-08T01:37:35.899Z",
                    "type": ["VerifiableCredential"],
                    "material": {"circom_circuit": "SMTInclusionSingleClaim"},
                    "subject": "did:smb1:1337:0xfc98c982ca22ea0141c3452325c372ff728e9ccd:78218754147316378273184740864117609881796548893517659643381541228635294090456",
                    "claims": {
                        "https://simba-dev-claim-service.platform.simbachain.com/context/claims/schema/e616/appAccess.jsonld": {
                            "appAccess": {
                                "app": "appName",
                                "deviceDid": "did:smb1:1337:0x1e1a08635650ba7dbf50e288ec6fe1f0cdd589c8:66268477513221317904738054106931844069421232936537904336167242563918357599489"
                                }
                        }
                    },
                    "verification_key": "#1",
                }
        """

        path_params: Dict[str, Any] = {
            "domain_name": domain_name,
        }
        resp = await self.post(
            f"/domains/{domain_name}/vcs/",
            data=str(createvchttp)
            if not issubclass(type(createvchttp), BaseModel)
            else createvchttp.model_dump_json(),  # type: ignore
            params=path_params,
        )

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def get_vc(
        self,
        vc_id: str,
        domain_name: str,
    ) -> credential_schemas.CredentialServiceDomainModelsVerifiableCredential:
        """
                ## GET VC

        Args:
        - `vc_id`: The MongoDB ObjectID of the VC.

        - `domain`: Name of the `Domain` where the `VC` is located.

        Returns:
        - A `VC` model, see the OpenAPI schema section of this documentation.
        """

        path_params: Dict[str, Any] = {
            "vc_id": vc_id,
            "domain_name": domain_name,
        }
        resp = await self.get(f"/domains/{domain_name}/vcs/{vc_id}", params=path_params)

        try:
            resp_model = credential_schemas.CredentialServiceDomainModelsVerifiableCredential.model_validate(
                resp.json()
            )
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def update_vc(
        self,
        vc_id: str,
        domain_name: str,
        updatevchttp: credential_schemas.UpdateVcHttp,
    ) -> str:
        """ """

        path_params: Dict[str, Any] = {
            "vc_id": vc_id,
            "domain_name": domain_name,
        }
        resp = await self.put(
            f"/domains/{domain_name}/vcs/{vc_id}",
            data=str(updatevchttp)
            if not issubclass(type(updatevchttp), BaseModel)
            else updatevchttp.model_dump_json(),  # type: ignore
            params=path_params,
        )

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def revoke_vc(
        self,
        vc_id: str,
        domain_name: str,
    ) -> str:
        """
                ## Revoke a VC

        If invoked with a self-signing DID, then pending_transaction must be obtained from vc.metadata, signed, and submtitted to /vcs/{vc_id}/submit_signed_revocation/. If invoked with server-signing DID, then no further action is needed.

        Args:
        - `vc_id`: id of the VC to be revoked.

        - `domain`: Domain where the VC resides.

        Returns:
        - `ObjectID`: ID of the VC that is being revoked
        """

        path_params: Dict[str, Any] = {
            "vc_id": vc_id,
            "domain_name": domain_name,
        }
        resp = await self.delete(
            f"/domains/{domain_name}/vcs/{vc_id}", params=path_params
        )

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def create_dpp(
        self,
        domain_name: str,
        dppinput: credential_schemas.DPPInput,
    ) -> str:
        """
                ## Create DPP

        To create a DPP requires one issuer DID. The issuer must be in the form of a Credential Issuer model.
        Optional start and end dates can be supplied. Parameters that control proof generation must also be supplied. Note
        that DPPs by their very nature are public.

        Args:

        - `domain`: The Domain name where the `DPP` will be created.

        - `dpp_input`:  The input model `DPPInput`

            - `issuer`: The CredentialIssuer model containing issuer DID-string ID.

            - `subject`: The `credentialSubject`, a `Product` model, see swagger example value at `subject` key.

            - `valid_from`: Date-time from which this VC is valid.

            - `valid_until`: Expiry date-time of this VC.

            - `credential_id`: URI used as the VC `id` field. Optional.

            - `material`: Proof challenge inputs, used to add the proof to the VC. Optional.

            - `renderer`: is a list of `RenderInput` models that contain a type, usually `WebRenderingTemplate2022` and an
            HTML template string, which should be a representation of the DPP in HTML.

        Returns:
        - `DocumentId`: The MongoDB ObjectID of the newly created Document.<br><br>
        """

        path_params: Dict[str, Any] = {
            "domain_name": domain_name,
        }
        resp = await self.post(
            f"/domains/{domain_name}/vcs/dpps/",
            data=str(dppinput)
            if not issubclass(type(dppinput), BaseModel)
            else dppinput.model_dump_json(),  # type: ignore
            params=path_params,
        )

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def accept_vc(
        self,
        query_arguments: credential_queries.AcceptVcQuery,
        vc_id: str,
        domain_name: str,
    ) -> str:
        """
                ## Accept an issued VC

        When a user is issued a VC by another actor, the VC must be accepted before it can be used in a VP.
        The user can also reject the issued VC should they so desire.

        Args:
        - `accept`: If **True**, the vc will be accepted otherwise it is rejected.

        - `vc_id`: The id of the vc being accepted/rejected.

        Returns:
        - `DocumentId`: The MongoDB ObjectID of the updated VC.
        """

        # get rid of items where None
        query_params = {
            k: v for k, v in asdict(query_arguments).items() if v is not None
        }

        path_params: Dict[str, Any] = {
            "vc_id": vc_id,
            "domain_name": domain_name,
        }
        resp = await self.put(
            f"/domains/{domain_name}/vcs/{vc_id}/accept/",
            params=path_params | query_params,
        )

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def submit_signed_vc_revocation(
        self,
        vc_id: str,
        domain_name: str,
        didsignedtxn: credential_schemas.DIDSignedTxn,
    ) -> str:
        """
                ## Submit signed VC revocation

        If revocation was invoked at /vcs/{vc_id}/ using a self-signed DID, then this is the endpoint that the signed revocation transaction should be submitted to.

        Args:
        - `vc_id`: id of the VC to be revoked

        - `did_txn`: DIDSignedTxn object, which contains signed_txn and optional txn_id.

            - Example:

                ```
                {
                    "signed_txn": {
                        "raw_transaction": "0xf8a982010a808301c88c941e1a08635650ba7dbf50e288ec6fe1f0cdd589c880b8445128d9287418cfa4ac1e82b48a5dce5c0cfc726f871f0323675fd72884e4ca2ef01bd001119a4974372b9604ed760b5e07d3ec68470c64a8ac8d930c195123596d6d9279820a96a0447ea6baf2939f2715ed495a005943707e49f2dc2a5a7f1c9a0461f914b0332aa009cf2a53418be966d64b0f88b3c8d12c6c2e507e653d93a93ffe2b129eeacabc",
                        "hash": "0x74bbb09f644b525471fa01649c3fcfa9041e5666380cbed89b9ab19790f901a9",
                        "r": 30981047163814140783287298754053747282814365915322052127397526155826671137578,
                        "s": 4436845097583516932672107757708642469205335746548505565616760742112783944380,
                        "v": 2710,
                    },
                }
                ```

        Returns:
        - `ObjectID`: ID of the VC that is being revoked
        """

        path_params: Dict[str, Any] = {
            "vc_id": vc_id,
            "domain_name": domain_name,
        }
        resp = await self.put(
            f"/domains/{domain_name}/vcs/revoked-vcs/{vc_id}/submit-signed/",
            data=str(didsignedtxn)
            if not issubclass(type(didsignedtxn), BaseModel)
            else didsignedtxn.model_dump_json(),  # type: ignore
            params=path_params,
        )

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def submit_signed_vc(
        self,
        vc_id: str,
        domain_name: str,
        submitsignedcredentialhttp: credential_schemas.SubmitSignedCredentialHTTP,
    ) -> str:
        """
                ## Submit a signed VC, which has been signed by a private key

        When a user with a self-signing DID creates a VC, they must sign the VC and submit it, to create the proof for the VC

        Args:
        - `domain`: Domain where the VC resides.

        - `vc_id`: The id of the VC, for which the signature is being submitted.

        - `submit_signed_input`: SubmitSignedCredentialHTTP model, which contains signature, which is the signed VC

        Returns:
        - `DocumentId`: The MongoDB ObjectID of the signed VC.
        """

        path_params: Dict[str, Any] = {
            "vc_id": vc_id,
            "domain_name": domain_name,
        }
        resp = await self.put(
            f"/domains/{domain_name}/vcs/signed-vcs/{vc_id}/submit-signed/",
            data=str(submitsignedcredentialhttp)
            if not issubclass(type(submitsignedcredentialhttp), BaseModel)
            else submitsignedcredentialhttp.model_dump_json(),  # type: ignore
            params=path_params,
        )

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def get_pending_vc_txn(
        self,
        vc_id: str,
        domain_name: str,
    ) -> credential_schemas.PendingTxn:
        """
                ## Get PENDING VC transaction

        Args:
        - `domain`: Domain where the VC resides.

        - `vc_id`: id of the VC to be revoked

        Returns:
        - `PendingTxn`: PendingTxn object that contains txn_id and raw_txn. raw_txn is what gets signed and then submitted to complete the DID update txn

            - Example:

                ```
                {
                    "txn_id": "0ad500e8-c689-4b4e-8b74-d63e9b9d027b",
                    "raw_txn": {
                        "chainId": "1337",
                        "data": "0x7bf5a7b2000000000000000000000000000000000000000000000000000000000000006000000000000000000000000018636c2d650c9f7507da23d7aa5cb587424f4fe700000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000041736d62313a746573742d646f6d61696e2d313a63687269732e73696d706b696e4073696d6261636861696e2e636f6d3a4353696d6d6f2d706572663a766f6d777000000000000000000000000000000000000000000000000000000000000000",
                        "from": "0x879973f65187A6699db7034e784E45c3b324feCF",
                        "gas": "0x74c08",
                        "gasPrice": "0x0",
                        "nonce": "0x1be1",
                        "to": "0x1E1a08635650Ba7dbF50e288Ec6fE1f0CdD589c8",
                        "value": "0x0"
                    }
                }
                ```
        """

        path_params: Dict[str, Any] = {
            "vc_id": vc_id,
            "domain_name": domain_name,
        }
        resp = await self.get(
            f"/domains/{domain_name}/vcs/{vc_id}/pending-txn/", params=path_params
        )

        try:
            resp_model = credential_schemas.PendingTxn.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def delete_pending_vc_txn(
        self,
        vc_id: str,
        domain_name: str,
    ) -> credential_schemas.PendingTxn:
        """
                ## Delete PENDING VC transaction

        This endpoint should typically be invoked to delete a pending VC revocation transaction, but there may be other use cases.

        Args:
        - `vc_id`: id of the VC to be revoked

        Returns:
        - `ObjectID`: ID of the VC that is being revoked
        """

        path_params: Dict[str, Any] = {
            "vc_id": vc_id,
            "domain_name": domain_name,
        }
        resp = await self.delete(
            f"/domains/{domain_name}/vcs/{vc_id}/pending-txn/", params=path_params
        )

        try:
            resp_model = credential_schemas.PendingTxn.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def get_vc_digest(
        self,
        vc_id: str,
        domain_name: str,
    ) -> credential_schemas.ProofDigest:
        """
                ## get VC digest

        When self-signing a VC / VC proof, the digest is what needs to be signed by a private key

        Args:
        - `domain`: Domain where the VC resides.

        - `vc_id`: The id of the VC

        Returns:
        - `ProofDigest`: object containing "digest" (bytes) property, which is what needs to be signed by private key
        """

        path_params: Dict[str, Any] = {
            "vc_id": vc_id,
            "domain_name": domain_name,
        }
        resp = await self.get(
            f"/domains/{domain_name}/vcs/{vc_id}/digest/", params=path_params
        )

        try:
            resp_model = credential_schemas.ProofDigest.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def create_from_vc(
        self,
        domain_name: str,
        addvchttp: credential_schemas.AddVCHttp,
    ) -> credential_schemas.CredentialServiceDomainModelsVerifiableCredential:
        """
                ## Create VC

        Create/Add a VC to Credential-Service using a JSON-LD VC as input.

        Args:

        - `domain`: The Domain name where the `VC` will be created.

        - `vc_http_input`:  The input model `CreateVCHttp`

            - `auto_accept`: If `true` the VC is accepted immediately on behalf of the Holder. Note: setting `true` requires `Admin` permission.

            - `is_public`: Optional, if `true` the VC can be read by anyone with access to the domain.

            - `material`: Optional, proof challenge inputs, used to add the proof to the VC:

            - `verification_key`: Optional, a relative or absolute key reference. This will be ignored if the VC contains a proof.

            - `vc`: A JSON-LD VC.

        Returns:
        - `VerificableCredential`: The newly created Document.<br><br>

        ### CreateVCHttp detail:

        - **tags (Optional)**:

          - Description: A list of _**tags**_ attached to the _**VC**_.

          - Example: `<Drivers License>`

        - **auto_accept**:

          - Description: If `true` the VC is accepted immediately on behalf of the Holder. Note: setting `true` requires `Admin` permission.

          - Example: `false`

        - **materials**:

          - Proof challenge inputs, used to add the proof to the VC

          - Example: `{"circom_circuit": "SMTInclusionSingleClaim"}`

        - **verification_key**:

          - Used to select the DIDs verificationMethod which is used for proof generation and signing when the posted
          JSON-LD VC does not comtain a proof. <br>If not supplied and the VC does not have a proof, the default is to use the
          issuer DID's first verificationMethod.

          - Example:  `"#1" | "did:example:123#1"`


        - **vc**:

          - A well formed JSON-LD VC optionally including a proof, see the example below.


        ## Full payload example

        ### Example 1:

                {
                  "tags": [
                    "string"
                  ],
                  "is_public": "false | true",
                  "auto_accept": "false | true",
                  "material": {},
                  "verification_key": "Optional, #1 | did:example:123#1",
                  "vc": {
                    "@context": [
                      "https://www.w3.org/2018/credentials/v1",
                      "https://www.w3.org/2018/credentials/examples/v1",
                      "https://simbachain.github.io/context/crypto/ERC191Suite2023.jsonld"
                    ],
                    "proof": {
                      "type": "ERC191Signature2023",
                      "created": "2025-03-19T21:04:56.713415+00:00",
                      "proofPurpose": "assertionMethod",
                      "verificationMethod": "did:smb1:1337:0x1e1a08635650ba7dbf50e288ec6fe1f0cdd589c8:87846783959889227866580749686625002103301015674329220177929364676842176513793#1",
                      "proofValue": "0x8e7aae674f27107211b7f5bb7338ce2c5fa2a66595be29ffdb1cdec2e54be7d5108dc89bfdf689bacfde8e7bf5ff49cd6a6323b9778069e8529f4ed03a5319641c"
                    },
                    "id": "urn:uuid:df5e1fac-2b0e-4e13-88a4-f0b6f9097bdb",
                    "type": [
                      "VerifiableCredential"
                    ],
                    "issuer": "did:smb1:1337:0x1e1a08635650ba7dbf50e288ec6fe1f0cdd589c8:87846783959889227866580749686625002103301015674329220177929364676842176513793",
                    "credentialSubject": {
                      "id": "did:smb1:1337:0x1e1a08635650ba7dbf50e288ec6fe1f0cdd589c8:30232190550540842924946097596550793492175973526398728801684738755048631459073",
                      "degree": {
                        "type": "BachelorDegree",
                        "name": "Bachelor of Science and Arts"
                      }
                    },
                    "validFrom": "2024-03-08T01:37:35.899000+00:00",
                    "validUntil": "2026-03-08T01:37:35.899000+00:00"
                  }
                }
        """

        path_params: Dict[str, Any] = {
            "domain_name": domain_name,
        }
        resp = await self.post(
            f"/domains/{domain_name}/vcs/from-vc/",
            data=str(addvchttp)
            if not issubclass(type(addvchttp), BaseModel)
            else addvchttp.model_dump_json(),  # type: ignore
            params=path_params,
        )

        try:
            resp_model = credential_schemas.CredentialServiceDomainModelsVerifiableCredential.model_validate(
                resp.json()
            )
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def get_vps(
        self,
        query_arguments: credential_queries.GetVpsQuery,
        domain_name: str,
    ) -> credential_schemas.PageVerifiablePresentation:
        """
                ## List VPs created by this user.

        Args:
        - `domain`: You can scope the request by domain.

        - `vp_filter`: Filtering parameters, encapsulated by the VPFilter.


        Returns:
        - `Page[VerifiablePresentation]`: A page of VP objects that belong to the current user.

        ### Filters:
        For a detailed description and usage examples of the `VCFilter` parameters, please refer to the `VCFilter` model
        defined in the OpenAPI schema section of this documentation.

        - `__ilike`: Used for case-insensitive pattern matching. For example, `alias__ilike` would be used to search for
        aliases that match a specified pattern, ignoring case.

        - `__in`: Used to filter data that matches any value in a provided list. For example, `tags__in` filters for records
        where the tags attribute matches any value in the given list.

        - `__lte`: "less than or equal to". For example, `created_at__lte` would filter for records created at or before a
        specified date.

        - `__gte`: "greater than or equal to". For example, `created_at__gte` would filter for records created at or after a
        specified date.
        """

        # get rid of items where None
        query_params = {
            k: v for k, v in asdict(query_arguments).items() if v is not None
        }

        path_params: Dict[str, Any] = {
            "domain_name": domain_name,
        }
        resp = await self.get(
            f"/domains/{domain_name}/vps/", params=path_params | query_params
        )

        try:
            resp_model = credential_schemas.PageVerifiablePresentation.model_validate(
                resp.json()
            )
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def create_vp(
        self,
        domain_name: str,
        createvphttp: credential_schemas.CreateVPHttp,
    ) -> str:
        """
                ## Create VP

        Create a VP which can be used to present all or part of the logged-in-user's VerifiableCredential
        information in a secure and possibly redacted manner.

        Args:
        - `domain`: The Domain name where the `VP` will be created.

        - `vc_http`:  The input model `CreateVPHttp`

            - `vc_id`: the MongoDB ObjectID of the [VC][credential_service.domain.models.VerifiableCredential] being presented.

            - `proof_type`: `"SMTInclusionProof"`

            - `material`: Proof challenge input dict, used to add the proof to the VP, example,
                ```
                {
                    "challenge": "0x18",
                    "domain": "0x8d242e4bc081e2eeD5eb9d6BF734DdF5d2F435e0",
                    "presentation_time": 1698232514,
                }
                ```

            - `verification_key`: the verification method you would like to use (subject did)

        Returns:
        - `DocumentId`: The MongoDB ObjectID of the newly created Document.<br><br>

        ## Full payload example
        Below is a full payload example.
        - All fields should be set as required (see above descriptions of the fields):

        ```
        {
          "vc_id": "65f2c5d51f2315b03db61234",
          "proof_type": "SMTInclusionProof",
          "material": {
            "challenge": "0x18",
            "domain": "0x8d242e4bc081e2eeD5eb9d6BF734DdF5d2F435e0",
            "presentation_time": 1698232514
          }
          "verification_key": "#1"
        }
        ```
        """

        path_params: Dict[str, Any] = {
            "domain_name": domain_name,
        }
        resp = await self.post(
            f"/domains/{domain_name}/vps/",
            data=str(createvphttp)
            if not issubclass(type(createvphttp), BaseModel)
            else createvphttp.model_dump_json(),  # type: ignore
            params=path_params,
        )

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def get_vp(
        self,
        vp_id: str,
        domain_name: str,
    ) -> credential_schemas.VerifiablePresentation:
        """
                ## GET VP

        Args:
        - `vp_id`: The MongoDB ObjectID of the VP.

        - `domain`: Name of the `Domain` where the `VP` is located.

        Returns:
        - A `VP` model, see the OpenAPI schema section of this documentation.
        """

        path_params: Dict[str, Any] = {
            "vp_id": vp_id,
            "domain_name": domain_name,
        }
        resp = await self.get(f"/domains/{domain_name}/vps/{vp_id}", params=path_params)

        try:
            resp_model = credential_schemas.VerifiablePresentation.model_validate(
                resp.json()
            )
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def submit_signed_vp(
        self,
        vp_id: str,
        domain_name: str,
        submitsignedcredentialhttp: credential_schemas.SubmitSignedCredentialHTTP,
    ) -> str:
        """
                ## Submit a signed VP, which has been signed by a private key

        When a user with a self-signing DID creates a VP, they must sign the VP and submit it, to create the proof for the VP

        Args:
        - `vp_id`: The id of the VP, for which the signature is being submitted.

        - `submit_signed_input`: SubmitSignedCredentialHTTP model, which contains signature, which is the signed VP

        Returns:
        - `DocumentId`: The MongoDB ObjectID of the signed VP.
        """

        path_params: Dict[str, Any] = {
            "vp_id": vp_id,
            "domain_name": domain_name,
        }
        resp = await self.put(
            f"/domains/{domain_name}/vps/signed-vps/{vp_id}/submit-signed/",
            data=str(submitsignedcredentialhttp)
            if not issubclass(type(submitsignedcredentialhttp), BaseModel)
            else submitsignedcredentialhttp.model_dump_json(),  # type: ignore
            params=path_params,
        )

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def get_vp_digest(
        self,
        vp_id: str,
        domain_name: str,
    ) -> credential_schemas.ProofDigest:
        """
                ## get VP digest

        When self-signing a VP / VP proof, the digest is what needs to be signed by a private key

        Args:
        - `domain`: Domain where the VC resides.

        - `vp_id`: The id of the VP

        Returns:
        - `ProofDigest`: object containing "digest" (bytes) property, which is what needs to be signed by private key
        """

        path_params: Dict[str, Any] = {
            "vp_id": vp_id,
            "domain_name": domain_name,
        }
        resp = await self.get(
            f"/domains/{domain_name}/vps/{vp_id}/digest/", params=path_params
        )

        try:
            resp_model = credential_schemas.ProofDigest.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def list_tasks(
        self,
        query_arguments: credential_queries.ListTasksQuery,
        domain_name: str,
    ) -> credential_schemas.PageTask:
        """
                ## List Tasks created by this user.
        Args:
        - `task_filter`: Filtering parameters encapsulated by the `TaskFilter`

        Returns:
        - `Page[Task]`: A page of Task objects that belong to the current user.

        Filters:
        - `id`: The ObjectId of a task.

        - `order_by`: a list of attributes on which to sort, for example  `created_at`

        - `__in`: Used to filter data that matches any value in a provided list. For example, `tags__in` filters for records
        where the tags attribute matches any value in the given list.

        - `__lte`: "less than or equal to". For example, `created_at__lte` would filter for records created at or before a
        specified date.

        - `__gte`: "greater than or equal to". For example, `created_at__gte` would filter for records created at or after a
        specified date.
        """

        # get rid of items where None
        query_params = {
            k: v for k, v in asdict(query_arguments).items() if v is not None
        }

        path_params: Dict[str, Any] = {
            "domain_name": domain_name,
        }
        resp = await self.get(
            f"/domains/{domain_name}/tasks/", params=path_params | query_params
        )

        try:
            resp_model = credential_schemas.PageTask.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def get_task(
        self,
        task_id: str,
        domain_name: str,
    ) -> credential_schemas.Task:
        """
                ## Get a Task created by the logged-in user.

        Args:
        - `task_id`: the mongodb document id returned by `create_did`

        - `x_simba_sub_id`: Optional Member service id (UUID) for the user

        Returns:
        - `Task`: a single task object which corresponds to the `task_id`
        """

        path_params: Dict[str, Any] = {
            "task_id": task_id,
            "domain_name": domain_name,
        }
        resp = await self.get(
            f"/domains/{domain_name}/tasks/{task_id}", params=path_params
        )

        try:
            resp_model = credential_schemas.Task.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def verify_vc(
        self,
        body: object,
    ) -> credential_schemas.VerificationResult:
        """
                ## Verify VC
        This endpoint can be used to verify the integrity of a VerifiableCredential.

        Args:
        - `vc`: A JSON_LD VerifiableCredential

        Returns:
        - A `VerificationResult` model, see the OpenAPI schema section of this documentation.
        """

        path_params: Dict[str, Any] = {}
        resp = await self.post(
            "/verify/vc/",
            data=str(body)
            if not issubclass(type(body), BaseModel)
            else body.model_dump_json(),  # type: ignore
            params=path_params,
        )

        try:
            resp_model = credential_schemas.VerificationResult.model_validate(
                resp.json()
            )
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def verify_vp(
        self,
        body: object,
    ) -> credential_schemas.VerificationResult:
        """
                ## Verify VP
        This endpoint can be used to verify the integrity of a VerifiablePresentation.

        Args:
        - `vp`: A JSON_LD VerifiablePresentation

        Returns:
        - A `VerificationResult` model, see the OpenAPI schema section of this documentation.
        """

        path_params: Dict[str, Any] = {}
        resp = await self.post(
            "/verify/vp/",
            data=str(body)
            if not issubclass(type(body), BaseModel)
            else body.model_dump_json(),  # type: ignore
            params=path_params,
        )

        try:
            resp_model = credential_schemas.VerificationResult.model_validate(
                resp.json()
            )
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def get_version(
        self,
    ) -> str:
        """ """

        path_params: Dict[str, Any] = {}
        resp = await self.get("/version/", params=path_params)

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def health(
        self,
    ) -> object:
        """ """

        path_params: Dict[str, Any] = {}
        resp = await self.get("/healthz/", params=path_params)

        try:
            resp_model = object.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def ping(
        self,
    ) -> credential_schemas.PingResponses:
        """ """

        path_params: Dict[str, Any] = {}
        resp = await self.get("/pingz/", params=path_params)

        try:
            resp_model = credential_schemas.PingResponses.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model
