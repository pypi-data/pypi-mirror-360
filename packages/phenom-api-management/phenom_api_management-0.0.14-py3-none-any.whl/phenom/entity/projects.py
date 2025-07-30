from phenom.api.projects.candidates_api import CandidatesApi
from phenom.api.projects.workflows_api import WorkflowsApi
from phenom.api.projects.projects_api import ProjectsApi
from phenom.api.projects.workflow_status_api import WorkflowStatusApi

class Projects(object):
    def __init__(self, token, gateway_url, apikey):
        self.__token = token
        self.__gateway_url = gateway_url
        self.__apikey = apikey
    def candidates_api(self):
        return CandidatesApi(self.__token, self.__gateway_url, self.__apikey)
    def workflows_api(self):
        return WorkflowsApi(self.__token, self.__gateway_url, self.__apikey)
    def projects_api(self):
        return ProjectsApi(self.__token, self.__gateway_url, self.__apikey)
    def workflow_status_api(self):
        return WorkflowStatusApi(self.__token, self.__gateway_url, self.__apikey)
