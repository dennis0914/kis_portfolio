from kis_api import kis_api
import json

api = None

def set_kis_api(account_number_or_account_number_path, app_key_or_key_path, token_or_token_path, app_secret = None):
    try:
        with open(account_number_or_account_number_path, "r") as account_detail_file:
            account_detail = json.load(account_detail_file)
            account_detail_file.close()
        ACCOUNT_NUMBER = account_detail["account_number"]
    except:
        ACCOUNT_NUMBER = account_number_or_account_number_path

    try:
        with open(app_key_or_key_path, "r") as app_key_file:
            app_key = json.load(app_key_file)
            app_key_file.close()
        APP_KEY = app_key["app_key"]
        APP_SECRET = app_key["app_secret"]
    except:
        APP_KEY = app_key_or_key_path
        APP_SECRET = app_secret
    global api
    api = kis_api(APP_KEY, APP_SECRET, ACCOUNT_NUMBER)
    api.set_token(token_path = token_or_token_path)

def get_krw_usd_rate():
    current_balance = api.get_current_price_overseas("SPY", "AMEX")
    return(float(current_balance["output"]['t_rate']))

def get_account_balance():
    res = api.get_account_balance()
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
    for asset_value, asset_name in zip(res['output1'], asset_balance.keys()):
        asset_balance[asset_name] = asset_value
        asset_balance["account_total"] = res['output2']
        asset_balance["account_total"]["whol_weit_rt"] = '100.00'
        account_balance = dict()
    for asset_type in asset_balance:
        if float(asset_balance[asset_type]['whol_weit_rt']) == 0:
            continue
        else:
            account_balance[asset_type]=(asset_balance[asset_type])
    return account_balance

def get_overseas_balance():
    overseas_balance = api.get_overseas_balance()
    return overseas_balance

def get_domestic_balance():
    domestic_balance = api.get_domestic_balance()
    return domestic_balance

def get_domestic_asset_price(asset_code):
    return api.get_current_price_korea(asset_code)

def get_overseas_asset_price(asset_code, asset_market):
    return api.get_current_price_overseas(asset_code, asset_market)

def get_asset_current_price(asset_code, asset_market, price_in_krw = True):
    if asset_market == 'KRX':
        return float(get_domestic_asset_price(asset_code)['output']['stck_prpr'])
    else:
        return float(get_overseas_asset_price(asset_code, asset_market)['output']['last'])*get_krw_usd_rate()

def get_asset_current_quantity(asset_code, asset_market):
    if asset_market == 'KRX':
        domestic_balance = get_domestic_balance()
        if domestic_balance['output1'] == []:
            return 0
        for domestic_asset in domestic_balance['output1']:
            if domestic_asset['pdno'] == asset_code:
                return int(domestic_asset['hldg_qty'])
        return 0
    else:
        overseas_balance = get_overseas_balance()
        if overseas_balance['output1'] == []:
            return 0
        for overseas_asset in overseas_balance['output1']:
            if overseas_asset['ovrs_pdno'] == asset_code:
                return int(overseas_asset['ord_psbl_qty'])
        return 0

def get_total_account_evaluation():
    account_balance = get_account_balance()
    return(int(account_balance['account_total']['tot_asst_amt']))

def submit_order(asset_code, asset_market, order_price, order_quantity, fake = True):
    if asset_market == 'KRX':
        return api.submit_order_domestic(asset_code, order_price, order_quantity, fake)
    else:
        return api.submit_order_overseas(asset_code, asset_market, order_price, order_quantity, fake)

def check_order_filled(asset_code, asset_market, order_number):
    if asset_market=='KRX':
        order_conclusions=api.check_order_conclusion_domestic(asset_code)
        for order in order_conclusions['output1']:
            if order_number==order['odno']:
                return int(order['rmn_qty'])
            else:
                return -1
