import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Union

from simba_sdk.core.requests.client.credential.client import CredentialClient
from simba_sdk.core.requests.client.resource.client import ResourceClient
from simba_sdk.core.requests.client.resource.schemas import TokenStatus
from simba_sdk.sessions.base import Base, BaseSession


@dataclass
class VP(Base):
    proof: Dict[str, str] = field(default_factory=dict)
    type: List[str] = "VerifiablePresentation"
    material: Dict[str, Union[int, str]] = field(default_factory=dict)
    digest: str = ""
    verification_key: str = "#1"
    id: str = field(default_factory=lambda: f"urn:uuid:{uuid.uuid4()}")


class VPSession(BaseSession):
    vp: VP
    vc: dict
    domain: str

    def __init__(self, vp_id: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._clients = {
            "credential": CredentialClient,
            "resource": ResourceClient,
        }
        self.vp_id = vp_id

    async def __aenter__(self) -> "VPSession":
        await super().__aenter__()
        # Get VP
        vp = await self._clients["credential"].get_vp(
            vp_id=self.vp_id, domain_name=self.domain
        )
        vp_dict = vp.vp
        vp_dict["digest"] = (vp.metadata.digest if vp.metadata.digest else "",)
        vp_dict["material"] = vp.metadata.material
        self.vc = vp.vp["verifiableCredential"]
        self.vp = VP.from_dict(vp_dict)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.vp = None

    async def verify_vp(self):
        vp_dict = {
            "@context": self.vc[0]["@context"],
            "verifiableCredential": self.vc,
            "id": self.vp.id,
            "proof": self.vp.proof,
            "type": self.vp.type,
        }
        resp = await self._clients["credential"].verify_vp(body=json.dumps(vp_dict))
        if resp.error:
            raise Exception(resp.error)
        return resp.success

    async def request_access(self, resource_id: str, wait_for_active: bool = True):
        vp_data = json.dumps(
            {
                "@context": self.vc[0]["@context"],
                "proof": self.vp.proof,
                "type": ["VerifiablePresentation"],
                "verifiableCredential": self.vc,
                "id": self.vp.id,
            }
        )
        print("Requesting Token")
        resource_token = await self._clients["resource"].request_access(
            resource_id=resource_id, body=vp_data
        )
        token_value = resource_token.value
        if wait_for_active:
            time_elapsed = 0
            active = False
            await asyncio.sleep(2)
            while not active:
                if time_elapsed >= self.settings.timeout:
                    raise Exception("Token took too long to activate")
                now = time.time()
                try:
                    resource_token = await self._clients["resource"].get_token(
                        token_value
                    )
                    active = resource_token.status == TokenStatus.ACTIVE
                    if active:
                        print("Token active")
                        return token_value
                except Exception as e:
                    await asyncio.sleep(2)
                    # For some reason tokens take a while to show up
                    if "not valid" not in str(e):
                        raise e
                await asyncio.sleep(2)
                time_elapsed += time.time() - now
            print("Token did not activate")
            raise Exception("Token did not activate")
