from phenom.api.hrm.jobs_api import JobsApi

class HiringManager(object):
    def __init__(self, token, gateway_url, apikey=None):
        self.__token = token
        self.__gateway_url = gateway_url
        self.__apikey = apikey
    def jobs_api(self):
        return JobsApi(self.__token, self.__gateway_url, self.__apikey)