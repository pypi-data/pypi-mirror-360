import dataclasses
from typing import Optional, Union

AcceptableTypes = Union[
    str,
    dict,
    object,
]


class Response:
    """Return a Response object from a route handler for more control
    """
    def __init__(self,
                 content: AcceptableTypes,
                 status: int = 200,
                 headers: Optional[dict[str, Optional[str]]] = None):
        self.content = content
        self.status = status
        self.headers = headers or {}
