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
        exchange_calendar_code_dict = {"KRX":"XKRX",
                                       "NASD":"XNYS",
                                       "NYSE":"XNYS",
                                       "AMEX":"XNYS",
                                       "SEHK":"XHKG",
                                       "SHAA":"XSHG",
                                       "SZAA":"XSHG",
                                       "TKSE":"XTKS",
                                       "HASE":"XHKG",
                                       "VNSE":"XHKG"}
        self.exchange_calendars = []
        for asset in self.asset_list:
            if asset.market not in self.exchange_calendars:
                self.exchange_calendars.append(asset.market)
        self.exchange_calendars = [excal.get_calendar(exchange_calendar_code_dict[market]) for market in self.exchange_calendars]
        total_weight = 0
        for asset in self.asset_list:
            total_weight += asset.target_weight
            if exchange_calendar_code_dict[asset.market] not in self.exchange_calendars:
                self.exchange_calendars.append(exchange_calendar_code_dict[asset.market])
        assert total_weight <= 1
        self.update_assets()
        print("portofolio initialized")

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
            for asset in self.asset_list:
                if asset.market == "KRX":
                    kis_utils.submit_order(asset.code, asset.market, asset.get_current_price, (asset.target_quantity - asset.current_quantity), fake)
            time_to_open = self.nys_calendar.next_open(utc_datetime.date()) - utc_datetime
            time.sleep(int(time_to_open.total_seconds()))
            for asset in self.asset_list:
                if asset.market in ["NASD", "NYSE", "AMEX"]:
                    kis_utils.submit_order(asset.code, asset.market, asset.get_current_price, (asset.target_quantity - asset.current_quantity), fake)
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
        self.total_evaluation = self.current_price * self.current_quantity
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
