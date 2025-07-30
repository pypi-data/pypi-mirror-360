from phenom.api.apply.attachments_api import AttachmentsApi
from phenom.api.apply.applications_api import ApplicationsApi

class Applications(object):
    def __init__(self, token, gateway_url, apikey=None):
        self.__token = token
        self.__gateway_url = gateway_url
        self.__apikey = apikey

    # applications apis
    def attachments_api(self):
        return AttachmentsApi(self.__token, self.__gateway_url, self.__apikey)

    def applications_api(self):
        return ApplicationsApi(self.__token, self.__gateway_url, self.__apikey)