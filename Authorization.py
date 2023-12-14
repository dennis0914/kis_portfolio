import json
import requests
import datetime

API_KEY_PATH = "./api_key.json"
TOKEN_PATH = "./token.json"

URL_BASE = "https://openapi.koreainvestment.com:9443"

with open(API_KEY_PATH, "r") as app_key_file:
    app_key = json.load(app_key_file)
    app_key_file.close()
APP_KEY = app_key["app_key"]
APP_SECRET = app_key["app_secret"]

def issue_token():
    headers = {"content-type":"application/json"}
    body = {"grant_type":"client_credentials",
            "appkey":APP_KEY,
            "appsecret":APP_SECRET}
    PATH = "oauth2/tokenP"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    return res.json()

def get_token():
    with open(TOKEN_PATH, "r") as token_file:
        token = json.load(token_file)
        token_file.close()
    token_expire_datetime = datetime.datetime.strptime(token["access_token_token_expired"], "%Y-%m-%d %H:%M:%S")
    if token_expire_datetime < datetime.datetime.now():
        token = issue_token()
        print("access token renewed")
        print(token)
        with open(TOKEN_PATH, "w") as token_file:
            json.dump(token, token_file)
            token_file.close()
        return "Bearer " + token["access_token"]
    else:
        return "Bearer " + token["access_token"]

def get_app_key():
    return APP_KEY

def get_app_secret():
    return APP_SECRET

