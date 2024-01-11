import json
from kis_api import kis_api
from Portfolio import Portfolio

ACCOUNT_DETAIL_PATH = "./account_detail.json"
with open(ACCOUNT_DETAIL_PATH, "r") as account_detail_file:
    account_detail = json.load(account_detail_file)
    account_detail_file.close()
account_number = account_detail["account_number"]

API_KEY_PATH = "./api_key.json"
TOKEN_PATH = "./token.json"

with open(API_KEY_PATH, "r") as app_key_file:
    app_key = json.load(app_key_file)
    app_key_file.close()
APP_KEY = app_key["app_key"]
APP_SECRET = app_key["app_secret"]

kis_api = kis_api(APP_KEY, APP_SECRET, account_number)
kis_api.set_token(token_path=TOKEN_PATH)

bot = Portfolio(stock_target_weight=0.7,
                bond_target_weight=0.3,
                kis_api=kis_api,
                account_number=account_number)

#bot.start_trading()