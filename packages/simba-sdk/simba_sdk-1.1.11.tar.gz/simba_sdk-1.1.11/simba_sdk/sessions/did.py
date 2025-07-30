from dataclasses import dataclass
from typing import List, Optional

from simba_sdk.core.requests.client.credential.client import CredentialClient
from simba_sdk.core.requests.client.credential.schemas import (
    CreateVCHttp,
    UpdateDIDMetadataFromUser,
)
from simba_sdk.core.requests.client.resource.client import ResourceClient
from simba_sdk.sessions import parse
from simba_sdk.sessions.base import Base, BaseSession
from simba_sdk.sessions.vc import VC, VCSession


@dataclass
class DID(Base):
    name: str
    permission: str
    alias: str
    seed: str
    field_context: List[str] = ""
    did: str = ""
    register_status: str = ""
    revoke_status: str = ""
    owner: str = ""
    domain: str = ""
    trust_profile: str = ""
    nickname: str = ""
    public_name: str = ""


class DIDSession(BaseSession):
    domain: str
    did: DID

    def __init__(self, did_id: str, **kwargs: str) -> None:
        """
        For kwargs see BaseSession.__init__
        """
        super().__init__(**kwargs)
        self._clients = {
            "credential": CredentialClient,
            "resource": ResourceClient,
        }
        self.did_id = did_id

    async def __aenter__(self) -> "DIDSession":
        await super().__aenter__()
        did = await self._clients["credential"].get_did(
            self.did_id, domain_name=self.domain
        )
        did_dict = dict(did.did_document.model_dump(), **did.metadata.model_dump())
        did_dict["did"] = did.did_document.id
        self.did = DID.from_dict(did_dict)
        self.trust_config = did_dict["trust_config"]
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.did = None

    async def update_did(
        self, tags: Optional[dict] = None, name: Optional[str] = None
    ) -> None:
        """
        For updating DID metadata, update the Session's DID object directly before calling this method with no arguments.
        """
        did_update = {"tags": tags, "name": name}
        await self._clients["credential"].update_did(
            domain_name=self.domain,
            did_id=self.did_id,
            updatedidmetadatafromuser=UpdateDIDMetadataFromUser(**did_update),
        )

    async def delete_did(self):
        await self._clients["credential"].revoke_did(
            domain_name=self.domain, did_id=self.did_id
        )
        await self.__aexit__(None, None, None)

    @parse(VC)
    async def create_vc(self, vc: VC):
        create_vc_http = CreateVCHttp(
            id=vc.id,
            field_context=vc.context,
            issuer=vc.issuer,
            valid_from=vc.valid_from,
            valid_until=vc.valid_until,
            material=vc.material,
            subject=vc.subject,
            claims=vc.claims,
        )
        vc_id = await self._clients["credential"].create_vc(
            domain_name=self.domain, createvchttp=create_vc_http
        )
        session = VCSession(vc_id=vc_id, settings=self.settings)
        session.domain = self.domain

        return session
