import asyncio
import time
from dataclasses import asdict, dataclass, fields
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID

from simba_sdk.core.requests.client.credential.client import CredentialClient
from simba_sdk.core.requests.client.credential.queries import (
    ListCustodialAccountsQuery,
    ListDidsQuery,
    ListVcsQuery,
)
from simba_sdk.core.requests.client.credential.schemas import (
    CreateAccountHttp,
    CreateDidHttp,
    CreateSchemaHttp,
)
from simba_sdk.core.requests.client.members.client import MembersClient
from simba_sdk.core.requests.client.members.queries import (
    GetDomainsQuery,
    GetOrganisationsQuery,
)
from simba_sdk.core.requests.client.members.schemas import (
    AddDomainOrganisationInput,
    AdminAddUserToOrgDomain,
    CreateInviteSubOrgsInput,
    CreateOrganisationInput,
)
from simba_sdk.core.requests.client.resource.client import ResourceClient
from simba_sdk.core.requests.client.resource.queries import GetStoragesQuery
from simba_sdk.core.requests.client.resource.schemas import CreateResourceBundleRequest
from simba_sdk.core.requests.exception import EnsureException
from simba_sdk.sessions import parse
from simba_sdk.sessions.base import Base, BaseSession
from simba_sdk.sessions.did import DID, DIDSession
from simba_sdk.sessions.resource import Resource, ResourceSession, Storage
from simba_sdk.sessions.vc import VC, VCSession
from simba_sdk.sessions.vp import VP, VPSession


@dataclass
class ClaimAttribute(Base):
    name: str
    type: str  # input name
    suggested_values: List[str]
    hash: str = ""
    description: Optional[str] = None


@dataclass
class Schema(Base):
    schema_name: str
    attributes: Union[Dict[str, ClaimAttribute], List[Dict[str, ClaimAttribute]]]
    hash: str = ""
    id: str = ""
    schema_description: Optional[str] = None


@dataclass
class Registry(Base):
    schemas: List[str]


@dataclass
class Domain(Base):
    name: str
    display_name: str = ""
    id: Optional[UUID] = None
    organisations: Optional[List[str]] = None


@dataclass
class Organisation(Base):
    name: str
    display_name: str = ""
    id: Optional[UUID] = None


@dataclass
class Account(Base):
    alias: str
    network: str
    public_key: Optional[str] = None
    organisation: Optional[str] = None
    id: Optional[UUID] = None


async def _await_task(client, task_id: str, domain: str):
    timeout = 500
    time_taken = 0
    while time_taken < timeout:
        now = time.time()
        task = await client.get_task(task_id=task_id, domain_name=domain)
        if task.status == "FAILED":
            raise Exception(f"Task failed.\n{task.error_details}")
        if task.status == "COMPLETED":
            return task
        else:
            await asyncio.sleep(5)
            time_taken += time.time() - now
    raise Exception(f"Timeout waiting for task.\n{task.status}")


class RegistrySession(BaseSession):
    def __init__(self, domain: str, **kwargs):
        super().__init__(**kwargs)
        self._clients = {
            "credential": CredentialClient,
        }
        self.domain = domain

    async def __aenter__(self):
        await super().__aenter__()
        registry_resp = await self._clients["credential"].get_schema_registry(
            domain_name=self.domain
        )
        self.registry = {
            schema.name: Schema(
                id=schema.id,
                schema_name=schema.name,
                hash=schema.hash,
                attributes=[
                    ClaimAttribute(
                        name=attr.name,
                        type=attr.type,
                        hash=attr.hash,
                        suggested_values=attr.suggestedValues,
                    )
                    for attr in schema.attributes or []
                ],
            )
            for schema in registry_resp.schemas.values()
        }
        return self

    @parse(Schema)
    async def create_schema(self, schema: Schema) -> None:
        attribs = {k: asdict(v) for k, v in schema.attributes.items()}  # type: ignore
        create_schema = CreateSchemaHttp(
            schema_name=schema.schema_name,
            attributes=attribs,
        )
        task = await self._clients["credential"].create_schema(
            domain_name=self.domain, createschemahttp=create_schema
        )
        await _await_task(
            client=self._clients["credential"],
            task_id=task.field_id,
            domain=self.domain,
        )

    async def delete_schema(self, schema_name: str) -> None:
        await self._clients["credential"].delete_schema(
            domain_name=self.domain, schema_name=schema_name
        )
        self.registry.pop(schema_name)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.registry = None
        await super().__aexit__(exc_type, exc_val, exc_tb)


