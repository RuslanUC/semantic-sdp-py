from __future__ import annotations

from dataclasses import dataclass

from semanticsdp import BaseSdp
from semanticsdp._dataclass_fix import DATACLASS_KWARGS


@dataclass(**DATACLASS_KWARGS)
class DatachannelInfo(BaseSdp):
    port: int
    max_message_size: int
