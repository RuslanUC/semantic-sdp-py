from __future__ import annotations

from dataclasses import dataclass

from semanticsdp import BaseSdp


@dataclass(slots=True, eq=True)
class DatachannelInfo(BaseSdp):
    port: int
    max_message_size: int
