from dataclasses import asdict
from typing import Any, Dict

import pydantic_core
from pydantic import BaseModel

from simba_sdk.core.requests.client.base import Client
from simba_sdk.core.requests.client.operator import queries as operator_queries
from simba_sdk.core.requests.client.operator import schemas as operator_schemas
from simba_sdk.core.requests.exception import EnsureException


class OperatorClient(Client):
    """
    This client is used as a context manager to interact with one of the SIMBAChain service APIs.
    e.g.
    ```
    my_dids: List[DidResponse] = await credential_client.dids_get_dids()
    ```
    Clients are generated with methods that have a 1:1 relationship with endpoints on the service's API. You can find the models from the api in ./schemas.py
    and query models in ./queries.py
    """

    async def _get_subscriptions(
        self,
    ) -> None:
        """ """

        path_params: Dict[str, Any] = {}
        await self.get("/dapr/subscribe/", params=path_params)

        return

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

    async def get_see_requests(
        self,
        query_arguments: operator_queries.GetSeeRequestsQuery,
    ) -> operator_schemas.PageSeeRequestPublic:
        """
                List container requests

        Returns a list of known container requests.
        """

        # get rid of items where None
        query_params = {
            k: v for k, v in asdict(query_arguments).items() if v is not None
        }

        path_params: Dict[str, Any] = {}
        resp = await self.get("/v1/see/", params=path_params | query_params)

        try:
            resp_model = operator_schemas.PageSeeRequestPublic.model_validate(
                resp.json()
            )
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def create_see_requests(
        self,
        seerequestcreate: operator_schemas.SeeRequestCreate,
    ) -> str:
        """
                Create container requests

        Creates a new container request for the given input
        """

        path_params: Dict[str, Any] = {}
        resp = await self.post(
            "/v1/see/",
            data=str(seerequestcreate)
            if not issubclass(type(seerequestcreate), BaseModel)
            else seerequestcreate.model_dump_json(),  # type: ignore
            params=path_params,
        )

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def get_see_requests_by_id(
        self,
        see_request_id: str,
    ) -> operator_schemas.SeeRequestPublic:
        """
                Get container requests

        Returns a container requests for the given ID.
        """

        path_params: Dict[str, Any] = {
            "see_request_id": see_request_id,
        }
        resp = await self.get(f"/v1/see/{see_request_id}", params=path_params)

        try:
            resp_model = operator_schemas.SeeRequestPublic.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(
                f"The response came back in an unexpected format: {resp.text}"
            )
        return resp_model

    async def delete_see_requests(
        self,
        see_request_id: str,
    ) -> str:
        """
                Delete container requests

        Deletes a container requests with the given ID
        """

        path_params: Dict[str, Any] = {
            "see_request_id": see_request_id,
        }
        resp = await self.delete(f"/v1/see/{see_request_id}", params=path_params)

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def update_see_requests(
        self,
        query_arguments: operator_queries.UpdateSeeRequestsQuery,
        seerequestupdate: operator_schemas.SeeRequestUpdate,
    ) -> str:
        """
                Update container requests

        Updates an existing container request with the given input
        """

        # get rid of items where None
        query_params = {
            k: v for k, v in asdict(query_arguments).items() if v is not None
        }

        path_params: Dict[str, Any] = {}
        resp = await self.put(
            "/v1/see/{see_requests_id}",
            data=str(seerequestupdate)
            if not issubclass(type(seerequestupdate), BaseModel)
            else seerequestupdate.model_dump_json(),  # type: ignore
            params=path_params | query_params,
        )

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def version(
        self,
    ) -> str:
        """ """

        path_params: Dict[str, Any] = {}
        resp = await self.get("/v1/version/", params=path_params)

        resp_model = str(resp.json())  # type: ignore
        return resp_model

    async def job_request_status_event_handler(
        self,
        cloudeventmodeljobrequeststatusevent: operator_schemas.CloudEventModelJobRequestStatusEvent,
    ) -> None:
        """ """

        path_params: Dict[str, Any] = {}
        await self.post(
            "/events/simba-operator-pubsub/simba.operator.job_request_status/",
            data=str(cloudeventmodeljobrequeststatusevent)
            if not issubclass(type(cloudeventmodeljobrequeststatusevent), BaseModel)
            else cloudeventmodeljobrequeststatusevent.model_dump_json(),  # type: ignore
            params=path_params,
        )

        return
