from typing import Dict, Type

from pydantic_settings import BaseSettings

from simba_sdk.core.requests.middleware.manager import BaseMiddleware
from simba_sdk.core.requests.middleware.trailing_slash import (
    UrlAppendTrailingSlashHandler,
)

MIDDLEWARE: Dict[str, Type[BaseMiddleware]] = {
    "trailing_slash": UrlAppendTrailingSlashHandler
}


class Settings(BaseSettings):
    """
    client_id: str - Client ID from Client Credentials
    client_secret: str - Client Secret from Client Credentials
    base_url: str - Base URL template. A string template that can be formatted to form a service URL.
    token_url: str - The url you can get an oauth token from. Likely ends in /oauth/token/.
    timeout: int - how long the sdk should wait for responses from a client request.
    """

    client_id: str
    client_secret: str
    token_url: str
    base_url: str
    timeout: int = 500

    model_config = {"extra": "ignore"}
