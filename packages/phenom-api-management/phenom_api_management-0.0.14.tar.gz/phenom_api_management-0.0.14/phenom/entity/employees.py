from phenom.api.employees.employee_profile_api import EmployeeProfileApi
from phenom.api.employees.employee_preferences_api import EmployeePreferencesApi
from phenom.api.employeescourses.employee_courses_api import EmployeeCoursesApi
from phenom.api.employeesreferral.employee_referrals_api import EmployeeReferralsApi
from phenom.api.employeescareerpath.employee_career_path_api import EmployeeCareerPathApi

from phenom.api.exsearch.employee_search_api import EmployeeSearchApi
from phenom.api.exsearch.mentor_api import MentorApi

class Employees(object):
    def __init__(self, token, gateway_url, apikey=None):
        self.__token = token
        self.__gateway_url = gateway_url
        self.__apikey = apikey

    def employee_profile_api(self):
        return EmployeeProfileApi(self.__token, self.__gateway_url, self.__apikey)

    def employee_preferences_api(self):
        return EmployeePreferencesApi(self.__token, self.__gateway_url, self.__apikey)

    def employee_courses_api(self):
        return EmployeeCoursesApi(self.__token, self.__gateway_url, self.__apikey)

    def employee_referrals_api(self):
        return EmployeeReferralsApi(self.__token, self.__gateway_url, self.__apikey)

    def employee_career_path_api(self):
        return EmployeeCareerPathApi(self.__token, self.__gateway_url, self.__apikey)

    def employee_search_api(self):
        return EmployeeSearchApi(self.__token, self.__gateway_url, self.__apikey)

    def mentor_api(self):
        return MentorApi(self.__token, self.__gateway_url, self.__apikey)