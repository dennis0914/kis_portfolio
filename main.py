import requests
import json
import datetime
import Authorization
import Order
import Account

URL_BASE = "https://openapi.koreainvestment.com:9443"
APP_KEY = Authorization.get_app_key()
APP_SECRET = Authorization.get_app_secret()
TOKEN = Authorization.get_token()
CANO = Account.get_cano()
ACNT_PRDT_CD = Account.get_acnt_prdt_cd()

def get_krw_usd_rate():
    headers = {"content-type":"application/json",
               "authorization":TOKEN,
               "appkey":APP_KEY,
               "appsecret":APP_SECRET,
               "tr_id":"CTRP6504R",
               "custtype":"P"}
    data = {"CANO":CANO,
            "ACNT_PRDT_CD":ACNT_PRDT_CD,
            "WCRC_FRCR_DVSN_CD":"02",
            "NATN_CD":"000",
            "TR_MKET_CD":"00",
            "INQR_DVSN_CD":"00"}
    PATH = "/uapi/overseas-stock/v1/trading/inquire-present-balance"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.get(URL, headers=headers, params=data)
    #print(res.json())
    #print(json.dumps(res.json(), indent = 4, ensure_ascii = False))
    return(float(res.json()["output2"][0]["frst_bltn_exrt"]))

def get_current_weight():
    total_account_evaluation = float(Account.get_account_balance()["account_total"]["tot_asst_amt"])
    stock = Account.get_domestic_balance()['output1'][0]
    bond = Account.get_overseas_balance()['output1'][0]
    stock_current_price = float(stock["prpr"])
    stock_current_quantity = int(stock["hldg_qty"])

    bond_current_price = float(bond["now_pric2"]) * get_krw_usd_rate()
    bond_current_quantity = int(bond["ord_psbl_qty"])
    stock_current_weight = (stock_current_price * stock_current_quantity) / total_account_evaluation
    bond_current_weight = (bond_current_price * bond_current_quantity) / total_account_evaluation
    print(stock_current_weight, bond_current_weight)

def get_rebalance_quantity():
    STOCK_WEIGHT_TARGET = 0.7
    BOND_WEIGHT_TARGET = 0.3
    assert STOCK_WEIGHT_TARGET + BOND_WEIGHT_TARGET == 1
    account_balance = Account.get_account_balance()
    domestic_balance = Account.get_domestic_balance()
    overseas_balance = Account.get_overseas_balance()
    stock = domestic_balance['output1'][0]
    bond = overseas_balance['output1'][0]

    assert stock["prdt_name"] == "KODEX 미국S&P500TR" and stock["pdno"] == "379800"
    stock_current_price = float(stock["prpr"])

    assert bond["ovrs_item_name"] == "SPDR LONG TERM TREASURY ETF" and bond["ovrs_pdno"] == "SPTL"
    bond_current_price = float(bond["now_pric2"])*get_krw_usd_rate()

    total_account_evaluation = float(account_balance["account_total"]["tot_asst_amt"])

    stock_target_quantity = int(total_account_evaluation * STOCK_WEIGHT_TARGET / stock_current_price)
    bond_target_quantity = int(total_account_evaluation * BOND_WEIGHT_TARGET / bond_current_price)
    assert (stock_target_quantity * stock_current_price + bond_target_quantity * bond_current_price) <= total_account_evaluation

    return stock_target_quantity, bond_target_quantity

def get_current_price():
    headers = {"content-type":"application/json",
               "authorization":TOKEN,
               "appkey":APP_KEY,
               "appsecret":APP_SECRET,
               "tr_id":"FHKST01010100",
               "custtype":"P"}
    data = {"FID_COND_MRKT_DIV_CODE":"J",
            "FID_INPUT_ISCD":379800}
    PATH = "/uapi/domestic-stock/v1/quotations/inquire-price"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.get(URL, headers=headers, params=data)
    print(json.dumps(res.json(), indent = 4, ensure_ascii = False))

get_current_weight()
