from enum import Enum
from enum import Enum


class WorkStatus(Enum):
    NOT_SUBMITTED = 0
    NOT_SUBMITTED_RED = 1
    CORRECTED = 2
    CORRECTED_GREEN = 3

    def __str__(self):
        if self == WorkStatus.NOT_SUBMITTED:
            return "未提交"
        elif self == WorkStatus.NOT_SUBMITTED_RED:
            return "[red]未提交[/red]"
        elif self == WorkStatus.CORRECTED:
            return "已批改"
        elif self == WorkStatus.CORRECTED_GREEN:
            return "[green]已批改[/green]"
