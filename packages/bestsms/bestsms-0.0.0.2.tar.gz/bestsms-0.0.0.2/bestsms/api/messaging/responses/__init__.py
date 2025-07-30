""" Reference to bestsms.base.get.message_result.MessageResult """
def MessageApiResult(**kwargs):
    
    from bestsms.api.messaging.responses.message_api_result import MessageApiResult as process

    response = process(**kwargs)

    return response.Data