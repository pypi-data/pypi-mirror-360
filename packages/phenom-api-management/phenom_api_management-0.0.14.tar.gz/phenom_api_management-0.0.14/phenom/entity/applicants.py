from phenom.api.applicants.applicants_api import ApplicantsApi
from phenom.api.applicants.leads_api import LeadsApi
from phenom.api.applicants.activity_api import ActivityApi
from phenom.api.applicants.hiring_status_api import HiringStatusApi
from phenom.api.applicants.candidates_attachments_api import CandidatesAttachmentsApi

class Applicants(object):
    def __init__(self, token, gateway_url, apikey=None):
        self.__token = token
        self.__gateway_url = gateway_url
        self.__apikey = apikey

    # applicants apis
    def applicants_api(self):
        return ApplicantsApi(self.__token, self.__gateway_url, self.__apikey)

    def activity_api(self):
        return ActivityApi(self.__token, self.__gateway_url, self.__apikey)

    def hiring_status_api(self):
        return HiringStatusApi(self.__token, self.__gateway_url, self.__apikey)

    def leads_api(self):
        return LeadsApi(self.__token, self.__gateway_url, self.__apikey)

    def candidates_attachments_api(self):
        return CandidatesAttachmentsApi(self.__token, self.__gateway_url, self.__apikey)