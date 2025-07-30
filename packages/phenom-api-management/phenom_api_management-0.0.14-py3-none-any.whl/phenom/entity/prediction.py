from phenom.api.prediction.prediction_api import PredictionApi

class Prediction(object):
    def __init__(self, token, gateway_url, apikey=None):
        self.__token = token
        self.__gateway_url = gateway_url
        self.__apikey = apikey

    def prediction_api(self):
        return PredictionApi(self.__token, self.__gateway_url, self.__apikey)