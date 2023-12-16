import Authorization
import requests
import json
import Authorization

URL_BASE = "https://openapi.koreainvestment.com:9443"
TOKEN = Authorization.get_token()
APP_KEY = Authorization.get_app_key()
APP_SECRET = Authorization.get_app_secret()

ACCOUNT_DETAIL_PATH = "./account_detail.json"
with open(ACCOUNT_DETAIL_PATH, "r") as account_detail_file:
    account_detail = json.load(account_detail_file)
    account_detail_file.close()
CANO = account_detail["CANO"]
ACNT_PRDT_CD = account_detail["ACNT_PRDT_CD"]

def get_cano():
    return CANO

def get_acnt_prdt_cd():
    return ACNT_PRDT_CD

def get_account_balance():
    headers = {"content-type":"application/json",
               "authorization":TOKEN,
               "appkey":APP_KEY,
               "appsecret":APP_SECRET,
               "tr_id":"CTRP6548R",
               "custtype":"P"}
    data = {"CANO":CANO,
            "ACNT_PRDT_CD":ACNT_PRDT_CD,
            "INQR_DVSN_1":"",
            "BSPR_BF_DT_APLY_YN":""}
    PATH = "uapi/domestic-stock/v1/trading/inquire-account-balance"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.get(URL, headers=headers, params=data)
    asset_balance = {"stock_domestic":None,
                     "fund":None,
                     "bond_domestic":None,
                     "els_dls":None,
                     "wrap":None,
                     "trust":None,
                     "rp":None,
                     "stock_overseas":None,
                     "bond_overseas":None,
                     "gold":None,
                     "cd_cp":None,
                     "short_term_bond_domestic":None,
                     "other":None,
                     "short_term_bond_overseas":None,
                     "els_dls_overseas":None,
                     "overseas_currency":None,
                     "deposit_cma":None,
                     "applicant_deposit":None,
                     "account_total":None}
    #print(json.dumps(res.json(), indent = 4))
    for asset_value, asset_name in zip(res.json()['output1'], asset_balance.keys()):
        asset_balance[asset_name] = asset_value
    asset_balance["account_total"] = res.json()['output2']
    asset_balance["account_total"]["whol_weit_rt"] = '100.00'
    account_balance = dict()
    for asset_type in asset_balance:
        if float(asset_balance[asset_type]['whol_weit_rt']) == 0:
            continue
        else:
            account_balance[asset_type]=(asset_balance[asset_type])
    return account_balance

def get_overseas_balance():
    headers = {"content-type":"application/json",
               "authorization":TOKEN,
               "appkey":APP_KEY,
               "appsecret":APP_SECRET,
               "tr_id":"TTTS3012R",
               "custtype":"P"}
    data = {"CANO":CANO,
            "ACNT_PRDT_CD":ACNT_PRDT_CD,
            "OVRS_EXCG_CD":"NASD",
            "TR_CRCY_CD":"USD",
            "CTX_AREA_FK200":"",
            "CTX_AREA_NK200":""}
    PATH = "uapi/overseas-stock/v1/trading/inquire-balance"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.get(URL, headers=headers, params=data)
    #print(json.dumps(res.json(), indent = 4, ensure_ascii = False))
    return res.json()

def get_domestic_balance():
    headers = {"content-type":"application/json",
               "authorization":TOKEN,
               "appkey":APP_KEY,
               "appsecret":APP_SECRET,
               "tr_id":"TTTC8434R",
               "custtype":"P"}
    data = {"CANO":CANO,
            "ACNT_PRDT_CD":ACNT_PRDT_CD,
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
    URL = f"{URL_BASE}/{PATH}"
    res = requests.get(URL, headers=headers, params=data)
    #print(json.dumps(res.json(), indent = 4, ensure_ascii = False))
    return(res.json())