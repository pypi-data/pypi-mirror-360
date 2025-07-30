from phenom.api.servicehubpublic.user_management_api import UserManagementApi
from phenom.api.servicehubscim.scim_api import SCIMApi

class UserManagement(object):
    def __init__(self, token, gateway_url, apikey=None):
        self.__token = token
        self.__gateway_url = gateway_url
        self.__apikey = apikey

    def user_management(self):
        return UserManagementApi(self.__token, self.__gateway_url, self.__apikey)

    def scim_api(self):
        return SCIMApi(self.__token, self.__gateway_url, self.__apikey)