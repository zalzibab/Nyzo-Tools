NYZO-MANAGER

Nyzo Manager is a Python CLI tool for quickly viewing your NYZO balances across all verifiers, wallets, and your qTrade account

Input your verifier/wallet nicknames (does not have to be the nickname attached to the verifier) in the list at line 30 and the Public IDs for each of those in the list at line 32. Add your qTrade API where specified at line 77

You will receive individualized and totalled amounts of NYZO holdings, as well as the BTC values of all holdings at the current best bid, front of the order book (lowest ask - 1 satoshi), and orderbook mid point between best bid and lowest ask

Create and append csv file to track NYZO holdings and "best_ask" BTC value over time
Render chart showing historical holdings and BTC value


NYZO-JOURNAL

This script pulls your NYZO buy/sell and withdraw/deposit history from your qTrade account and reformats the data to be imported into the Delta Portfolio Tracker App

Run the script and import transactions from csv. Output file will be named <nyzo_import.csv>

*Known limitations*
-Script only pulls your last 200 completed trades for all qTrade markets. So if you are heavily active trading NYZO or trade many pairs on qTrade, there is a chance you will be missing some earlier data points
-Due to how Delta processes Deposit txs, Deposits are marked as {"From": "MINING"}
-Due to how Delta processes Withdraw/Transfer txs, withdraws are marked as {"Type": "TRANSFER"}. You will need to then go in and manually update all NYZO {"Type": "TRANSFER"} txs to a "Sell" and leave the Market as NYZO/NYZO and Price as 1

*Recommended/Upcoming Updates*
-Perform a readfile function to search for existing nyzo_import.csv file and append txs to that file, performing a dropby("Date", keep=Last) operation to amend new trades to existing csv
-Alternative: Use the qTrade py-client module to read only NYZO trade data and make use of newer_than paramater to pull trade data only from last tx recorded


NYZO Donation address: id__87ErmbZKKb5b.wt_KMqJQ-_DWCw9cc9PmyjrF_zj3JHz9Ez~8jQJ
