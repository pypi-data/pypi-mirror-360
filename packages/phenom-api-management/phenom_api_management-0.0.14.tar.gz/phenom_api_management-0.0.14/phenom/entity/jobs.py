from phenom.api.search.search_api import SearchApi
from phenom.api.recommendation.recommendations_api import RecommendationsApi
from phenom.api.jobactivities.job_category_api import JobCategoryApi
from phenom.api.jobactivities.job_attachments_api import JobAttachmentsApi
from phenom.api.jobactivities.job_notes_api import JobNotesApi
from phenom.api.jobactivities.hiring_team_api import HiringTeamApi
from phenom.api.jobquestionnarie.job_questionnaire_api import JobQuestionnaireApi
from phenom.api.jobquestionnarie.questionnaire_templates_api import QuestionnaireTemplatesApi
from phenom.api.jobsync.jobs_api import JobsApi

class Jobs(object):
    def __init__(self, token, gateway_url, apikey=None):
        self.__token = token
        self.__gateway_url = gateway_url
        self.__apikey = apikey

    def search_api(self):
        return SearchApi(self.__token, self.__gateway_url, self.__apikey)

    def recommendations_api(self):
        return RecommendationsApi(self.__token, self.__gateway_url, self.__apikey)

    def job_category_api(self):
        return JobCategoryApi(self.__token, self.__gateway_url, self.__apikey)

    def job_attachments_api(self):
        return JobAttachmentsApi(self.__token, self.__gateway_url, self.__apikey)

    def job_notes_api(self):
        return JobNotesApi(self.__token, self.__gateway_url, self.__apikey)

    def hiring_team_api(self):
        return HiringTeamApi(self.__token, self.__gateway_url, self.__apikey)

    def job_questionnaire_api(self):
        return JobQuestionnaireApi(self.__token, self.__gateway_url, self.__apikey)

    def questionnaire_templates_api(self):
        return QuestionnaireTemplatesApi(self.__token, self.__gateway_url, self.__apikey)

    def jobs_api(self):
        return JobsApi(self.__token, self.__gateway_url, self.__apikey)