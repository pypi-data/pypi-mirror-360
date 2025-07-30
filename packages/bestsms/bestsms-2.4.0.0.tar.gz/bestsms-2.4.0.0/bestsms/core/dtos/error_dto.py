from dataclasses import dataclass, field

from bestsms.helpers.functions import Functions


@dataclass
class ErrorDTO:
    Result: str = "Failed"
    ErrorMessage: list[str] = field(default_factory=list)

    def __repr__(self):
        return Functions.__pretty_class__(self, self)