from phenom.api.campaignssms.sms_campaigns_api import SMSCampaignsApi
from phenom.api.campaignsemail.email_campaigns_api import EmailCampaignsApi

class Campaigns:
    def __init__(self, token, gateway_url, apikey):
        self.__token = token
        self.__gateway_url = gateway_url
        self.__apikey = apikey

    def sms_campaigns_api(self):
        return SMSCampaignsApi(self.__token, self.__gateway_url, self.__apikey)

    def email_campaigns_api(self):
        return EmailCampaignsApi(self.__token, self.__gateway_url, self.__apikey)