""" Reference to bestsms.base.get.status_request_result.StatusRequestResult """
def StatusRequestResult(**kwargs):

    from bestsms.api.reports.responses.status_request_result import StatusRequestResult as run

    response = run(**kwargs)

    return response.Data

""" Reference to bestsms.base.get.sms_reply_result.SMSReceivedResult """
def SMSReplyResult(**kwargs):

    from bestsms.api.reports.responses.sms_reply_result import SMSReplyResult as run

    response = run(**kwargs)

    return response.Data

""" Reference to bestsms.base.get.sms_received_result.SMSReceivedResult """
def SMSReceivedResult(**kwargs):

    from  bestsms.api.reports.responses.sms_received_result import SMSReceivedResult as run

    response = run(**kwargs)

    return response.Data