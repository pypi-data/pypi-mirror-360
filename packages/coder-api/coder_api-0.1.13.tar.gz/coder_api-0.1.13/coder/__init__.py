from typing import Optional

from typing_extensions import Literal

from .core import Organization, Template, User, Workspace  # noqa

api_domain: str = None
token: str = None


def set_token(value: str):
    global token
    token = value


# Set to either 'debug' or 'info', controls console logging
log: Optional[Literal["debug", "info"]] = None
