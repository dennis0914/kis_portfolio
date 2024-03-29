import requests
import json
from datetime import date, datetime, timedelta

class kis_api():
    def __init__(self, app_key, app_secret, account_number):
        self.APP_KEY = app_key
        self.APP_SECRET = app_secret
        self.account_number = account_number
        self.URL_BASE = "https://openapi.koreainvestment.com:9443"
        self.TOKEN = None

    def set_token(self, token_path = None, token = None):
        #if token value is given
        if token_path is None and token is not None:
            self.TOKEN = "Bearer " + token
        #else path to token file is given
        else:
            try:
                with open(token_path, "r") as token_file:
                    token = json.load(token_file)
                    token_file.close()
                token_expire_datetime = datetime.strptime(token["access_token_token_expired"], "%Y-%m-%d %H:%M:%S")
                if token_expire_datetime < datetime.now():
                    token = self.issue_token()
                    print("ACCESS TOKEN RENEWED")
                    print(token)
                    with open(token_path, "w") as token_file:
                        json.dump(token, token_file)
                        token_file.close()
                    self.TOKEN = "Bearer " + token["access_token"]
                else:
                    self.TOKEN = "Bearer " + token["access_token"]
            except:
                token = self.issue_token()
                print("ACCESS TOKEN RENEWED")
                print(token)
                with open(token_path, "w") as token_file:
                    json.dump(token, token_file)
                    token_file.close()
                self.TOKEN = "Bearer " + token["access_token"]

    def get_account_balance(self):
        headers = {"content-type":"application/json",
                "authorization":self.TOKEN,
                "appkey":self.APP_KEY,
                "appsecret":self.APP_SECRET,
                "tr_id":"CTRP6548R",
                "custtype":"P"}
        data = {"CANO":self.account_number[:8],
                "ACNT_PRDT_CD":self.account_number[8:],
                "INQR_DVSN_1":"",
                "BSPR_BF_DT_APLY_YN":""}
        PATH = "uapi/domestic-stock/v1/trading/inquire-account-balance"
        URL = f"{self.URL_BASE}/{PATH}"
        res = requests.get(URL, headers=headers, params=data)
        return res.json()

    def get_overseas_balance(self):
        headers = {"content-type":"application/json",
                "authorization":self.TOKEN,
                "appkey":self.APP_KEY,
                "appsecret":self.APP_SECRET,
                "tr_id":"TTTS3012R",
                "custtype":"P"}
        data = {"CANO":self.account_number[:8],
                "ACNT_PRDT_CD":self.account_number[8:],
                "OVRS_EXCG_CD":"NASD",
                "TR_CRCY_CD":"USD",
                "CTX_AREA_FK200":"",
                "CTX_AREA_NK200":""}
        PATH = "uapi/overseas-stock/v1/trading/inquire-balance"
        URL = f"{self.URL_BASE}/{PATH}"
        res = requests.get(URL, headers=headers, params=data)
        #print(json.dumps(res.json(), indent = 4, ensure_ascii = False))
        return res.json()

    def get_domestic_balance(self):
        headers = {"content-type":"application/json",
                "authorization":self.TOKEN,
                "appkey":self.APP_KEY,
                "appsecret":self.APP_SECRET,
                "tr_id":"TTTC8434R",
                "custtype":"P"}
        data = {"CANO":self.account_number[:8],
                "ACNT_PRDT_CD":self.account_number[8:],
                "AFHR_FLPR_YN":"N",
                "OFL_YN":"",
                "INQR_DVSN":"02",
                "UNPR_DVSN":"",
                "FUND_STTL_ICLD_YN":"N",
                "FNCG_AMT_AUTO_RDPT_YN":"N",
                "PRCS_DVSN":"00",
                "CTX_AREA_FK100":"",
                "CTX_AREA_NK100":""}
        PATH = "/uapi/domestic-stock/v1/trading/inquire-balance"
        URL = f"{self.URL_BASE}/{PATH}"
        res = requests.get(URL, headers=headers, params=data)
        #print(json.dumps(res.json(), indent = 4, ensure_ascii = False))
        return(res.json())

    def submit_order_domestic(self, product_code, order_price, order_quantity, fake):
        if fake:
            return "Fake order placed"
        #buy order
        if order_quantity > 0:
            trading_id = "TTTC0802U"
        #sell order
        elif order_quantity < 0:
            trading_id = "TTTC0801U"
        else:
            return None
        order_quantity = abs(int(order_quantity))
        order_price = int(order_price)
        headers = {"content-type":"application/json",
                "authorization":self.TOKEN,
                "appkey":self.APP_KEY,
                "appsecret":self.APP_SECRET,
                "tr_id":trading_id,
                "custtype":"P"}
        data = {"CANO":self.account_number[:8],
                "ACNT_PRDT_CD":self.account_number[8:],
                "PDNO":str(product_code),
                "ORD_DVSN":"00",
                "ORD_QTY":str(order_quantity),
                "ORD_UNPR":str(order_price)}
        PATH = "/uapi/domestic-stock/v1/trading/order-cash"
        URL = f"{self.URL_BASE}/{PATH}"
        res = requests.post(URL, headers=headers, data=json.dumps(data))
        return(res.json())

    def submit_order_overseas(self, asset_code, asset_market, order_price, order_quantity, fake):
        if fake:
            return "Fake order placed"
        order_trading_id_dict = {"NASD":{"BUY":"TTTT1002U",
                                    "SELL":"TTTT1006U"},
                            "NYSE":{"BUY":"TTTT1002U",
                                    "SELL":"TTTT1006U"},
                            "AMEX":{"BUY":"TTTT1002U",
                                    "SELL":"TTTT1006U"},
                            "SEHK":{"BUY":"TTTS1002U",
                                    "SELL":"TTTS1001U"},
                            "SHAA":{"BUY":"TTTS0202U",
                                    "SELL":"TTTS1005U"},
                            "SZAA":{"BUY":"TTTS0305U",
                                    "SELL":"TTTS0304U"},
                            "TKSE":{"BUY":"TTTS0308U",
                                    "SELL":"TTTS0307U"},
                            "HASE":{"BUY":"TTTS0311U",
                                    "SELL":"TTTS0310U"},
                            "VNSE":{"BUY":"TTTS0311U",
                                    "SELL":"TTTS0310U"}
                            }
        order_type = "BUY" if order_quantity > 0 else "SELL"
        order_quantity = abs(int(order_quantity))
        trading_id = order_trading_id_dict[asset_market][order_type]

        headers = {"content-type":"application/json",
            "authorization":self.TOKEN,
            "appkey":self.APP_KEY,
            "appsecret":self.APP_SECRET,
            "tr_id":trading_id,
            "custtype":"P"}

        data = {"CANO":self.account_number[:8],
                "ACNT_PRDT_CD":self.account_number[8:],
                "OVRS_EXCG_CD":asset_market,
                "PDNO":str(asset_code),
                "ORD_QTY":str(order_quantity),
                "OVRS_ORD_UNPR":str(order_price),
                "ORD_SVR_DVSN_CD":"0",
                "ORD_DVSN":"00"}
        PATH = "/uapi/overseas-stock/v1/trading/order"
        URL = f"{self.URL_BASE}/{PATH}"
        res = requests.post(URL, headers=headers, data=json.dumps(data))
        return(res.json())

    def get_current_balance(self):
        headers = {"content-type":"application/json",
                "authorization":self.TOKEN,
                "appkey":self.APP_KEY,
                "appsecret":self.APP_SECRET,
                "tr_id":"CTRP6504R",
                "custtype":"P"}
        data = {"CANO":self.account_number[:8],
                "ACNT_PRDT_CD":self.account_number[8:],
                "WCRC_FRCR_DVSN_CD":"02",
                "NATN_CD":"000",
                "TR_MKET_CD":"00",
                "INQR_DVSN_CD":"00"}
        PATH = "/uapi/overseas-stock/v1/trading/inquire-present-balance"
        URL = f"{self.URL_BASE}/{PATH}"
        res = requests.get(URL, headers=headers, params=data)
        return(res.json())

    def get_current_quantity(self):
        stock = self.get_domestic_balance()['output1'][0]
        stock_current_quantity = int(stock["hldg_qty"])
        bond = self.get_overseas_balance()['output1'][0]
        bond_current_quantity = int(bond["ord_psbl_qty"])
        return (stock_current_quantity, bond_current_quantity)

    def get_current_price_korea(self, product_code):
        headers = {"content-type":"application/json",
                   "authorization":self.TOKEN,
                   "appkey":self.APP_KEY,
                   "appsecret":self.APP_SECRET,
                   "tr_id":"FHKST01010100",
                   "custtype":"P"}
        data = {"FID_COND_MRKT_DIV_CODE":"J",
                "FID_INPUT_ISCD":str(product_code)}

        PATH = "/uapi/domestic-stock/v1/quotations/inquire-price"
        URL = f"{self.URL_BASE}/{PATH}"
        res = requests.get(URL, headers=headers, params=data)
        #print(res.json())
        #print(json.dumps(res.json(), indent = 4, ensure_ascii = False))
        return(res.json())

    def get_current_price_overseas(self, asset_code, asset_market):
        exchange_code_dict = {"NASD":"NAS",
                              "NYSE":"NYS",
                              "AMEX":"AMS",
                              "SEHK":"HKS",
                              "SHAA":"SHS",
                              "SZAA":"SZS",
                              "TKSE":"TSE",
                              "HASE":"HNX",
                              "VNSE":"HSX"}
        headers = {"content-type":"application/json",
                   "authorization":self.TOKEN,
                   "appkey":self.APP_KEY,
                   "appsecret":self.APP_SECRET,
                   "tr_id":"HHDFS76200200",
                   "custtype":"P"}
        data = {"AUTH":"",
                "EXCD":exchange_code_dict[asset_market],
                "SYMB":str(asset_code)}

        PATH = "/uapi/overseas-price/v1/quotations/price-detail"
        URL = f"{self.URL_BASE}/{PATH}"
        res = requests.get(URL, headers=headers, params=data)
        #print(res.json())
        #print(json.dumps(res.json(), indent = 4, ensure_ascii = False))
        return(res.json())

    def issue_token(self):
        headers = {"content-type":"application/json"}
        body = {"grant_type":"client_credentials",
                "appkey":self.APP_KEY,
                "appsecret":self.APP_SECRET}
        PATH = "oauth2/tokenP"
        URL = f"{self.URL_BASE}/{PATH}"
        res = requests.post(URL, headers=headers, data=json.dumps(body))
        return res.json()

    def check_order_conclusion_domestic(self, asset_code=""):
        headers = {"content-type":"application/json",
                   "authorization":self.TOKEN,
                   "appkey":self.APP_KEY,
                   "appsecret":self.APP_SECRET,
                   "tr_id":"TTTC8001R",
                   "custtype":"P"}
        data = {"CANO":self.account_number[:8],
                "ACNT_PRDT_CD":self.account_number[8:],
                "INQR_STRT_DT":(date.today()-timedelta(weeks=12)).strftime("%Y%m%d"),
                "INQR_END_DT":date.today().strftime("%Y%m%d"),
                "SLL_BUY_DVSN_CD":"00",
                "INQR_DVSN":"00",
                "PDNO":asset_code,
                "CCLD_DVSN":"00",
                "ORD_GNO_BRNO":"",
                "ODNO":"",
                "INQR_DVSN_3":"00",
                "INQR_DVSN_1":"",
                "CTX_AREA_FK100":"",
                "CTX_AREA_NK100":""}
        PATH = "/uapi/overseas-stock/v1/trading/inquire-present-balance"
        URL = f"{self.URL_BASE}/{PATH}"
        res = requests.get(URL, headers=headers, params=data)
        return(res.json())