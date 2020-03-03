#!/usr/bin/env python
# coding: utf-8

import requests
import requests.auth
import base64
import time
import json
import binascii
from hashlib import sha256
from urllib.parse import urlparse
from pandas.io.json import json_normalize
import pandas as pd
import numpy as np
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re





class QtradeAuth(requests.auth.AuthBase):
    def __init__(self, key):
        self.key_id, self.key = key.split(":")

    def __call__(self, req):
        # modify and return the request
        timestamp = str(int(time.time()))
        url_obj = urlparse(req.url)

        request_details = req.method + "\n"
        request_details += url_obj.path + url_obj.params + "\n"
        request_details += timestamp + "\n"
        if req.body:
            request_details += req.body + "\n"
        else:
            request_details += "\n"
        request_details += self.key
        hsh = sha256(request_details.encode("utf8")).digest()
        signature = base64.b64encode(hsh)
        req.headers.update({
            "Authorization": "HMAC-SHA256 {}:{}".format(self.key_id, signature.decode("utf8")),
            "HMAC-Timestamp": timestamp
        })
        return req

# Create a session object to make repeated API calls easy!
api = requests.Session()
# Create an authenticator with your API key
api.auth = QtradeAuth("YOUR_API_KEY")





trade_history = api.get("https://api.qtrade.io/v1/user/trades").json()
json_str = json.dumps(trade_history)
trade_history = json.loads(json_str)





nyzo_sells = []
for x in range(len(trade_history['data']['trades'])):
    if trade_history['data']['trades'][x]['market_string'] == 'NYZO_BTC' and trade_history['data']['trades'][x]['side'] == 'sell':
        nyzo_sells.append(trade_history['data']['trades'][x])





nyzo_buys = []
for x in range(len(trade_history['data']['trades'])):
    if trade_history['data']['trades'][x]['market_string'] == 'NYZO_BTC' and trade_history['data']['trades'][x]['side'] == 'buy':
        nyzo_buys.append(trade_history['data']['trades'][x])





default_column_list = ['Date', 'Type', 'Exchange', 'Base amount', 'Base currency', 'Quote amount', 'Quote currency', 'Fee', 'Fee currency', 'Costs/Proceeds', 'Costs/Proceeds currency', 'Sync Holdings', 'Sent/Received from', 'Sent to', 'Notes']





nyzo_buy_df = pd.DataFrame(data=nyzo_buys)
for x in range(len(nyzo_buy_df)):
    nyzo_buy_df['created_at'].iloc[x] = pd.to_datetime(nyzo_buy_df['created_at'].iloc[x]).strftime('%Y-%m-%d %H:%M:%S')

nyzo_buy_df = nyzo_buy_df.rename(columns={'created_at': 'Date', 'base_fee': 'Fee', 'market_amount': 'Base amount', 'base_amount': 'Quote amount'})
del nyzo_buy_df['id']
del nyzo_buy_df['price']
del nyzo_buy_df['taker']
del nyzo_buy_df['side']
del nyzo_buy_df['market_string']
del nyzo_buy_df['market_id']
del nyzo_buy_df['order_id']

nyzo_buy_df['Type'] = 'BUY'
nyzo_buy_df['Exchange'] = 'qTrade'
nyzo_buy_df['Base currency'] = 'NYZO'
nyzo_buy_df['Quote currency'] = 'BTC'
nyzo_buy_df['Fee currency'] = 'BTC'
nyzo_buy_df['Costs/Proceeds'] = 'NaN'
nyzo_buy_df['Costs/Proceeds currency'] = 'NaN'
nyzo_buy_df['Sync Holdings'] = '1'
nyzo_buy_df['Sent/Received from'] = 'NaN'
nyzo_buy_df['Sent to'] = 'NaN'
nyzo_buy_df['Notes'] = 'NaN'





buy_column_list = list(nyzo_buy_df.columns)
buy_cols = buy_column_list
buy_cols = buy_cols[3:6]+buy_cols[0:1]+buy_cols[6:7]+buy_cols[1:2]+buy_cols[7:8]+buy_cols[2:3]+buy_cols[8:]
nyzo_buy_df = nyzo_buy_df[buy_cols]





nyzo_sell_df = pd.DataFrame(data=nyzo_sells)

for x in range(len(nyzo_sell_df)):
    nyzo_sell_df['created_at'].iloc[x] = pd.to_datetime(nyzo_sell_df['created_at'].iloc[x]).strftime('%Y-%m-%d %H:%M:%S')

