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

def get_balance(url, wallet_id):
    page = urlopen(url+wallet_id)
    soup = BeautifulSoup(page, features="lxml")
    balance = soup.body.find('div', attrs={'id' : 'currentBalance'}).text
    balance = balance[16:]
    return balance

#Leave 'url' variable unchanged
#Replace verifier/wallet nicknames in the 'nicknames' variable

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
json_str = json.dumps(all_balances)
all_balances = json.loads(json_str)
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
json_str = json.dumps(ticker)
ticker = json.loads(json_str)

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
timestamp = datetime.now(tz=None).strftime('%Y-%m-%d %H:%M')
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

