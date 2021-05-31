import threading
import telebot
import os
from dotenv import load_dotenv
import util
from datetime import datetime

from selenium import webdriver

load_dotenv()

# release API_KEY
# debug API_KEY_DEV
bot = telebot.TeleBot(os.getenv("API_KEY"), parse_mode="HTML")

print("Starting bot ...")

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

    "🔭\n<b>/showinv</b>\n" + 
    "<i>ex : /showinv</i>\n" +
    "<i>Show all the investments you made (BSC only for now)</i>\n\n" +

    "🗑\n<b>/rm</b> [token/coin name]\n" + 
    "<i>ex : /rm feg</i>\n" +
    "<i>Remove an investment you made (BSC only for now)</i>\n\n" +

    "📈\n<b>/addcontract</b> [token/coin name] [contract address]\n" + 
    "<i>ex : /addcontract reth 0x00000000</i>\n" +
    "<i>Add a contract to contract list (BSC only for now)</i>\n\n" +

    "🚀\n<b>/[cryptoname]</b>\n" + 
    "<i>ex : /feg</i>\n" +
    "<i>Check your profit on that crypto</i>\n\n" +

     "⚙️\n<b>/pref</b> [preference] [value]\n" +
     "<i>ex : /pref currency usd</i>\n" +
     "<i>available preferences: " + ", ".join(util.pref_list) + "</i>\n" +
     "<i>Set a profile preference</i>\n\n"

     "📋️\n<b>/portfolio</b>\n" +
     "<i>List status of all the user's crypto</i>\n\n"
    )

############################################################################

