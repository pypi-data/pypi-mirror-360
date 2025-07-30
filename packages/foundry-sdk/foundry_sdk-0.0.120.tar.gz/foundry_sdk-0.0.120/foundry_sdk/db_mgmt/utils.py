from enum import Enum

class InsertionMode(Enum):
    IGNORE = "IGNORE"
    RAISE = "RAISE"
    UPDATE = "UPDATE"
    INSERT_MISSING = "INSERT_MISSING"


class InsertionModeFactory:
    @staticmethod
    def build(insertion_mode: str) -> InsertionMode:
        """
        Build InsertionMode object from string
        """
        insertion_mode = insertion_mode.upper()
        return InsertionMode[insertion_mode]


