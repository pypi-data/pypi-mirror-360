class Messaging(object):

    def __init__(self):
        self._sms = None
    
    @property
    def SMS(self,**kwargs):

        from bestsms.api.messaging.requests.sms_api import SMSApi

        if self._sms != None:
            del(self._sms)
            
        self._sms = SMSApi(kwargs)

        return self._sms
