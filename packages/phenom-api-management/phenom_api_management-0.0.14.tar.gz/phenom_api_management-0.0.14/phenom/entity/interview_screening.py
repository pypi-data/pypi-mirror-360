from phenom.api.videoplatform.review_api import ReviewApi
from phenom.api.videoplatform.evaluations_api import EvaluationsApi
from phenom.api.videoplatform.questions_api import QuestionsApi
from phenom.api.videoplatform.candidate_invite_api import CandidateInviteApi
from phenom.api.videoplatform.job_questionnaire_config_api import JobQuestionnaireConfigApi
from phenom.api.videoplatform.questionnaire_templates_api import QuestionnaireTemplatesApi

class InterviewScreening(object):
    def __init__(self, token, gateway_url, apikey=None):
        self.__token = token
        self.__gateway_url = gateway_url
        self.__apikey = apikey

    def review_api(self):
        return ReviewApi(self.__token, self.__gateway_url, self.__apikey)

    def evaluations_api(self):
        return EvaluationsApi(self.__token, self.__gateway_url, self.__apikey)

    def questions_api(self):
        return QuestionsApi(self.__token, self.__gateway_url, self.__apikey)

    def candidate_invite_api(self):
        return CandidateInviteApi(self.__token, self.__gateway_url, self.__apikey)

    def job_questionnaire_config_api(self):
        return JobQuestionnaireConfigApi(self.__token, self.__gateway_url, self.__apikey)

    def questionnaire_templates_api(self):
        return QuestionnaireTemplatesApi(self.__token, self.__gateway_url, self.__apikey)