from phenom.api.evaluation.interview_evaluations_api import InterviewEvaluationsApi
from phenom.api.evaluation.jobs_api import JobsApi

class Evaluations(object):
    def __init__(self, token, gateway_url, apikey=None):
        self.__token = token
        self.__gateway_url = gateway_url
        self.__apikey = apikey
    def interview_evaluations_api(self):
        return InterviewEvaluationsApi(self.__token, self.__gateway_url, self.__apikey)

    def jobs_api(self):
        return JobsApi(self.__token, self.__gateway_url, self.__apikey)