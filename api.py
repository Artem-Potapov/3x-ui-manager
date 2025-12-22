import asyncio
import datetime
import json
import logging
import subprocess
from collections.abc import Sequence, Mapping
from typing import Self, Optional, Dict, Iterable, AsyncIterable, TypeAlias, Type, Union, Any, List, Tuple

import httpx
from httpx import Response, AsyncClient
from requests import session

import util
from util import JsonType

DataType: Type[str|bytes|Iterable[bytes]|AsyncIterable[bytes]] = Union[str, bytes, Iterable[bytes], AsyncIterable[bytes]]
PrimitiveData = Optional[Union[str, int, float, bool]]
ParamType = Union[
    Mapping[str, Union[PrimitiveData, Sequence[PrimitiveData]]],
    List[Tuple[str, PrimitiveData]],
    Tuple[Tuple[str, PrimitiveData], ...],
    str,
    bytes,
]
CookieType = Union[Dict[str, str], List[Tuple[str, str]]]
HeaderType = Union[
    Mapping[str, str],
    Mapping[bytes, bytes],
    Sequence[Tuple[str, str]],
    Sequence[Tuple[bytes, bytes]],
]


class XUIClient:
    _instance = None

    def __init__(self, base_host:str, base_port: int, base_path: str,
                 *, xui_username: str|None=None, xui_password: str|None=None,
                 two_fac_code: str|None=None, session_duration: int=3600) -> None:
        self.session: AsyncClient | None = None
        self.base_host: str = base_host
        self.base_port: int = base_port
        self.base_path: str = base_path
        self.base_url: str = f"https://{self.base_host}:{self.base_port}/{self.base_path}"
        self.session_start: float|None = None
        self.session_duration: int = session_duration
        self.xui_username: str|None = xui_username
        self.xui_password: str|None = xui_password
        self.two_fac_code: str|None = two_fac_code
        self.max_retries: int = 5
        self.retry_delay: int = 1

    def __new__(cls, *args, **kwargs):
        print("initializing client")
        if cls._instance is None:
            print("nu instance")
            cls._instance = super(XUIClient, cls).__new__(cls)
        return cls._instance


    async def safe_get(self,
                       url: httpx.URL | str,
                       *,
                       params: ParamType | None = None,
                       headers: HeaderType | None = None,
                       cookies: CookieType | None = None) -> Response:
        if self.session is None:
            raise RuntimeError("Session is not initialized")

        for attempt in range(self.max_retries):
            resp = await self.session.get(url=url, params=params, headers=headers, cookies=cookies)
            if resp.status_code != 200:
                if resp.status_code == 404:
                    now: float = datetime.datetime.now().timestamp()
                    if self.session_start is None or now - self.session_start > self.session_duration:
                        await self.login()
                        continue
                raise RuntimeError(f"Server returned status code {resp.status_code}")

            status = util.check_xui_response_validity(resp)
            if status == "OK":
                return resp
            if status == "DB_LOCKED":
                if attempt + 1 >= self.max_retries:
                    raise RuntimeError("Database locked: max retries exceeded")
                await asyncio.sleep(self.retry_delay)
                continue


            raise RuntimeError(f"Unexpected response validity status: {status}")

    async def safe_post(self,
                        url: httpx.URL | str,
                        *,
                        content: DataType | None = None,
                        data: JsonType | None = None,
                        json: Any | None = None,
                        params: ParamType | None = None,
                        headers: HeaderType | None = None,
                        cookies: CookieType | None = None) -> Response:
        if self.session is None:
            raise RuntimeError("Session is not initialized")

        for attempt in range(self.max_retries):
            resp = await self.session.post(url=url, content=content, data=data, json=json,
                                           params=params, headers=headers, cookies=cookies)
            if resp.status_code != 200:
                if resp.status_code == 404:
                    now: float = datetime.datetime.now().timestamp()
                    if self.session_start is None or now - self.session_start > self.session_duration:
                        await self.login()
                        continue
                raise RuntimeError(f"Server returned status code {resp.status_code}")

            status = util.check_xui_response_validity(resp)
            if status == "OK":
                return resp
            if status == "DB_LOCKED":
                if attempt + 1 >= self.max_retries:
                    raise RuntimeError("Database locked: max retries exceeded")
                await asyncio.sleep(self.retry_delay)
                continue

            raise RuntimeError(f"Unexpected response validity status: {status}")

    async def login(self, username: str|None = None, password: str|None = None,
                    two_fac_code: str|None = None) -> None:
        if self.xui_username and username:
            raise ValueError("You must provide a username either when initing XUI or to the function, not both")
        if self.xui_password and password:
            raise ValueError("You must provide a password either when initing XUI or to the function, not both")
        if self.two_fac_code and two_fac_code:
            raise ValueError("You must provide a 2fa code either when initing XUI or to the function, not both")

        payload = {
            "username": username,
            "password": password,
        }
        if two_fac_code is not None:
            payload["twoFactorCode"] = two_fac_code

        resp = await self.session.post("/login", data=payload)
        resp_json = resp.json()
        if resp.status_code == 200:
            if resp_json["success"]:
                self.session_start: float = (datetime.datetime.now().timestamp())
                return
            else:
                raise ValueError("Error: wrong credentials or failed login")
        else:
            raise RuntimeError(f"Error: server returned a status code of {resp.status_code}")

    def connect(self) -> None:
        self.session = AsyncClient(base_url=self.base_url)

    async def disconnect(self):
        await self.session.aclose()

    async def __aenter__(self) -> Self:
        self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.disconnect()
        return

a = XUIClient("12", 12, "23")
print(a)
print(a.__dict__)
b = XUIClient("12", 12, "34")
print(b)
print(b.__dict__)
