import json
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from simba_sdk.core.requests.client.credential.client import CredentialClient
from simba_sdk.core.requests.client.credential.queries import AcceptVcQuery
from simba_sdk.core.requests.client.credential.schemas import CreateVPHttp
from simba_sdk.core.requests.client.resource.client import ResourceClient
from simba_sdk.sessions import parse
from simba_sdk.sessions.base import Base, BaseSession
from simba_sdk.sessions.vp import VP, VPSession


@dataclass
class VC(Base):
    context: List[str]
    issuer: str
    material: Optional[Dict[str, str]] = None
    claims: Dict[str, dict] = field(default_factory=dict)
    proof: Dict[str, str] = field(default_factory=dict)
    id: str = field(default_factory=lambda: f"urn:uuid:{uuid.uuid4()}")
    subject: str = ""
    status: str = ""
    valid_from: str = ""
    valid_until: str = ""


class VCSession(BaseSession):
    vc: VC
    domain: str

    def __init__(self, vc_id: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._clients = {
            "credential": CredentialClient,
            "resource": ResourceClient,
        }
        self.vc_id = vc_id

    async def __aenter__(self) -> "VCSession":
        await super().__aenter__()
        vc = await self._clients["credential"].get_vc(
            vc_id=self.vc_id, domain_name=self.domain
        )
        vc_dict = {
            "id": vc.vc["id"],
            "context": vc.vc["@context"],
            "material": vc.metadata.material,
            "issuer": vc.vc["issuer"],
            "claims": {vc.vc["@context"][0]: vc.vc["credentialSubject"]},
            "proof": vc.vc["proof"],
            "subject": vc.vc["credentialSubject"].pop("id"),
            "status": vc.metadata.status,
            "valid_from": vc.vc["validFrom"],
            "valid_until": vc.vc["validUntil"],
        }
        self.vc = VC.from_dict(vc_dict)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.vc = None

    async def accept_vc(self, accept=True):
        """
        Pass accept=False to reject VC
        """
        query = AcceptVcQuery(accept=accept)
        await self._clients["credential"].accept_vc(
            query_arguments=query, vc_id=self.vc_id, domain_name=self.domain
        )

    async def verify_vc(self):
        vc_dict = {
            "@context": self.vc.context,
            "id": self.vc.id,
            "issuer": self.vc.issuer,
            "proof": self.vc.proof,
            "validFrom": self.vc.valid_from,
            "validUntil": self.vc.valid_until,
            "type": [
                "VerifiableCredential",
            ],
            "credentialSubject": dict(
                {
                    "id": self.vc.subject,
                },
                **self.vc.claims[self.vc.context[0]],
            ),
        }
        resp = await self._clients["credential"].verify_vc(body=json.dumps(vc_dict))
        if resp.error:
            raise Exception(resp.error)
        return resp.success

    @parse(VP)
    async def create_vp(self, vp: VP):
        create_vp_http = CreateVPHttp(
            vc_id=self.vc_id,
            proof_type=vp.proof["type"],
            material=vp.material,
            verification_key=vp.verification_key,
        )
        vp_id = await self._clients["credential"].create_vp(
            domain_name=self.domain, createvphttp=create_vp_http
        )
        session = VPSession(vp_id=vp_id, settings=self.settings)
        session.domain = self.domain
        return session
