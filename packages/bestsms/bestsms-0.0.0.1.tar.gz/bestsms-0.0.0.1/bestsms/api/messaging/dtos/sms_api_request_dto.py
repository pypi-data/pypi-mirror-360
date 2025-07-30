from dataclasses import dataclass, field

from bestsms.api.messaging.dtos.common_api_request_dto import CommonApiRequestDTO
from bestsms.helpers.functions import Functions

@dataclass
class SMSApiRequestDTO(CommonApiRequestDTO):
    FromNumber: str = None
    SMSEmailReply: str = None
    CharacterConversion: bool = False
    Message: str = None
    Files: list[str] = field(default_factory=list)

    def __repr__(self):
        return Functions.__pretty_class__(self, self)
