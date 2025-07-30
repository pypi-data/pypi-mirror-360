from dataclasses import dataclass, field

from bestsms.api.reports.dtos.sms_message_in_dto import SMSMessageInDTO
from bestsms.helpers.functions import Functions


@dataclass
class SMSReceivedDTO:
    Result: str = None
    TotalRecords: int = 0
    RecordsPerPage: int = 0
    PageCount: int = 1
    Page: int = 1
    Messages: list[SMSMessageInDTO] = field(default_factory=list)

    def __repr__(self):
        return Functions.__pretty_class__(self, self)