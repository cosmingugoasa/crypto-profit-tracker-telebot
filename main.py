import telebot
import os
from dotenv import load_dotenv
import json
import util

load_dotenv()

# release API_KEY
# debug API_KEY_DEV
bot = telebot.TeleBot(os.getenv("API_KEY_DEV"), parse_mode="HTML")

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
    "<i>Check your profit on that crypto</i>\n\n" +

     "⚙️\n<b>/[pref]</b> [preference] [value]\n" +
     "<i>ex : /pref currency usd</i>\n" +
     "<i>available preferences: " + ", ".join(util.pref_list) + "</i>\n" +
     "<i>Set a profile preference</i>\n\n"
    )

############################################################################

@bot.message_handler(commands=['reg'])
def reg(message):
    owner = message.from_user.full_name

    if (util.checkIfUserExists(owner) == True):
        bot.reply_to(message, "⚠️ User <b>" + message.from_user.full_name + "</b> alredy exists. Contact admin.")
        exit()

    util.regUser(owner, message.text.split(" ")[1])

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
    crypto_name = message.text.split(" ")[1].upper()
    investment = message.text.split(" ")[2]

    try:
        util.addInvestmentToJson(owner, crypto_name, investment)
    except:
        bot.send_message(message.chat.id, "⚠️ Failed to add investment")

    bot.send_message(message.chat.id, "✅ Added investment of <b>" + investment + "</b> on <b>" + crypto_name.upper() + "</b> for <b>" + message.from_user.full_name + "</b>")

############################################################################

@bot.message_handler(commands=['pref'])
def pref(message):
    split = message.text.split(" ")

    # check number of arguments
    if len(split) != 3:
        bot.send_message(message.chat.id, "Wrong number of arguments")
        return

    pref = split[1].lower()
    val = split[2].lower()

    # preference exists
    if not util.checkPrefExists(pref):
        bot.send_message(message.chat.id, "Preference " + split[1] + " doesn't exists")
        return

    # pref vaule exists
    if not util.checkPrefValueExists(pref, val):
        bot.send_message(message.chat.id, "Value not possible, available choices:\n" +
                         ", ".join(util.getPreferenceValues(pref)))
        return

    ret_val = util.setPreference(message.from_user.full_name, pref, val)
    if ret_val:
        bot.send_message(message.chat.id, "ok!")
    else:
        bot.send_message(message.chat.id, "Fail")

############################################################################

@bot.message_handler(regexp="\/")
def crypto_fetch(message):

    # check in json if investement for this crypto and user exists
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

    balance = util.simulateTradeToBUSD(crypto_address, bsc_scan['balance'])
    if(balance == None):
        bot.reply_to(message, "Error in simulateTradeToBUSD")
        return

    symbol = "$"
    if util.getPreference(message.from_user.full_name, "currency") == "eur":
        balance = util.BUSDtoEUR(balance)
        symbol = "€"

    if balance is None:
        bot.reply_to(message, "BUSDtoEUR")
        return

    profit = float(balance) - float(investment)
    color = "🔴"
    if profit > 0.0:
        color = "🟢"

    bot.send_message(message.chat.id,
        "<b>" + message.from_user.full_name + "</b> your profit on <b>" +
        message.text[1:].upper() + "</b> is : \n" +
        color + "    <b>" + symbol + " {:.2f}".format(float(profit)) + "</b>")


############################################################################

bot.polling()
