from test import update_json
import telebot
import os
from dotenv import load_dotenv
import json
import util

load_dotenv()

bot = telebot.TeleBot(os.getenv("API_KEY"), parse_mode="HTML")

@bot.message_handler(commands=['start'])
def start(message):
	bot.send_message(message.chat.id, "Hi " + message.from_user.full_name +"! I'm PTSL's Crypto Bot !")

############################################################################

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 
    "⚒ <b><u>C O M M A N D S</u></b> ⚒\n\n" +

    "👤\n<b>/reg</b> [your wallet address]\n" + 
    "<i>ex : /reg 0x1234567890asdfgh</i>\n" +
    "<i>Register your user with wallet address</i>\n\n" +

    "💸\n<b>/add</b> [token/coin name] [investment]\n" + 
    "<i>ex : /add feg 25</i>\n" +
    "<i>Add an investment you made (BSC only for now)</i>\n\n" +

    "📈\n<b>/addcontract</b> [token/coin name] [contract address]\n" + 
    "<i>ex : /addcontract reth 0x00000000</i>\n" +
    "<i>Add a contract to contract list (BSC only for now)</i>\n\n" +

    "🚀\n<b>/[cryptoname]</b>\n" + 
    "<i>ex : /feg</i>\n" +
    "<i>Check your profit on that crypto</i>\n\n"
    )

############################################################################

@bot.message_handler(commands=['reg'])
def reg(message):
    owner = message.from_user.full_name

    if (util.checkIfUserExists(owner) == True):
        bot.reply_to(message, "⚠️ User <b>" + message.from_user.full_name + "</b> alredy exists. Contact admin.")
        exit()

    json_data = {
        str(owner) : [{
            'address' : str(message.text.split(" ")[1])
        }]
    }

    new_data = util.updateJson(json_data)
    util.rewriteJson(new_data)

    bot.send_message(message.chat.id, "✅ Registered : <b>" + message.from_user.full_name + "</b>")

############################################################################

@bot.message_handler(commands=['addcontract'])
def addc(message):
    crypto_name = message.text.split(" ")[1].upper()
    crypto_contract = message.text.split(" ")[2]
    try:
        util.addContractToJson(crypto_name, crypto_contract)
        bot.send_message(message.chat.id, "✅ Added <b>" + crypto_name + "</b> @" + crypto_contract)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "‼️ Failed to add contract")

############################################################################

@bot.message_handler(commands=['add'])
def add(message):
    owner = message.from_user.full_name
    crypto_name = message.text.split(" ")[1]
    investment = message.text.split(" ")[2]

    json_data = {
        str(owner) : [{
            'crypto' : str(crypto_name).upper(),
            'investment' : float(investment)
        }]
    }
    
    new_data = util.updateJson(json_data)
    util.rewriteJson(new_data)

    bot.send_message(message.chat.id, "✅ Added investment of <b>" + investment + "</b> on <b>" + crypto_name.upper() + "</b> for <b>" + message.from_user.full_name + "</b>")

############################################################################

@bot.message_handler(regexp="\/")
def crypto_fetch(message):

    #check in json if investement for this crypto and user exists
    investment = util.getInvestmentOfFromJson(message.from_user.full_name, message.text[1:].upper()) 
    if (investment == None):
        bot.reply_to(message, "your poor ass doesn't have this crypto")

    bot.send_message(message.chat.id, "⏳ Gimme ~5 seconds ...\n<i>Don't send other commands pls</i>")

    crypto_address = util.getCryptoAddressFromJson(message.text[1:].upper())
    owner_address = util.getOwnerAddressFromJson(message.from_user.full_name)
    bsc_scan = util.getTokenBalanceFromBSCscan(crypto_address, owner_address)
    
    if(bsc_scan == None):
        bot.reply_to(message, "Error in getTokenBalanceFromBSCscan")
        return

    busdBalance = util.simulateTradeToBUSD(crypto_address, bsc_scan['balance'])
    if(busdBalance == None):
        bot.reply_to(message, "Error in simulateTradeToBUSD")
        return
    
    eurBalance = util.BUSDtoEUR(busdBalance)
    if(eurBalance == None):
        bot.reply_to(message, "BUSDtoEUR")
        return

    profit = float(eurBalance) - float(investment)
    if(profit > 0.0):
        bot.send_message(message.chat.id, 
        "<b>" + message.from_user.full_name +  "</b> your profit on <b>" +
        message.text[1:].upper() + "</b> is : \n" +
        "🟢💶   <b>" + "{:.2f}".format(float(profit)) + "</b>")
    else:
        bot.send_message(message.chat.id, 
        "<b>" + message.from_user.full_name +  "</b> your profit on <b>" +
        message.text[1:].upper() + "</b> is : \n" +
        "🔴💶   <b>" + "{:.2f}".format(float(profit)) + "</b>")

############################################################################


bot.polling()
