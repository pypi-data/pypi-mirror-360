from dataclasses import dataclass
from typing import Union

from simba_sdk.core.requests.client.operator import schemas as operator_schemas


@dataclass
class GetSeeRequestsQuery:
    page: int
    size: int
    template: Union[str, None] = None
    user: Union[str, None] = None
    status: Union[operator_schemas.SEEState, None] = None
    requested_state: Union[operator_schemas.SeeRequestedState, None] = None
    order_by: Union[str, None] = None


@dataclass
class UpdateSeeRequestsQuery:
    see_request_id: str
