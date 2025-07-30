from phenom.api.candidatesapiactivities.candidate_notes_api import CandidateNotesApi
from phenom.api.candidatesapiactivities.candidate_activities_api import CandidateActivitiesApi
from phenom.api.candidatesAttachmentsApi.candidate_attachments_api import CandidateAttachmentsApi
from phenom.api.candidates.candidates_api import CandidatesApi
class Candidate(object):
    def __init__(self, token, gateway_url, apikey=None):
        self.__token = token
        self.__gateway_url = gateway_url
        self.__apikey = apikey

    def candidate_notes_api(self):
        return CandidateNotesApi(self.__token, self.__gateway_url, self.__apikey)

    def candidate_activities_api(self):
        return CandidateActivitiesApi(self.__token, self.__gateway_url, self.__apikey)

    def candidate_attachments_api(self):
        return CandidateAttachmentsApi(self.__token, self.__gateway_url, self.__apikey)

    def candidates_api(self):
        return CandidatesApi(self.__token, self.__gateway_url, self.__apikey)