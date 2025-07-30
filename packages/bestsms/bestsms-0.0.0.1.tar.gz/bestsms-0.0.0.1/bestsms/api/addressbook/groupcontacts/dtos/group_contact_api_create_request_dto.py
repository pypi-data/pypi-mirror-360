from dataclasses import dataclass, field

from bestsms.helpers.functions import Functions


@dataclass
class GroupContactApiCreateRequestDTO:
    
    ContactID: str = None

    def __repr__(self):
        return Functions.__pretty_class__(self, self)