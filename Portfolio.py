import time
import exchange_calendars as excal
import datetime

import kis_utils

import json
def set_kis_utils(account_number_or_account_number_path, app_key_or_key_path, token_or_token_path, app_secret = None):
    kis_utils.set_kis_api(account_number_or_account_number_path, app_key_or_key_path, token_or_token_path)


class Portfolio():
    def __init__(self, assets, rebalance_condition):
        self.asset_list = assets
        self.krx_calendar = excal.get_calendar("XKRX")
        self.nys_calendar = excal.get_calendar("XNYS")
        total_weight = 0
        for asset in self.asset_list:
            total_weight += asset.target_weight
        assert total_weight <= 1
        self.update_assets()
        print("portofolio initialized")
    '''
    def get_current_weight(self):
        total_account_evaluation = float(kis_utils.get_account_balance()["account_total"]["tot_asst_amt"])
        stock = kis_utils.get_domestic_balance()['output1'][0]
        bond = kis_utils.get_overseas_balance()['output1'][0]
        stock_current_price = float(stock["prpr"])
        stock_current_quantity = int(stock["hldg_qty"])

        bond_current_price = float(bond["now_pric2"]) * self.kis_utils.get_krw_usd_rate()
        bond_current_quantity = int(bond["ord_psbl_qty"])
        stock_current_weight = (stock_current_price * stock_current_quantity) / total_account_evaluation
        bond_current_weight = (bond_current_price * bond_current_quantity) / total_account_evaluation
        return(stock_current_weight, bond_current_weight)
    '''

    def submit_order(self, product_code, order_quantity, order_price = 0, product_market = "korea", fake = True):
        if str.lower(product_market) == "korea":
            return self.kis_utils.submit_order_korea(order_quantity = order_quantity, product_code = product_code, order_price = order_price, fake=fake)
        elif str.lower(product_market) == "nyse":
            return self.kis_utils.submit_order_nyse(order_quantity = order_quantity, product_code = product_code, order_price = self.kis_utils.get_current_price("SPTL"), fake = fake)

    def update_assets(self):
        account_total_evaluation = kis_utils.get_total_account_evaluation()
        for assets in self.asset_list:
            assets.update(account_total_evaluation)

    def rebalance_portfolio(self, fake):
        asset_current_quantities = self.kis_utils.get_current_quantity()
        asset_target_quantities = self.get_rebalance_quantity()
        stock_order_quantity = asset_current_quantities[0] - asset_target_quantities[0]
        bond_order_quantity = asset_current_quantities[1] - asset_target_quantities[1]
        utc_datetime = datetime.datetime.now(datetime.UTC)
        if self.krx_calendar.is_trading_minute(utc_datetime):
            self.submit_order("379800", stock_order_quantity, product_market="korea", fake=fake)
            time_to_open = self.nys_calendar.next_open(utc_datetime.date()) - utc_datetime
            time.sleep(int(time_to_open.total_seconds()))
            self.submit_order("SPTL", bond_order_quantity, product_market="nyse", fake=fake)
        elif self.nys_calendar.is_trading_minute(utc_datetime):
            self.submit_order("SPTL", bond_order_quantity, product_market="nyse", fake=fake)
            time_to_open = self.nys_calendar.next_open(utc_datetime.date()) - utc_datetime
            time.sleep(int(time_to_open.total_seconds()))
            self.submit_order("379800", stock_order_quantity, product_market="korea", fake=fake)

    def start_trading(self, fake = True):
        while True:
            utc_datetime = datetime.datetime.now(datetime.UTC)

            if self.krx_calendar.is_trading_minute(utc_datetime) or self.nys_calendar.is_trading_minute(utc_datetime):
                asset_weights = self.get_current_weight()
                stock_current_weight = asset_weights[0]
                bond_current_weight = asset_weights[1]
                print(stock_current_weight, bond_current_weight)
                if abs(self.stock_target_weight - stock_current_weight) > 0.05 or abs(self.bond_target_weight - bond_current_weight) > 0.05:
                    self.rebalance_portfolio(fake = fake)
            else:
                time.sleep(3600)

class Asset():
    def __init__(self, name, code, market, target_weight):
        self.name = name
        self.code = code

        supported_market_list = ["KRX", "NASD", "NYSE", "AMEX", "SEHK", "SHAA", "SZAA", "TKSE", "HASE", "VNSE"]
        self.market = str.upper(market)
        assert self.market in supported_market_list, f"Asset must be in one of the following markets: {supported_market_list}"

        self.target_weight = target_weight
        self.is_domestic = True if self.market == "KRX" else False
        self.current_quantity = self.get_current_quantity()
        self.current_price = self.get_current_price()
        self.total_evaluation = self.currents_price * self.current_quantity
        self.current_weight = 0
        self.target_quantity = 0

    def get_current_quantity(self):
        return kis_utils.get_asset_current_quantity(self.code, self.market)

    def get_current_price(self):
        return kis_utils.get_asset_current_price(self.code, self.market)

    def update(self, account_total_evaluation):
        self.current_price = self.get_current_price()
        self.current_quantity = self.get_current_quantity()
        self.total_evaluation = self.current_price * self.current_quantity
        self.current_weight = self.total_evaluation / account_total_evaluation
        self.target_quantity = int(account_total_evaluation * self.target_weight / self.current_price)
