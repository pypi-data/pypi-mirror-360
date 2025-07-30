import http.client
import datetime
import jwt

token_details = {"token": "", "expiry": ""}


def tokengeneration(url, client_id, client_secret):
    try:
        conn = http.client.HTTPSConnection(url)
        payload = "clientId=" + client_id + "&" "clientSecret=" + client_secret
        headers = {
            'AUTH_COOKIE': '1634546337.139.324.65458',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'AUTH_COOKIE=1663132096.438.8422.634494|09d85645d3393accb9766216f4aa3fc4; LOGIN_COOKIE=1674571736.129.29.465911|6215ab38db341c1677dfbe9882af3be1'
        }
        conn.request("POST", "/token", payload, headers)
        res = conn.getresponse()
        data = res.read()
        data = data.decode("utf-8")
        i = data.index(":")
        j = data.index(",")
        conn.close()
        return "Bearer " + data[i + 2:j - 1]
    except:
        raise Exception("provide valid credentials")