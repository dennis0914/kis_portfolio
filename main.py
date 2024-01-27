import json
from kis_api import kis_api

from Portfolio import Portfolio, Asset, set_kis_utils

ACCOUNT_DETAIL_PATH = "./account_detail.json"
API_KEY_PATH = "./api_key.json"
TOKEN_PATH = "./token.json"

set_kis_utils(ACCOUNT_DETAIL_PATH, API_KEY_PATH, TOKEN_PATH)


asset_stock = Asset("KODEX S&P500 TR", "379800", "krx", 0.7)
asset_bond = Asset("SPDR Portfolio Long Term Treasury ETF", "SPTL", "ams", 0.3)
print(asset_stock.total_evaluation)
print(asset_bond.total_evaluation)

bot = Portfolio(assets = [asset_stock, asset_bond], rebalance_condition=None)



#bot.start_trading()