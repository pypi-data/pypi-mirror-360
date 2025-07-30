""" Reference to bestsms.base.set.set_request_result.ActionResult """
def ActionApiResult(**kwargs):

    from bestsms.api.actions.responses.action_api_result import ActionApiResult as process

    result = process(**kwargs)

    return result.Data