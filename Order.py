import Authorization
import Account
import requests
import json

URL_BASE = "https://openapi.koreainvestment.com:9443"
APP_KEY = Authorization.get_app_key()
APP_SECRET = Authorization.get_app_secret()
TOKEN = Authorization.get_token()
CANO = Account.get_cano()
ACNT_PRDT_CD = Account.get_acnt_prdt_cd()

def submit_order(order_quantity, product_code="379800"):
    #buy order
    if order_quantity > 0:
        trading_id = "TTTC0802U"
    #sell order
    elif order_quantity < 0:
        trading_id = "TTTC0801U"
    else:
        return None
    headers = {"content-type":"application/json",
               "authorization":TOKEN,
               "appkey":APP_KEY,
               "appsecret":APP_SECRET,
               "tr_id":trading_id,
               "custtype":"P"}
    data = {"CANO":CANO,
            "ACNT_PRDT_CD":ACNT_PRDT_CD,
            "PDNO":str(product_code),
            "ORD_DVSN":"01",
            "ORD_QTY":str(order_quantity),
            "ORD_UNPR":"0"}
    PATH = "/uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    return(res.json())

def submit_order_overseas(product_code, order_quantity, order_price):
    #buy order
    if order_quantity > 0:
        trading_id = "TTTT1002U"
    #sell order
    elif order_quantity < 0:
        trading_id = "TTTT1006U"
    else:
        return None
    headers = {"content-type":"application/json",
               "authorization":TOKEN,
               "appkey":APP_KEY,
               "appsecret":APP_SECRET,
               "tr_id":trading_id,
               "custtype":"P"}

    data = {"CANO":CANO,
            "ACNT_PRDT_CD":ACNT_PRDT_CD,
            "OVRS_EXCG_CD":"NYSE",
            "PDNO":str(product_code),
            "ORD_QTY":str(order_quantity),
            "OVRS_ORD_UNPR":str(order_price),
            "ORD_SVR_DVSN_CD":"0",
            "ORD_DVSN":"00"}
    PATH = "/uapi/overseas-stock/v1/trading/order"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    return(res.json())