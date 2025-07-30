import asyncio
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import IO, Dict, List, Optional

from simba_sdk.core.requests.client.resource.client import ResourceClient
from simba_sdk.core.requests.client.resource.queries import GetBundlesQuery
from simba_sdk.core.requests.client.resource.schemas import (
    Account,
    Action,
    Policy,
    PublicationRequest,
)
from simba_sdk.core.requests.exception import RequestException
from simba_sdk.sessions.base import Base, BaseSession


@dataclass
class Storage(Base):
    name: str
    type: str
    config: Optional[Dict] = None


@dataclass
class Resource(Base):
    name: str
    storage: str
    bundle_id: str = ""
    container: str = ""
    published: bool = False
    private: bool = False
    policies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class ResourceSession(BaseSession):
    resource_id: str
    domain: str

    def __init__(self, resource_id: str, **kwargs):
        super().__init__(**kwargs)
        self._clients = {
            "resource": ResourceClient,
        }
        self.resource_id = resource_id

    async def __aenter__(self):
        await super().__aenter__()
        query = GetBundlesQuery(page=1, size=100)
        resources_resp = await self._clients["resource"].get_bundles(
            query_arguments=query, domain_name=self.domain
        )
        for bundle in resources_resp.items:
            if bundle.resource_id == self.resource_id:
                resource = Resource.from_dict(
                    {
                        "bundle_id": bundle.id.hex,
                        "name": bundle.name,
                        "container": bundle.container,
                        "published": bundle.published,
                        "private": bundle.private,
                        "storage": bundle.storage,
                        "policies": bundle.policies,
                    }
                )
                self.resource = resource
                return self
        raise Exception(f"Resource {self.resource_id} not found")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.resource = None

    async def _await_task(self, task_id: str, domain: str):
        timeout = 500
        time_taken = 0
        while time_taken < timeout:
            now = time.time()
            task = await self._clients["resource"].get_task(
                uid=self.resource.bundle_id, task_id=task_id, domain_name=domain
            )
            if task.status == "FAILED":
                raise Exception(f"Task failed.\n{task.error_details}")
            if task.status == "COMPLETED":
                return task
            else:
                await asyncio.sleep(5)
                time_taken += time.time() - now
        raise Exception(f"Timeout waiting for task.\n{task.status}")

    async def publish(self, public_key: str, alias: str):
        publicationrequest = PublicationRequest(
            action=Action("publish"),
            account=Account(public_key=public_key, alias=alias),
            clear_draft=False,
        )
        task = await self._clients["resource"].publish_action(
            uid=self.resource.bundle_id,
            domain_name=self.domain,
            publicationrequest=publicationrequest,
        )
        await self._await_task(task_id=task.id.hex, domain=self.domain)

    async def add_policy(
        self,
        identifier: str,
        criteria: List[Dict[str, str]],
        junction: str = "AND",
        dataType: str = "STR",
    ):
        new_policy = Policy(
            identifier=identifier,
            junction=junction,
            dataType=dataType,
            criteria=criteria,
        )
        # Add access policy to bundle for comparison to VPs later.
        _ = await self._clients["resource"].add_policy(
            uid=self.resource.bundle_id, policy=new_policy, domain_name=self.domain
        )

    async def upload(self, stream: Optional[IO] = None, url: Optional[str] = None):
        if stream is None and url is None:
            raise Exception("Either stream or url must be provided")
        if stream is None:
            task = await self._clients["resource"].upload_files(
                file_url=url, uid=self.resource.bundle_id, domain_name=self.domain
            )
            await self._await_task(task.id, domain=self.domain)
        if url is None:
            filename = f"./tmp_{uuid.uuid4().hex}"
            with open(filename, "wb") as f:
                stream.seek(0)
                f.write(stream.read())
            task = await self._clients["resource"].upload_files(
                file_url=filename, uid=self.resource.bundle_id, domain_name=self.domain
            )
            await self._await_task(task.id, domain=self.domain)
            os.remove(filename)

    async def download(self, token: str, out_stream: IO):
        pending = True
        time_elapsed = 0
        while pending:
            now = time.time()
            if time_elapsed > self.settings.timeout:
                raise Exception("Waited too long to access resource")
            try:
                byte_resp = await self._clients["resource"].get_access(token=token)
                out_stream.write(byte_resp)
                pending = False
            except RequestException as e:
                if "PENDING" not in str(e):
                    raise e
                time_elapsed += time.time() - now
