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
from datetime import datetime, timezone
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import os.path
import matplotlib.dates as mdates
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import gridspec
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
from matplotlib.pyplot import figure

def get_balance(url, wallet_id):
    page = urlopen(url+wallet_id)
    soup = BeautifulSoup(page, features="lxml")
    balance = soup.body.find('div', attrs={'id' : 'currentBalance'}).text
    balance = balance[16:]
    return balance

#Leave 'url' variable unchanged
url = 'https://nyzo.co/wallet?id='
#Replace Sample with the nicknames for each of your verifiers/wallets
nicknames = ['Sample', 'Sample', 'Sample']
#Replace Sample with the public ID for each of your verifiers/wallets. Length of list should match length of nicknames list
wallet_ids = ['Sample', 'Sample', 'Sample']    

wallet_balances = []
wallet_tuples = []
wallets_dict = 0
for x in range(len(wallet_ids)):
    wallet_balances.append(get_balance(url, wallet_ids[x]))
    wallet_tuples.append(tuple((nicknames[x], float(wallet_balances[x]))))
wallets_dict = {k: v for k, v in enumerate(wallet_tuples)}

total_wallet_balance = 0
for x in range(len(wallets_dict)):
    total_wallet_balance += wallets_dict[x][1]
total_wallet_balance = round(total_wallet_balance, 6)

#Initiate API connection to qTrade account

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
api.auth = QtradeAuth("") #Your API Key goes between the quotations here

all_balances = api.get("https://api.qtrade.io/v1/user/balances").json()
for x in range(len(all_balances['data']['balances'])):
        if all_balances['data']['balances'][x]['currency'] == 'NYZO':
            cold_balance = float(all_balances['data']['balances'][x]['balance'])
        else:
            cold_balance = 0.0

if len(all_balances['data']['order_balances']) > 0:
    for x in range(len(all_balances['data']['order_balances'])):
        if all_balances['data']['order_balances'][x]['currency'] == 'NYZO':
            on_order_balance = float(all_balances['data']['balances'][x]['balance'])
else:
    on_order_balance = 0.0
total_qTrade_balance = cold_balance + on_order_balance
total_balance = total_qTrade_balance + total_wallet_balance

ticker = api.get("https://api.qtrade.io/v1/ticker/NYZO_BTC").json()

highest_bid = float(ticker['data']['bid'])
lowest_ask = float(ticker['data']['ask'])
front_of_book = lowest_ask-0.00000001
mid_price = (highest_bid + lowest_ask)/2

best_bid_value = format(total_balance*highest_bid, '.8f')
front_of_book_value = format(total_balance*front_of_book, '.8f')
mid_price_value = format(total_balance*mid_price, '.8f')
highest_bid = format(highest_bid, '.8f')
front_of_book = format(front_of_book, '.8f')
mid_price = format(mid_price, '.8f')
timestamp = datetime.now(tz=None).strftime('%m-%d-%Y %H:%M')
message = f"""All Wallets & Verifiers: {total_wallet_balance}
qTrade Balance: {total_qTrade_balance}
Total NYZO Holdings: {total_balance}
Best Bid Value @ {highest_bid}: {best_bid_value}
Front Of Book Value @ {front_of_book}: {front_of_book_value}
Mid Price Value @ {mid_price}: {mid_price_value}"""

print(str(timestamp))
for k, v in wallets_dict.items():
    print(str(v[0])+': '+str(v[1]))
print(message+'\n')

dictionary = {'Date': timestamp}
for x,y in wallet_tuples:
    dictionary[x] = y
dictionary['qTrade'] = total_qTrade_balance
dictionary['Total'] = total_wallet_balance
dictionary['btcValue'] = front_of_book_value

if os.path.isfile('nyzo_holdings.csv'):
    nyzo_balances_df = pd.read_csv('nyzo_holdings.csv', index_col=0)
    new_values_df = pd.DataFrame(data=dictionary, index=[0])
    new_values_df['Change'] = 0
    nyzo_balances_df = nyzo_balances_df.append(new_values_df, ignore_index=True, sort=True)
    nyzo_balances_df['Change'].iloc[-1] = (nyzo_balances_df['Total'].iloc[-1]-nyzo_balances_df['Total'].iloc[-2])
    nyzo_balances_df.to_csv('nyzo_holdings.csv')
    
    fig = plt.figure(figsize=(18,10))
    gs1 = gridspec.GridSpec(2, 1, height_ratios=[1, 1])

    x_axis = nyzo_balances_df['Date']
    ax1 = plt.subplot(gs1[0])
    plt.plot(x_axis, nyzo_balances_df['Total'], label='Current_Total_Nyzo'+'\n'+str(total_balance))
    plt.ylabel('Total_Nyzo', fontdict={'fontsize': 24})
    plt.title('Nyzo_Holdings_History', fontdict={'fontsize': 32})
    plt.legend()
    ax1.xaxis_date()
    ax1.set_axisbelow(True)
    plt.grid(b=None, which='major', axis='both')
    plt.tick_params(axis='x', which='both', top=False, bottom=False, labelbottom=False)
    plt.tick_params(axis='y', which='both', left=True, right=True, labelleft=True, labelright=True)

    ax2 = plt.subplot(gs1[1], sharex=ax1)
    plt.plot(x_axis, nyzo_balances_df['btcValue'])
    plt.ylabel('BTC_Value', fontdict={'fontsize': 24})
    plt.tick_params(axis='x', which='both', top=False, bottom=True, labeltop=False, labelbottom=True)
    plt.tick_params(axis='y', which='both', left=True, right=True, labelleft=True, labelright=True)
    plt.grid(b=None, which='major', axis='both')
    ax2.set_axisbelow(True)
    plt.autoscale(tight=True)
    plt.tight_layout()
    plt.subplots_adjust(top=0.85, bottom=0.07, left=0.07, right=0.93, hspace=0, wspace=0)
    plt.savefig('nyzo_holdings.png', bbox_inches='tight',dpi=100)
    plt.clf()

else:
    nyzo_balances_df = pd.DataFrame(data=dictionary, index=[0])
    nyzo_balances_df['Change'] = 0
    nyzo_balances_df.to_csv('nyzo_holdings.csv')
