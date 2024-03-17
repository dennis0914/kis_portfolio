import time
import exchange_calendars as excal
from datetime import datetime, timezone, timedelta
import kis_utils

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
        self.portfolio_asset_market_dict = dict()
        for asset in self.asset_list:
            if asset.market not in self.portfolio_asset_market_dict:
                self.portfolio_asset_market_dict[asset.market] = excal.get_calendar(exchange_calendar_code_dict[asset.market])
        total_weight = 0
        for asset in self.asset_list:
            total_weight += asset.target_weight
        assert total_weight <= 1
        account_total_evaluation = kis_utils.get_total_account_evaluation()
        for asset in self.asset_list:
            asset.update(account_total_evaluation)
        print("portofolio initialized")

    def update_assets(self, asset_list):
        account_total_evaluation = kis_utils.get_total_account_evaluation()
        self.asset_list = asset_list
        for asset in asset_list:
            asset.update(account_total_evaluation)

    def rebalance_portfolio(self, fake):
        while self.rebalance_trigger():
            for portfolio_asset_market in self.portfolio_asset_market_dict:
                exchange_calendar = self.portfolio_asset_market_dict[portfolio_asset_market]
                if exchange_calendar.is_trading_minute(datetime.now(timezone.utc)):
                    for asset in self.asset_list:
                        if asset.market == portfolio_asset_market:
                            order_quantity = int(asset.target_quantity - asset.current_quantity)
                            if order_quantity == 0:
                                continue
                            else:
                                print(datetime.now(timezone.utc), f"Submitting order for {asset.name}, order quantity {order_quantity}, order price {asset.current_price}")
                                order_detail=kis_utils.submit_order(asset.code, asset.market, asset.current_price, order_quantity, fake=fake)
                                #{'rt_cd': '0', 'msg_cd': 'APBK0013', 'msg1': '주문 전송 완료 되었습니다.', 'output': {'KRX_FWDG_ORD_ORGNO': '91254', 'ODNO': '0000063291', 'ORD_TMD': '094745'}}
                                print(datetime.now(timezone.utc), f"Order submitted for {asset.name}, order quantity {order_quantity}")
                                print(order_detail)
                                time.sleep(10)
                                while asset.rebalance_needed:
                                    remaining_quantity_to_filled=kis_utils.check_order_filled(asset.code, asset.market, order_detail['output']['ODNO'])
                                    if remaining_quantity_to_filled==0:
                                        print(datetime.now(timezone.utc), f"Order filled for {asset.name}. filled quantity {order_quantity}")
                                        asset.rebalance_needed=False
                                    time.sleep(5)
        self.rebalance_needed = False

    def rebalance_trigger(self):
        for asset in self.asset_list:
            if asset.rebalance_needed == True:
                return True
        return False

    def market_closest_open(self):
        min_time_to_open = timedelta(days=999)
        market_closest_to_open = None
        for exchange in self.portfolio_asset_market_dict:
            time_to_open = self.portfolio_asset_market_dict[exchange].next_open(datetime.now(timezone.utc)) - datetime.now(timezone.utc)
            market_closest_to_open = exchange if time_to_open < min_time_to_open else None
        return market_closest_to_open

    def start_trading(self, fake = True):
        self.rebalance_needed = False
        while True:
            for exchange_calendar in self.portfolio_asset_market_dict.values():
                if exchange_calendar.is_trading_minute(datetime.now(timezone.utc)):
                    current_account_total_balance = kis_utils.get_total_account_evaluation()
                    for asset in self.asset_list:
                        asset.update(current_account_total_balance)
                        print(f"{asset.name} price: {asset.current_price}, quantity: {asset.current_quantity}, evaluation: {asset.current_asset_evaluation}, weight: {asset.current_weight}")
                        if abs(asset.current_weight - asset.target_weight) > 0.05 and int(asset.target_quantity - asset.current_quantity) != 0:
                            self.rebalance_needed = True
                            asset.rebalance_needed = True
                            print(datetime.now(timezone.utc), "Rebalance condition triggered")
                else:
                    print(datetime.now(timezone.utc), "None of the assets in the portfolio are tradable now. ")
                    next_open_market = self.market_closest_open()
                    time_to_open = self.portfolio_asset_market_dict[next_open_market].next_open(datetime.now(timezone.utc)) - datetime.now(timezone.utc)
                    time_to_open = round(time_to_open.total_seconds() + 0.5)
                    print(f"Next trading session: {next_open_market}, time to open: {timedelta(seconds=time_to_open)}")
                    time.sleep(30)
            print(f"Current account total evaluation: {kis_utils.get_total_account_evaluation()}")
            if self.rebalance_needed:
                self.rebalance_portfolio(fake=fake)
            time.sleep(30)


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
        self.current_asset_evaluation = self.current_price * self.current_quantity
        self.current_weight = 0
        self.target_quantity = 0
        self.rebalance_needed = False

    def get_current_quantity(self):
        return kis_utils.get_asset_current_quantity(self.code, self.market)

    def get_current_price(self):
        return kis_utils.get_asset_current_price(self.code, self.market)

    def update(self, account_total_evaluation):
        self.current_price = self.get_current_price()
        self.current_quantity = self.get_current_quantity()
        self.current_asset_evaluation = self.current_price * self.current_quantity
        self.current_weight = self.current_asset_evaluation / account_total_evaluation
        self.target_quantity = int(account_total_evaluation * self.target_weight / self.current_price)
