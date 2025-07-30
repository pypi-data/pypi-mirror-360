from phenom.entity.ai_matching import AIMatching
from phenom.entity.applications import Applications
from phenom.entity.applicants import Applicants
from phenom.entity.campaigns import Campaigns
from phenom.entity.candidate import Candidate
from phenom.entity.communications import Communications
from phenom.entity.interview_screening import InterviewScreening
from phenom.entity.employees import Employees
from phenom.entity.evaluations import Evaluations
from phenom.entity.hiring_manager import HiringManager
from phenom.entity.jobs import Jobs
from phenom.entity.projects import Projects
from phenom.entity.parsers import Parsers
from phenom.entity.prediction import Prediction
from phenom.entity.tags import Tags
from phenom.entity.user_management import UserManagement

from phenom.commons.get_token import tokengeneration
class Authorization(object):
    def __init__(self, url, client_id, client_secret, gateway_url, apikey=None):
        self.__url = url
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__gateway_url = gateway_url
        self.__apikey = apikey

    def token(self):
        return tokengeneration(self.__url, self.__client_id, self.__client_secret)

    def ai_matching(self):
        return AIMatching(self.token(), self.__gateway_url, self.__apikey)
    def applications(self):
        return Applications(self.token(), self.__gateway_url, self.__apikey)
    def applicants(self):
        return Applicants(self.token(), self.__gateway_url, self.__apikey)
    def campaigns(self):
        return Campaigns(self.token(), self.__gateway_url, self.__apikey)
    def candidate(self):
        return Candidate(self.token(), self.__gateway_url, self.__apikey)
    def communications(self):
        return Communications(self.token(), self.__gateway_url, self.__apikey)
    def interview_screening(self):
        return InterviewScreening(self.token(), self.__gateway_url, self.__apikey)
    def employees(self):
        return Employees(self.token(), self.__gateway_url, self.__apikey)
    def evaluations(self):
        return Evaluations(self.token(), self.__gateway_url, self.__apikey)
    def hiring_manager(self):
        return HiringManager(self.token(), self.__gateway_url, self.__apikey)
    def jobs(self):
        return Jobs(self.token(), self.__gateway_url, self.__apikey)
    def projects(self):
        return Projects(self.token(), self.__gateway_url, self.__apikey)
    def parsers(self):
        return Parsers(self.token(), self.__gateway_url, self.__apikey)
    def prediction(self):
        return Prediction(self.token(), self.__gateway_url, self.__apikey)
    def tags(self):
        return Tags(self.token(), self.__gateway_url, self.__apikey)
    def user_management(self):
        return UserManagement(self.token(), self.__gateway_url, self.__apikey)