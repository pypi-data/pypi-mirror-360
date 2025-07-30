from dataclasses import dataclass, field

from bestsms.api.addressbook.groups.dtos.group_model import GroupModel
from bestsms.helpers.functions import Functions

@dataclass
class GroupApiResultDTO:
    
    Result: str = None
    Group: GroupModel = None
    ErrorMessage: list[str] = field(default_factory=list)

    def __repr__(self):
        return Functions.__pretty_class__(self, self)