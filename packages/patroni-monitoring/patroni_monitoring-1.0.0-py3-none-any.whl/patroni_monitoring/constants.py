from enum import Enum

class Status(Enum):
    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3