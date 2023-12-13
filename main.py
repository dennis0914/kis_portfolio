import requests
import json
import datetime

API_KEY_PATH = "./api_key.json"
TOKEN_PATH = "./token.json"
URL_BASE = "https://openapi.koreainvestment.com:9443"

def get_token():
    headers = {"content-type":"application/json"}
    body = {"grant_type":"client_credentials",
            "appkey":APP_KEY,
            "appsecret":APP_SECRET}
    PATH = "oauth2/tokenP"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    return res.json()

def load_token():
    with open(TOKEN_PATH, "r") as token_file:
        token = json.load(token_file)
        token_file.close()
    token_expire_datetime = datetime.datetime.strptime(token["access_token_token_expired"], "%Y-%m-%d %H:%M:%S")
    if token_expire_datetime < datetime.datetime.now():
        token = get_token()
        print("access token renewed")
        print(token)
        with open(TOKEN_PATH, "w") as token_file:
            json.dump(token, token_file)
            token_file.close()
        return "Bearer " + token["access_token"]
    else:
        return "Bearer " + token["access_token"]


def get_account_balance():
    headers = {"content-type":"application/json",
               "authorization":load_token(),
               "appkey":APP_KEY,
               "appsecret":APP_SECRET,
               "tr_id":"CTRP6548R",
               "custtype":"P"}
    data = {"CANO":"63534364",
            "ACNT_PRDT_CD":"01",
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
               "authorization":load_token(),
               "appkey":APP_KEY,
               "appsecret":APP_SECRET,
               "tr_id":"TTTS3012R",
               "custtype":"P"}
    data = {"CANO":"63534364",
            "ACNT_PRDT_CD":"01",
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
               "authorization":load_token(),
               "appkey":APP_KEY,
               "appsecret":APP_SECRET,
               "tr_id":"TTTC8434R",
               "custtype":"P"}
    data = {"CANO":"63534364",
            "ACNT_PRDT_CD":"01",
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

def get_krw_usd_rate():
    headers = {"content-type":"application/json",
               "authorization":load_token(),
               "appkey":APP_KEY,
               "appsecret":APP_SECRET,
               "tr_id":"CTRP6504R",
               "custtype":"P"}
    data = {"CANO":"63534364",
            "ACNT_PRDT_CD":"01",
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

def get_rebalance_quantity():
    STOCK_TARGET = 0.7
    BOND_TARGET = 0.3
    assert STOCK_TARGET + BOND_TARGET == 1

    asset_balance = get_account_balance()

get_domestic_balance()
