from phenom.api.aisourcing.ai_matching_api import AIMatchingApi


class AIMatching(object):
    def __init__(self, token, gateway_url, apikey=None):
        self.__token = token
        self.__gateway_url = gateway_url
        self.__apikey = apikey

    # ai-sourcing apis
    def ai_matching_api(self):
        return AIMatchingApi(self.__token, self.__gateway_url, self.__apikey)