class DomainSession(BaseSession):
    domain: Optional[Domain]
    account: Optional[Account]
    query = GetDomainsQuery

    def __init__(
        self, name: str, account: Union[UUID, Account, None] = None, **kwargs: str
    ) -> None:
        """
        name: str - The name of the domain
        account: Union[UUID, str, None] - Optionally specify a custodial Blocks account to use for transactions, either by its id (UUID) or public_key (str)
        For kwargs see BaseSession.__init__
        """
        super().__init__(**kwargs)
        self._clients = {
            "members": MembersClient,
            "credential": CredentialClient,
            "resource": ResourceClient,
        }
        self.name = name
        self.account = account
        self.domain = None

    async def __aenter__(self) -> "DomainSession":
        await super().__aenter__()
        field_names = [f.name for f in fields(self.query)]
        if "name" in field_names:
            query = self.query(page=1, size=100, name=self.name)
        elif "domain_name" in field_names:
            query = self.query(page=1, size=100, domain_name=self.name)
        else:
            raise EnsureException("SDK naming mismatch for GetDomainsQuery.")

        if not self.domain:
            domains = await self._clients["members"].get_domains(query_arguments=query)
            if len(domains.items) == 0:
                raise EnsureException(
                    "Domain does not exist, please create one via a UserSession"
                )
            domain = domains.items[0]
            domain.organisations = [
                org["name"] for org in domain.model_dump()["organisations"]
            ]
            self.domain = Domain.from_dict(domain.model_dump())
        accounts_query = ListCustodialAccountsQuery(page=1, size=100, domain=self.name)
        accounts = await self._clients["credential"].list_custodial_accounts(
            accounts_query
        )
        for account in accounts.results:
            if isinstance(self.account, UUID):
                if account.id == self.account:
                    self.account = Account.from_dict(account.model_dump())
                    break
            if isinstance(self.account, Account):
                if (
                    account.alias == self.account.alias
                    and account.network == self.account.network
                ):
                    self.account = Account.from_dict(account.model_dump())
                    break
        else:
            self.account = None
        return self

    @parse(Account)
    async def create_account(self, account: Account) -> None:
        account = await self._clients["credential"].create_custodial_account(
            createaccounthttp=CreateAccountHttp(
                domain=self.name,
                alias=account.alias,
                nickname=account.alias,
                org=account.organisation,
            )
        )
        self.account = Account(
            alias=account.alias,
            network=account.network,
            public_key=account.public_key,
            organisation=None,
            id=account.id,
        )

    async def get_organisation(self, name: str) -> "OrganisationSession":
        organisation_session = OrganisationSession(name=name, settings=self.settings)
        organisation_session.domain = self.domain
        organisation_session.account = self.account
        organisation_session.user = self.user
        return organisation_session

    async def create_organisation(
        self, organisation: Organisation
    ) -> "OrganisationSession":
        organisation_input = CreateOrganisationInput(
            name=organisation.name, display_name=organisation.display_name
        )
        await self._clients["members"].create_organisation(
            createorganisationinput=organisation_input
        )
        await self._clients["members"].add_domain_organisation(
            domain_name=self.name,
            adddomainorganisationinput=AddDomainOrganisationInput(
                organisation_name=organisation.name
            ),
        )
        self.domain.organisations.append(organisation.name)
        return self.get_organisation(organisation.name)

    async def add_user(self, email: str, roles: List[str]):
        _ = await self._clients["members"].admin_add_user_to_org_domain(
            organisation_name=self.name,
            adminaddusertoorgdomain=AdminAddUserToOrgDomain(
                to_email=email,
                role_names=roles,
                sub_organisations=[
                    CreateInviteSubOrgsInput(organisation_name=name, role_names=roles)
                    for name in self.domain.organisations
                ]
                if self.domain.organisations
                else None,
                system_type="ensure",
            ),
        )

    async def get_did(self, did_id: str) -> DIDSession:
        did_session = DIDSession(did_id)
        did_session.domain = self.name
        return did_session

    async def list_dids(self) -> List[Tuple[UUID, DID]]:
        query = ListDidsQuery(page=1, size=100)
        dids_response = await self._clients["credential"].list_dids(
            domain_name=self.name, query_arguments=query
        )
        dids_list = []
        for did in dids_response.items:
            did_obj = DID.from_dict(
                dict(
                    did.metadata.model_dump(),
                    **did.did_document.model_dump(),
                )
            )
            did_obj.did = did.did_document.id
            dids_list.append((did.field_id, did_obj))
        return dids_list

    @parse(DID)
    async def create_did(self, did: DID, timeout: int = 500) -> DIDSession:
        create_did = {
            "name": did.name,
            "trust_profile": did.trust_profile,
            "account": {
                "alias": self.account.alias,
                "public_key": self.account.public_key,
            },
            "permission": did.permission,
            "alias": did.alias,
            "seed": did.seed,
            "nickname": did.nickname,
            "public_name": did.public_name,
        }
        task_id = await self._clients["credential"].create_did(
            domain_name=self.name, createdidhttp=CreateDidHttp(**create_did)
        )
        task = await _await_task(
            client=self._clients["credential"], task_id=task_id, domain=self.name
        )
        did_session = DIDSession(did_id=task.object_id, settings=self.settings)
        did_session.domain = self.name
        return did_session

    async def list_vcs(self):
        query = ListVcsQuery(page=1, size=100)
        vc_response = await self._clients["credential"].list_vcs(
            domain_name=self.name, query_arguments=query
        )
        vc_list = [
            (
                vc.field_id,
                VC.from_dict(
                    dict(
                        vc.vc,
                        **vc.metadata.model_dump(),
                    )
                ),
            )
            for vc in vc_response.items
        ]
        return vc_list

    async def get_vc(self, vc_id: str) -> VCSession:
        vc_session = VCSession(vc_id=vc_id, settings=self.settings)
        vc_session.domain = self.name
        return vc_session

    async def list_vps(self):
        query = ListVcsQuery(page=1, size=100)
        vp_response = await self._clients["credential"].get_vps(
            domain_name=self.name, query_arguments=query
        )
        vp_list = [
            (
                vp.field_id,
                VP.from_dict(
                    dict(
                        vp.vp,
                        **vp.metadata.model_dump(),
                    )
                ),
            )
            for vp in vp_response.items
        ]
        return vp_list

    async def get_vp(self, vp_id: str) -> VPSession:
        vp_session = VPSession(vp_id=vp_id, settings=self.settings)
        vp_session.domain = self.name
        return vp_session

    async def get_resource(self, resource_id: str) -> ResourceSession:
        resource_session = ResourceSession(
            resource_id=resource_id, settings=self.settings
        )
        resource_session.domain = self.name
        return resource_session

    @parse(Resource)
    async def create_resource(self, resource: Resource) -> ResourceSession:
        new_bundle = CreateResourceBundleRequest(
            name=resource.name,
            storage_name=resource.storage,
            tags=resource.tags,
        )
        bundle = await self._clients["resource"].create_bundle(
            createresourcebundlerequest=new_bundle, domain_name=self.name
        )
        session = ResourceSession(
            resource_id=bundle.resource_id, settings=self.settings
        )
        session.domain = self.name
        return session

    async def get_storages(self) -> List[Storage]:
        storages = await self._clients["resource"].get_storages(
            domain_name=self.name, query_arguments=GetStoragesQuery(page=1, size=100)
        )
        return [
            Storage.from_dict({"name": storage.name, "type": storage.storage_type})
            for storage in storages.items
        ]

    async def get_schema_registry(self):
        registry_session = RegistrySession(domain=self.name, settings=self.settings)
        return registry_session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.domain = None
        await super().__aexit__(exc_type, exc_val, exc_tb)


class OrganisationSession(BaseSession):
    organisation: Optional[Organisation]
    query = GetOrganisationsQuery

    def __init__(self, name: str, **kwargs):
        """
        name: str - The name of the domain
        account: Union[UUID, str, None] - Optionally specify a custodial Blocks account to use for transactions, either by its id (UUID) or public_key (str)
        For kwargs see BaseSession.__init__
        """
        super().__init__(**kwargs)
        self._clients = {
            "members": MembersClient,
        }
        self.name = name

    async def __aenter__(self) -> "OrganisationSession":
        await super().__aenter__()
        field_names = [f.name for f in fields(self.query)]
        if "name" in field_names:
            query = self.query(page=1, size=100, name=self.name)
        elif "organisation_name" in field_names:
            query = self.query(page=1, size=100, organisation_name=self.name)
        else:
            raise EnsureException(f"SDK naming mismatch for {self.query.__name__}.")

        organisation = await self._clients["members"].get_domains(query_arguments=query)
        if len(organisation.items) == 0:
            raise EnsureException(
                "Organisation does not exist, please create one via a UserSession"
            )
        self.organisation = Organisation.from_dict(organisation.items[0].model_dump())
