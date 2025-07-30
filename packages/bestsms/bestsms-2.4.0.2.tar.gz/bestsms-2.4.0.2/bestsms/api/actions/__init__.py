from bestsms import _config

class BestSMS():

    def __init__(self, **kwargs):
        for key, value in kwargs.items():

            if key == "AuthToken":
                self.AuthToken = _config.__AuthToken__ = value
                _config.__APIHeaders__["Authorization"] = f"Basic {self.AuthToken}"

            if key == "Sender":
                self.Sender = _config.__Sender__ = value

            if key == "APIKey":
                self.APIKey = _config.__APIKey__ = value

        self._messaging = None
        self._reports = None
        self._actions = None
        self._addressbook = None

    #
    # Renamed since v2.3.0.0
    #

    @property
    def Messaging(self, **kwargs):
        
        """ bestsms.messaging.__init__.py - Messaging() """

        if self._messaging == None:
            from bestsms.api.messaging.requests import Messaging

            self._messaging = Messaging(**kwargs)

        return self._messaging
    
    @property
    def Reports(self, **kwargs):
    
        """ bestsms.reports._reference.py - Reference() """
        
        if self._reports == None:
            from bestsms.api.reports.requests import Reports
            self._reports = Reports(**kwargs)
    
        return self._reports
    
    @property
    def Actions(self, **kwargs):

        """ bestsms.actions._reference.py - Reference() """

        if self._actions == None:
            from bestsms.api.actions.requests import Actions
            self._actions = Actions(**kwargs)
    
        return self._actions
    
    @property
    def Addressbook(self, **kwargs):
        
        if self._addressbook == None:
            from bestsms.api.addressbook import Addressbook
            self._addressbook = Addressbook(**kwargs)

        return self._addressbook