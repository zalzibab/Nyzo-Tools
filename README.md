Input your verifier/wallet nicknames (does not have to be the nickname attached to the verifier) in the list at line 30 and the Public IDs for each of those in the list at line 32. Add your qTrade API where specified at line 77

You will receive individualized and totalled amounts of NYZO holdings, as well as the BTC values of all holdings at the current best bid, front of the order book (lowest ask - 1 satoshi), and orderbook mid point between best bid and lowest ask

To keep a daily record of your holdings and value, you can create a cronjob with the following format after making the nyzo_manager.py executable and changing the PATH variable on line 1 of the script to the proper value

0 0 * * * <PATH_TO_SCRIPT>/nyzo_manager.py >> nyzo_holdings.txt

NYZO Donation address: id__87ErmbZKKb5b.wt_KMqJQ-_DWCw9cc9PmyjrF_zj3JHz9Ez~8jQJ
