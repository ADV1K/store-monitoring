from enum import Enum, StrEnum, auto


class StoreStatusEnum(StrEnum):
    active = auto()
    inactive = auto()


class DayOfWeekEnum(Enum):
    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5
    sunday = 6