nyzo_sell_df = nyzo_sell_df.rename(columns={'created_at': 'Date', 'base_fee': 'Fee', 'market_amount': 'Base amount', 'base_amount': 'Quote amount'})
del nyzo_sell_df['id']
del nyzo_sell_df['price']
del nyzo_sell_df['taker']
del nyzo_sell_df['side']
del nyzo_sell_df['market_string']
del nyzo_sell_df['market_id']
del nyzo_sell_df['order_id']

nyzo_sell_df['Type'] = 'SELL'
nyzo_sell_df['Exchange'] = 'qTrade'
nyzo_sell_df['Base currency'] = 'NYZO'
nyzo_sell_df['Quote currency'] = 'BTC'
nyzo_sell_df['Fee currency'] = 'BTC'
nyzo_sell_df['Costs/Proceeds'] = 'NaN'
nyzo_sell_df['Costs/Proceeds currency'] = 'NaN'
nyzo_sell_df['Sync Holdings'] = '1'
nyzo_sell_df['Sent/Received from'] = 'NaN'
nyzo_sell_df['Sent to'] = 'NaN'
nyzo_sell_df['Notes'] = 'NaN'

sell_column_list = list(nyzo_sell_df.columns)
sell_cols = sell_column_list
sell_cols = sell_cols[3:6]+sell_cols[0:1]+sell_cols[6:7]+sell_cols[1:2]+sell_cols[7:8]+sell_cols[2:3]+sell_cols[8:]
nyzo_sell_df = nyzo_sell_df[sell_cols]





full_trade_df = pd.concat([nyzo_buy_df, nyzo_sell_df], axis=0)





withdraw_history = api.get("https://api.qtrade.io/v1/user/withdraws").json()
json_str = json.dumps(withdraw_history)
withdraw_history = json.loads(json_str)

btc_net_withdraws = []
for x in range(len(withdraw_history['data']['withdraws'])):
    if withdraw_history['data']['withdraws'][x]['currency'] == 'BTC':
        btc_net_withdraws.append(float(withdraw_history['data']['withdraws'][x]['amount']))

btc_withdraw_fees = []
for x in range(len(btc_net_withdraws)):
    btc_withdraw_fees.append(float(withdraw_history['data']['withdraws'][x]['network_data']['reciept']['CustomerFee']))

btc_gross_withdraws = np.array([btc_net_withdraws, btc_withdraw_fees])

btc_gross_withdraws = np.sum(btc_gross_withdraws, 0)

btc_gross_withdraws = np.around(btc_gross_withdraws, decimals=8)





btc_withdraws = []
for x in range(len(withdraw_history['data']['withdraws'])):
    if withdraw_history['data']['withdraws'][x]['currency'] == 'BTC':
        btc_withdraws.append((withdraw_history['data']['withdraws'][x]['currency'] ,(float(withdraw_history['data']['withdraws'][x]['amount']), float(withdraw_history['data']['withdraws'][x]['network_data']['reciept']['CustomerFee']))))

nyzo_withdraws_urls = []
for x in range(len(withdraw_history['data']['withdraws'])):
    if withdraw_history['data']['withdraws'][x]['currency'] == 'NYZO':
        nyzo_withdraws_urls.append(withdraw_history['data']['withdraws'][x]['network_data']['explorer_url'])
nyzo_withdraws = []
for y in nyzo_withdraws_urls:
    page = urlopen(y)
    soup = BeautifulSoup(page)
    x = soup.body.find('div', attrs={'class' : 'block-div'}).text
    total_nyzo = re.split(r"[ :\-]+", x)[17][1:-3]
    nyzo_fee = re.split(r"[ :\-]+", x)[18][1:-8]
    nyzo_withdraws.append(('NYZO', (float(total_nyzo)+5, float(nyzo_fee)+5)))





btc_withdraw_timestamps = []
for x in range(len(withdraw_history['data']['withdraws'])):
    if withdraw_history['data']['withdraws'][x]['currency'] == 'BTC':
        btc_withdraw_timestamps.append(pd.to_datetime(withdraw_history['data']['withdraws'][x]['network_data']['sent_time']).strftime('%Y-%m-%d %H:%M:%S'))

nyzo_withdraw_timestamps = []
for x in range(len(withdraw_history['data']['withdraws'])):
    if withdraw_history['data']['withdraws'][x]['currency'] == 'NYZO':
        nyzo_withdraw_timestamps.append(pd.to_datetime(withdraw_history['data']['withdraws'][x]['created_at']).strftime('%Y-%m-%d %H:%M:%S'))

btc_nyzo_withdraw_timestamps = []
btc_nyzo_withdraw_timestamps.append(btc_withdraw_timestamps+nyzo_withdraw_timestamps)





