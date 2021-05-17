import util
from dotenv import load_dotenv
import os
import json

load_dotenv()

#get details from bscscan
token = json.loads(util.getTokenBalanceFromBSCscan(os.getenv("HODL"), os.getenv("WALLET_ADRESS")))
print("➜ " + token['name'] + " : " + token['balance'])

#bnb based crypto (trade : my_crypto -> bnb -> eur)
busdBalance = util.simulateTradeToBUSD(token['name'], token['balance'])
print(" ➜  USD : " + busdBalance)
eurBalance = util.BUSDtoEUR(busdBalance)
print(" ➜   EUR : " + str(eurBalance))
print("➜ Profit : " + str(float(eurBalance) - float(os.getenv("INVESTMENT"))))