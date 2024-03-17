import json
from kis_api import kis_api
import kis_utils

from Portfolio import Portfolio, Asset, set_kis_utils

#ACCOUNT_DETAIL_PATH = "./account_detail.json"
ACCOUT_NUMBER = "./account_detail_isa.json"
API_KEY_PATH = "./api_key_isa.json"
TOKEN_PATH = "./token_isa.json"

set_kis_utils(ACCOUT_NUMBER, API_KEY_PATH, TOKEN_PATH)



asset_stock = Asset("KODEX S&P500 TR", "379800", "KRX", 0.7)
asset_bond = Asset("KODEX 미국채울트라30년선물(H)", "304660", "KRX", 0.3)

#asset_bond = Asset("SPDR Portfolio Long Term Treasury ETF", "SPTL", "AMEX", 0.3)


bot = Portfolio(assets = [asset_stock, asset_bond], rebalance_condition=None)
bot.start_trading(fake = False)

api = kis_utils.api
#print(api.get_account_balance())
#print(kis_utils.get_asset_current_quantity("379800", "KRX"))
#print(kis_utils.get_asset_current_quantity("304660", "KRX"))