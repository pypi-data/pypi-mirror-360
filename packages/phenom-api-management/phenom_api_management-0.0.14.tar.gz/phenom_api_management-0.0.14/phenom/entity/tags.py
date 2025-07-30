from phenom.api.tags.tags_api import TagsApi
from phenom.api.tags.candidates_api import CandidatesApi

class Tags(object):
    def __init__(self, token, gateway_url, apikey=None):
        self.__token = token
        self.__gateway_url = gateway_url
        self.__apikey = apikey

    def tags_api(self):
        return TagsApi(self.__token, self.__gateway_url, self.__apikey)

    def candidates_api(self):
        return CandidatesApi(self.__token, self.__gateway_url, self.__apikey)