import time
import exchange_calendars as excal
import datetime

class Portfolio():
    def __init__(self, stock_target_weight, bond_target_weight, kis_api, account_number):
        self.stock_target_weight = stock_target_weight
        self.bond_target_weight = bond_target_weight
        self.account_number = account_number
        self.kis_api = kis_api
        self.krx_calendar = excal.get_calendar("XKRX")
        self.nys_calendar = excal.get_calendar("XNYS")

        assert self.stock_target_weight + self.bond_target_weight <= 1

    def get_current_weight(self):
        total_account_evaluation = float(self.kis_api.get_account_balance()["account_total"]["tot_asst_amt"])
        stock = self.kis_api.get_domestic_balance()['output1'][0]
        bond = self.kis_api.get_overseas_balance()['output1'][0]
        stock_current_price = float(stock["prpr"])
        stock_current_quantity = int(stock["hldg_qty"])

        bond_current_price = float(bond["now_pric2"]) * self.kis_api.get_krw_usd_rate()
        bond_current_quantity = int(bond["ord_psbl_qty"])
        stock_current_weight = (stock_current_price * stock_current_quantity) / total_account_evaluation
        bond_current_weight = (bond_current_price * bond_current_quantity) / total_account_evaluation
        return(stock_current_weight, bond_current_weight)

    def submit_order(self, product_code, order_quantity, order_price = 0, product_market = "korea",  fake = True):
        if str.lower(product_market) == "korea":
            return self.kis_api.submit_order_korea(order_quantity = order_quantity, product_code = product_code, order_price = order_price, fake=fake)
        elif str.lower(product_market) == "nyse":
            return self.kis_api.submit_order_nyse(order_quantity = order_quantity, product_code = product_code, order_price = self.kis_api.get_current_price("SPTL"), fake = fake)

    def get_current_price(self, product_code, product_market):
        if str.lower(product_market) == "korea":
            return self.kis_api.get_current_price_korea(product_code)
        elif str.lower(product_market) == "nyse":
            return self.kis_api.get_current_price_nyse(product_code)

    def get_rebalance_quantity(self):
        account_balance = self.kis_api.get_account_balance()
        domestic_balance = self.kis_api.get_domestic_balance()
        overseas_balance = self.kis_api.get_overseas_balance()
        stock = domestic_balance['output1'][0]
        bond = overseas_balance['output1'][0]

        assert stock["prdt_name"] == "KODEX 미국S&P500TR" and stock["pdno"] == "379800"
        stock_current_price = float(stock["prpr"])

        assert bond["ovrs_item_name"] == "SPDR LONG TERM TREASURY ETF" and bond["ovrs_pdno"] == "SPTL"
        bond_current_price = float(bond["now_pric2"])*self.kis_api.get_krw_usd_rate()

        total_account_evaluation = float(account_balance["account_total"]["tot_asst_amt"])

        stock_target_quantity = int(total_account_evaluation * self.stock_target_weight / stock_current_price)
        bond_target_quantity = int(total_account_evaluation * self.bond_target_weight / bond_current_price)
        assert (stock_target_quantity * stock_current_price + bond_target_quantity * bond_current_price) <= total_account_evaluation

        return stock_target_quantity, bond_target_quantity

    def rebalance_portfolio(self, fake = True):
        asset_current_quantities = self.kis_api.get_current_quantity()
        asset_target_quantities = self.get_rebalance_quantity()
        stock_order_quantity = asset_current_quantities[0] - asset_target_quantities[0]
        bond_order_quantity = asset_current_quantities[1] - asset_target_quantities[1]
        self.submit_order("379800", stock_order_quantity, product_market="korea", fake=fake)
        self.submit_order("SPTL", bond_order_quantity, product_market="nyse", fake=fake)

    def start_trading(self):
        while True:
            if self.krx_calendar.is_session(datetime.date.today()) or self.nys_calendar.is_session(datetime.date.today()):
                asset_weights = self.get_current_weight()
                stock_current_weight = asset_weights[0]
                bond_current_weight = asset_weights[1]
                print(stock_current_weight, bond_current_weight)
                if abs(self.stock_target_weight - stock_current_weight) > 0.05 or abs(self.bond_target_weight - bond_current_weight) > 0.05:
                    self.rebalance_portfolio()
                    time.sleep(60)
            else:
                time.sleep(3600)
