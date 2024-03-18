import sys

DATACLASS_KWARGS = {"slots": True} if sys.version_info.minor >= 10 or sys.version_info.major > 3 else {}
