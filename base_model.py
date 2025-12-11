import asyncio
import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union, overload, Self

import pydantic
import httpx
from functools import cached_property

import util

if TYPE_CHECKING:
    from .api import XUIClient

class BaseModel(pydantic.BaseModel):
    ERROR_RETRIES = 5
    ERROR_RETRY_COOLDOWN = 1
    if TYPE_CHECKING:
        client: XUIClient
    else:
        client: Any

    class ConfigDict:
        keep_untouched = (cached_property,)  # type: ignore

    @classmethod
    def from_list(cls, args: List[Dict[str, Any]],
                  client: "XUIClient"
                  ) -> List[Self]:
        return [cls(**obj, xui_client=client) for obj in args]

    @classmethod
    async def from_response(
            cls,
            response: httpx.Response,
            client: "XUIClient",
            expect: list|dict
    ) -> Union[Self, List[Self]]:
        """If you want to make out a list or dict, please pass an example"""


        json_resp: util.JsonType = response.json()
        valid = util.check_xui_response_validity(json_resp)
        if valid == "OK":
            obj = json_resp["obj"]
            if expect is list:
                return cls.from_list(obj, client=client)
            if expect is dict:
                return cls(**obj, client=client)
        else:
            raise ValueError(f"Invalid 3X-UI response, code {valid}")
