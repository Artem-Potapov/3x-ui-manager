import base_model
import pydantic
from types import NoneType
from typing import Union, Optional, TypeAlias

timestamp: TypeAlias = int
ip_address: TypeAlias = str
json_string: TypeAlias = str

class InboundStats(base_model.BaseModel):
    id: int
    inboundId: int
    enable: bool
    email: str
    uuid: str
    subId: str
    up: int    # bytes
    down: int  # bytes
    allTime: int # bytes
    expiryTime: timestamp  # UNIX timestamp
    total: int
    reset: int
    lastOnline: timestamp


class Inbound(base_model.BaseModel):
    id: int
    up: int # bytes
    down: int # bytes
    total: int # bytes
    allTime: int # bytes
    remark: str
    enable: bool
    expiryTime: timestamp # UNIX timestamp
    trafficReset: str # "Never", "Weekly", "Monthly", "Daily"
    lastTrafficResetTime: timestamp # UNIX timestamp
    clientStats: list[InboundStats]
    listen: str
    port: int
    protocol: str # "vless", "vmess", "trojan", etc.
    settings: json_string # JSON packed value, stringified
    streamSettings: json_string # JSON packed value, stringified
    tag: str
    sniffing: json_string # JSON packed value, stringified
