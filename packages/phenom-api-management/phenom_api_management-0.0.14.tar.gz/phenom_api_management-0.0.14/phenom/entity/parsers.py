from phenom.api.resumeparser.resume_parsing_api import ResumeParsingApi
from phenom.api.jobparser.job_parsing_api import JobParsingApi

class Parsers(object):
    def __init__(self, token, gateway_url, apikey=None):
        self.__token = token
        self.__gateway_url = gateway_url
        self.__apikey = apikey

    # resumeparser apis
    def resume_parsing_api(self):
        return ResumeParsingApi(self.__token, self.__gateway_url, self.__apikey)
    # job-parser apis
    def job_parsing_api(self):
        return JobParsingApi(self.__token, self.__gateway_url, self.__apikey)