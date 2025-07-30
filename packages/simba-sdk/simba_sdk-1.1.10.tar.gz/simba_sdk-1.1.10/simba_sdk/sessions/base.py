from dataclasses import dataclass, fields, is_dataclass
from typing import Any

from typeguard import TypeCheckError, check_type
from typing_extensions import Dict, List, Optional, Self, Type, Union

from simba_sdk.config import Settings
from simba_sdk.core.requests.auth.token_store import InMemoryTokenStore
from simba_sdk.core.requests.client.base import Client


def get_origin_and_args(tp):
    """Helper to extract __origin__ and __args__ from a typing type."""
    return getattr(tp, "__origin__", None), getattr(tp, "__args__", ())


def process_type(value: Any, field_type: Type) -> Any:
    """
    Cast `value` to `field_type`, recursively processing nested types.
    """
    origin, args = get_origin_and_args(field_type)

    # Handle Union (e.g. Union[str, None] or Optional[str])
    field_types = args if origin is Union else [field_type]

    last_error = None
    for i, candidate_type in enumerate(field_types):
        try:
            try:
                return check_type(value, candidate_type)
            except TypeCheckError:
                pass  # Proceed to deeper conversion attempts

            # Handle List[T]
            candidate_origin, candidate_args = get_origin_and_args(candidate_type)
            if candidate_origin is list and isinstance(value, list):
                inner_type = candidate_args[0]
                return [process_type(v, inner_type) for v in value]

            # Handle Dict[K, V]
            if candidate_origin is dict and isinstance(value, dict):
                key_type, val_type = candidate_args
                return {
                    process_type(k, key_type): process_type(v, val_type)
                    for k, v in value.items()
                }

            # Handle dataclasses
            if is_dataclass(candidate_type):
                if isinstance(value, candidate_type):
                    return value
                elif isinstance(value, dict):
                    if hasattr(candidate_type, "from_dict"):
                        return candidate_type.from_dict(value)
                    return candidate_type(**value)

            # Fallback: try direct cast
            return candidate_type(value)

        except Exception as e:
            last_error = e
            if i < len(field_types) - 1:
                continue
            break

    raise TypeError(
        f"Could not convert input of type {type(value)} to expected type {field_type}: {last_error}"
    )


@dataclass
class Base:
    @classmethod
    def from_dict(cls, kwargs: Dict[str, str]):
        """
        Use this method instead of __init__ to ignore extra args
        """
        cls_dict = {}
        for field in fields(cls):
            if field.name not in kwargs:
                continue
            value = kwargs.get(field.name)
            try:
                cls_dict[field.name] = process_type(value, field.type)
            except Exception as e:
                # Flag the field that is failing
                raise TypeError(
                    f"Failed to parse field '{field.name}' of type {field.type} with value {value}: {e}"
                )

        return cls(**cls_dict)


class BaseSession:
    def __init__(
        self,
        settings: Optional[Settings] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        **kwargs: str,
    ) -> None:
        if settings is None:
            self.client_id = client_id
            self.client_secret = client_secret
            if client_id:
                kwargs["client_id"] = client_id
            if client_secret:
                kwargs["client_secret"] = client_secret
            self.settings = Settings(**kwargs)
        else:
            self.settings = settings
        self._store = InMemoryTokenStore()
        self._clients: Dict[str, Union[Type[Client], Client]] = {}

    async def initialise_clients(self):
        for service, client in self._clients.items():
            self._clients[service] = client(
                name=service,
                settings=self.settings,
                token_store=self._store,
            )

    async def __aenter__(self) -> Self:
        self._registry: List[BaseSession] = []
        await self.initialise_clients()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._clients = None
        for child in self._registry:
            await child.__aexit__(exc_type, exc_val, exc_tb)
        self._registry = []