@bot.message_handler(commands=['reg'])
def reg(message):
    user = message.from_user.full_name
    
    print(message.text + " request from " + user + " on thread #" + str(threading.get_ident()) + " " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    #check number of arguments
    if len(message.text.split(" ")) > 2:
        bot.send_message(message.chat.id ,"⚠️ Invalid number of arguments")
        return
    
    address = message.text.split(" ")[1]
    
    #check wallet format validity
    if address[:2] != "0x":
        bot.send_message(message.chat.id ,"⚠️ Invalid wallet address format")
        return

    util.regUser(user, address)

    bot.send_message(message.chat.id, "✅ Registered : <b>" + user + "</b>")

############################################################################

@bot.message_handler(commands=['addcontract'])
def addc(message):
    user = message.from_user.full_name
    print(message.text + " request from " + user + " on thread #" + str(threading.get_ident()) + " " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    #check number of arguments
    if len(message.text.split(" ")) != 3:
        bot.send_message(message.chat.id ,"⚠️ Invalid number of arguments")
        return

    crypto_name = message.text.split(" ")[1].upper()
    crypto_contract = message.text.split(" ")[2]

    #check wallet format validity
    if crypto_contract[:2] != "0x":
        bot.send_message(message.chat.id ,"⚠️ Invalid wallet address format")
        return

    try:
        util.addContractToJson(crypto_name, crypto_contract)
        bot.send_message(message.chat.id, "✅ Added <b>" + crypto_name + "</b> @" + crypto_contract)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "⚠️ Something went wrong")

############################################################################


@bot.message_handler(commands=['add'])
def add(message):
    user = message.from_user.full_name
    print(message.text + " request from " + user + " on thread #" + str(threading.get_ident()) + " " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    #check number of arguments
    if len(message.text.split(" ")) != 3:
        bot.send_message(message.chat.id ,"⚠️ Invalid number of arguments")
        return


    crypto_name = message.text.split(" ")[1].upper()
    investment = 0 

    #checks if investment value is a valid float 
    try:
        investment = float(message.text.split(" ")[2])
    except:
        bot.send_message(message.chat.id ,"⚠️ Invalid investment value")
        return

    try:
        util.addInvestmentToJson(user, crypto_name, investment)
        bot.send_message(message.chat.id, "✅ Added investment of <b>" + str(investment) + "</b> on <b>" + crypto_name.upper() + "</b> for <b>" + message.from_user.full_name + "</b>")
    except:
        bot.send_message(message.chat.id, "⚠️ Failed to add investment")

    

############################################################################

@bot.message_handler(commands=['showinv'])
def showinv(message):

    user = message.from_user.full_name
    
    print(message.text + " request from " + user + " on thread #" + str(threading.get_ident()) + " " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    
    #check number of arguments
    if len(message.text.split(" ")) != 1:
        bot.send_message(message.chat.id ,"⚠️ Invalid number of arguments")
        return
    
    try:
        if util.getPreference(user, "currency") == "eur":
            symbol = "€"
        else:
            symbol = "$"

        result = util.showInvestments(user)
        str_result = "🔭 <b>" + user + "</b>'s Investments:\n"
        for key in result:
            str_result += key + " : " + str(result[key]["investment"]) + " " + symbol +"\n"

        bot.send_message(message.chat.id , str_result)
    except Exception as e:
        bot.send_message(message.chat.id ,"⚠️ Something went wrong")
        print(e)
    

############################################################################

@bot.message_handler(commands=['rm'])
def rm(message):
    user = message.from_user.full_name
    print(message.text + " request from " + user + " on thread #" + str(threading.get_ident()) + " " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    #check number of arguments
    if len(message.text.split(" ")) > 2 or len(message.text.split(" ")) < 2 :
        bot.send_message(message.chat.id ,"⚠️ Invalid number of arguments")
        return

    
    crypto_name = message.text.split(" ")[1].upper()

    # check in json if investement for this crypto and user exists
    investment = util.getInvestmentOfFromJson(user, crypto_name) 
    if (investment == None):
        bot.send_message(message.chat.id, "⚠️ Your poor ass doesn't have this crypto")
        return

    util.rmInvestmentFromJson(user, crypto_name)

    bot.send_message(message.chat.id, "✅ Removed investment on <b>" + crypto_name.upper() + "</b> for <b>" + message.from_user.full_name + "</b>")

############################################################################

@bot.message_handler(commands=['portfolio'])
def reg(message):
    user = message.from_user.full_name

    print(message.text + " request from " + user + " on thread #" + str(threading.get_ident()) + " " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    # check number of arguments
    if len(message.text.split(" ")) > 1:
        bot.send_message(message.chat.id, "⚠️ Invalid number of arguments")
        return

    # check if user exists
    if not util.checkIfUserExists(user):
        bot.send_message(message.chat.id, "⚠️ User does not exists, please register first")
        return

    # get list of investments for user
    crypto_list = util.getAllCryptoForUser(user)

    result_dict = {}

    # create driver instance for this request
    driver = webdriver.Chrome(util.chromeDriverPath, options=util.options)

    time = 5 * len(crypto_list)
    bot.send_message(message.chat.id, "⏳ Gimme ~" + str(time) +" seconds ...")

    owner_address = util.getOwnerAddressFromJson(user)

    for item in crypto_list:

        crypto_address = util.getCryptoAddressFromJson(item)
        bsc_scan = util.getTokenBalanceFromBSCscan(driver, crypto_address, owner_address)

        investment = util.getInvestmentOfFromJson(user, item)

        error = False

        if bsc_scan is None:
            error = True

        if not error:
            balance = util.simulateTradeToBUSD(driver, crypto_address, bsc_scan['balance'])

        if balance is None:
            error = True

        if not error:
            symbol = "$"
            if util.getPreference(user, "currency") == "eur":
                balance = util.BUSDtoEUR(driver, balance)
                symbol = "€"

        if balance is None:
            error = True

        if not error:
            profit = float(balance) - float(investment)
            color = "🔴"
            if profit > 0.0:
                color = "🟢"

            result_dict[item] = color + "<b>" + symbol + " {:.2f}".format(float(profit)) + "</b> - ATH : " + " {:.2f}".format(float(util.getPersonalAth(user, item)))
                     # "🛒 Amount : " + " {:.3f}".format(float(bsc_scan['balance'].replace(",", "")))
        else:
            result_dict[item] = item + ": <i>Error</i>"

    driver.quit()

    string_result = "📋 <b>" + user + "</b>'s Portfolio:\n"

    # if i have cryptos to display
    if result_dict:
        for key, val in result_dict.items():
            string_result += "\n " + str(key) + ":" + "   " + val
    else:
        string_result += "\nPortfolio is empty, stay poor"

    bot.send_message(message.chat.id, string_result)


############################################################################

@bot.message_handler(commands=['pref'])
def pref(message):
    user = message.from_user.full_name
    print(message.text + " request from " + user + " on thread #" + str(threading.get_ident()) + " " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

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

    user = message.from_user.full_name
    
    print(message.text + " request from " + user + " on thread #" + str(threading.get_ident()) + " " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    
    #check number of arguments
    if len(message.text.split(" ")) > 1:
        bot.send_message(message.chat.id ,"⚠️ Invalid number of arguments")
        return
    
    crpyto_name = message.text[1:].upper()

    # check in json if investement for this crypto and user exists
    investment = util.getInvestmentOfFromJson(user, crpyto_name) 
    if (investment == None):
        bot.reply_to(message, "⚠️ Your poor ass doesn't have this crypto")
        return

    #create driver instance for this request
    driver = webdriver.Chrome(util.chromeDriverPath, options=util.options)

    bot.send_message(message.chat.id, "⏳ Gimme ~5 seconds ...")

    crypto_address = util.getCryptoAddressFromJson(crpyto_name)
    owner_address = util.getOwnerAddressFromJson(user)

    bsc_scan = util.getTokenBalanceFromBSCscan(driver, crypto_address, owner_address)
    
    if(bsc_scan == None):
        bot.reply_to(message, "Error in getTokenBalanceFromBSCscan")
        return

    chartLink = ""
    if util.getPreference(user, "chart") == "poocoin":
        chartLink = util.getPoocoinChart(crypto_address)
    elif util.getPreference(user, "chart") == "dexguru":
        chartLink = util.getDexguruChart(crypto_address)
    elif util.getPreference(user, "chart") == "bogged":
        chartLink = util.getBoggedChart(crypto_address)

    balance = util.simulateTradeToBUSD(driver, crypto_address, bsc_scan['balance'])
    if(balance == None):
        bot.reply_to(message, "Error in simulateTradeToBUSD")
        return

    symbol = "$"
    if util.getPreference(user, "currency") == "eur":
        balance = util.BUSDtoEUR(driver, balance)
        symbol = "€"

    if balance is None:
        bot.reply_to(message, "BUSDtoEUR")
        return

    profit = float(balance) - float(investment)

    #check personal ath
    personal_ath = float(util.getPersonalAth(user, crpyto_name))
    if profit > personal_ath or personal_ath == 0:
        personal_ath = "Now"
        util.setPersonalAth(user, crpyto_name, profit)        
    else:
        personal_ath = "{:.2f}".format(float(profit))

    color = "🔴"
    if profit > 0.0:
        color = "🟢"

    bot.send_message(message.chat.id,
        "<b>" + user + "</b> your profit on <b>" +
        message.text[1:].upper() + "</b> is : \n" +
        color + "    <b>" + symbol + " {:.2f}".format(float(profit)) + "</b>\n" +
        "🔝 ATH : " + personal_ath + "\n" + 
        "🛒 Amount : " + " {:.3f}".format(float(bsc_scan['balance'].replace(",",""))) + 
        "\n🔗 <a href=\"" + chartLink + "\"> Chart </a> " 
        , disable_web_page_preview = True)

    driver.quit()


############################################################################

bot.polling()