btc_nyzo_withdraws = []
btc_nyzo_withdraws.append(btc_withdraws+nyzo_withdraws)
withdraws_df = pd.DataFrame(index = range(len(btc_nyzo_withdraws[0])), columns=sell_cols)

withdraws_df['Type'] = 'TRANSFER'
withdraws_df['Exchange'] = 'Nan'
withdraws_df['Costs/Proceeds'] = 'NaN'
withdraws_df['Costs/Proceeds currency'] = 'NaN'
withdraws_df['Sync Holdings'] = 'NaN'
withdraws_df['Sent/Received from'] = 'qTrade'
withdraws_df['Sent to'] = 'MY_WALLET'
withdraws_df['Notes'] = 'WITHDRAW'

for x in range(len(btc_nyzo_withdraws[0])):
    withdraws_df['Base amount'].iloc[x] = btc_nyzo_withdraws[0][x][1][0]
    withdraws_df['Fee'].iloc[x] = btc_nyzo_withdraws[0][x][1][1]
    withdraws_df['Fee currency'].iloc[x] = btc_nyzo_withdraws[0][x][0]
    withdraws_df['Base currency'].iloc[x] = btc_nyzo_withdraws[0][x][0]
    withdraws_df['Date'].iloc[x] = btc_nyzo_withdraw_timestamps[0][x]

withdraws_df = withdraws_df[sell_cols]





trades_withdraws = pd.concat([withdraws_df, full_trade_df], axis=0)





deposit_history = api.get("https://api.qtrade.io/v1/user/deposits").json()
json_str = json.dumps(deposit_history)
resp = json.loads(json_str)

btc_net_deposits = []
for x in range(len(resp['data']['deposits'])):
    if resp['data']['deposits'][x]['currency'] == 'BTC':
        btc_net_deposits.append(float(resp['data']['deposits'][x]['amount']))

btc_net_deposits = np.sum(btc_net_deposits, 0)

btc_net_deposits = np.around(btc_net_deposits, decimals=8)





btc_deposits = []
for x in range(len(resp['data']['deposits'])):
    if resp['data']['deposits'][x]['currency'] == 'BTC':
        btc_deposits.append((resp['data']['deposits'][x]['currency'] , float(resp['data']['deposits'][x]['amount'])))





nyzo_deposits = []
for x in range(len(resp['data']['deposits'])):
    if resp['data']['deposits'][x]['currency'] == 'NYZO':
        nyzo_deposits.append((resp['data']['deposits'][x]['currency'] , float(resp['data']['deposits'][x]['amount'])))





btc_deposit_timestamps = []
for x in range(len(resp['data']['deposits'])):
    if resp['data']['deposits'][x]['currency'] == 'BTC':
        btc_deposit_timestamps.append(pd.to_datetime(resp['data']['deposits'][x]['created_at']).strftime('%Y-%m-%d %H:%M:%S'))





nyzo_deposit_timestamps = []
for x in range(len(resp['data']['deposits'])):
    if resp['data']['deposits'][x]['currency'] == 'NYZO':
        nyzo_deposit_timestamps.append(pd.to_datetime(resp['data']['deposits'][x]['created_at']).strftime('%Y-%m-%d %H:%M:%S'))





btc_nyzo_deposit_timestamps = []
btc_nyzo_deposit_timestamps.append(btc_deposit_timestamps+nyzo_deposit_timestamps)





btc_nyzo_deposit = []
btc_nyzo_deposit.append(btc_deposits+nyzo_deposits)
deposit_df = pd.DataFrame(index = range(len(btc_nyzo_deposit[0])), columns=sell_cols)

deposit_df['Type'] = 'DEPOSIT'
deposit_df['Exchange'] = 'NaN'
deposit_df['Costs/Proceeds'] = 'NaN'
deposit_df['Costs/Proceeds currency'] = 'NaN'
deposit_df['Sync Holdings'] = 'NaN'
deposit_df['Sent/Received from'] = 'MINING'
deposit_df['Sent to'] = 'qTrade'
deposit_df['Notes'] = 'NaN'
deposit_df['Fee'] = '0'
deposit_df['Fee currency'] = 'NaN'

for x in range(len(btc_nyzo_deposit[0])):
    deposit_df['Base amount'].iloc[x] = btc_nyzo_deposit[0][x][1]
    deposit_df['Base currency'].iloc[x] = btc_nyzo_deposit[0][x][0]
    deposit_df['Date'].iloc[x] = btc_nyzo_deposit_timestamps[0][x]





final_import_df = pd.concat([trades_withdraws, deposit_df], axis=0)
final_import_df.to_csv('nyzo_import.csv')
