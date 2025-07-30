from dataclasses import dataclass, field

from bestsms.api.reports.dtos.sms_reply_recipient_reply_dto import SMSReplyRecipientReplyDTO
from bestsms.api.reports.dtos.recipient_dto import RecipientDTO

from bestsms.helpers.functions import Functions


@dataclass
class SMSReplyRecipientDTO(RecipientDTO):
    MessageText: str = None
    SMSReplies: list[SMSReplyRecipientReplyDTO] = field(default_factory=list)

    def __repr__(self):
        return Functions.__pretty_class__(self, self)