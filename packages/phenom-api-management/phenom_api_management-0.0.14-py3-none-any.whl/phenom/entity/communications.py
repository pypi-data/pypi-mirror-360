from phenom.api.communicationssms.sms_communications_api import SMSCommunicationsApi
from phenom.api.communicationsemail.email_communications_api import EmailCommunicationsApi
from phenom.api.communicationsemail.forward_profile_api import ForwardProfileApi

class Communications(object):
    def __init__(self, token, gateway_url, apikey=None):
        self.__token = token
        self.__gateway_url = gateway_url
        self.__apikey = apikey

    def sms_communications_api(self):
        return SMSCommunicationsApi(self.__token, self.__gateway_url, self.__apikey)

    def email_communications_api(self):
        return EmailCommunicationsApi(self.__token, self.__gateway_url, self.__apikey)

    def forward_profile_api(self):
        return ForwardProfileApi(self.__token, self.__gateway_url, self.__apikey)