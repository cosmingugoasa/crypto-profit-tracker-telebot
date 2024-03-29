from time import sleep
from dotenv import load_dotenv
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

load_dotenv()
chromeDriverPath = os.getenv("DRIVER_PATH")

options = Options()
options.add_argument("--headless")
options.add_argument("--log-level=3")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--mute-audio")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
#driver = webdriver.Chrome(chromeDriverPath, options=options)

sleep_time = 1.75

pref_list = {
    "currency": ["eur", "usd"],
    "chart": ["poocoin", "dexguru", "bogged"],
    "ath": ["true", "false"]
}

#######################################################
#                 Driver Management                   #
#######################################################

#create chrome driver istance
def createDriver():
    return webdriver.Chrome(chromeDriverPath, options=options)

#kill chrome driver istance
def killDriver(driver):
    driver.quit()

#######################################################
#                     Scraping                        #
#######################################################

# get token balance, specifying token contract adress and wallet adress
def getTokenBalanceFromBSCscan(driver,  tokenAdress, walletAdress):
    try:
        driver.get("https://bscscan.com/token/" + tokenAdress + "?a=" + walletAdress)
        
        sleep(sleep_time)
        #extract balance and token name from page source code
        info = driver.find_element_by_id("ContentPlaceHolder1_divFilteredHolderBalance")
        balanceValue = "".join(info.text).split("\n")[1].split(" ")[0]
        tokenName = "".join(info.text).split("\n")[1].split(" ")[1]
        json_result = {
            'name' : tokenName, 
            'balance': balanceValue
        }
        return json_result
    except:
        return None

# trade your_crypto for bnb simulation, than extract trade info
def simulateTradeToBUSD(driver, tokenAddress, amount):
    driver.get("https://exchange.pancakeswap.finance/#/swap")
    
    #insert HODL as starting crypto
    try:
        fromButton = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"swap-currency-input\"]/div/div[2]/button"))
        )
        fromButton.click()
    except Exception as e:
        print("Couldnt click 'From crypto button'. XPath my not be valid anymore.")
        killDriver(driver)
        return None
    
    #enter for confirming hodl adress
    try:
        #enter token address
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"token-search-input\"]"))).send_keys(tokenAddress)        
        #Click import
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//*[@id=\"root\"]/div[1]/div[2]/div[2]/div[1]/div[2]/div/button[text()=\"Import\"]"))).click()
        #Click checkbox
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//*[@id=\"root\"]/div[1]/div[2]/div[2]/div/div[3]/div/input"))).click()
        #Confirm
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//*[@id=\"root\"]/div[1]/div[2]/div[2]/div/div[3]/button"))).click()
        

    except Exception as e:
        print("Error inserting token adress. XPath my not be valid anymore.")
        print(e)
        killDriver(driver)
        return None

    #insert amount
    try:  
        amountCryptoInput = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[1]/div[1]/div/div[2]/div[1]/div[1]/div/div[2]/input"))
        )
        amountCryptoInput.click()
        sleep(sleep_time)
        
        amountCryptoInput.send_keys(str(amount).replace(",", ""))
    except Exception as e:
        print("Error inserting amount. XPath my not be valid anymore.")
        print(e)
        killDriver(driver)
        return None

    #select busd as output
    try:
        bnbSelectButton = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"swap-currency-output\"]/div/div[2]/button"))
        )
        bnbSelectButton.click()
        bnbSelectInput = driver.find_element_by_xpath("//*[@id=\"token-search-input\"]")
        bnbSelectInput.send_keys("BUSD")
        sleep(sleep_time)
        bnbSelectInput.send_keys(Keys.ENTER)
        
    except Exception as e:
        print("Couldnt select busd as output. XPath my not be valid anymore.")
        killDriver(driver)
        return None

    #extracting busd amount from transaction
    try:
        outputBUSDAmount = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[1]/div[2]/div/div[1]/div[1]/div[2]/div"))
        )
        return outputBUSDAmount.text.split(" ")[0]
    except Exception as e:
        print("Couldnt print output balance. XPath my not be valid anymore.")
        print(e)
        killDriver(driver)
        return None


# change from bnb to eur
def BUSDtoEUR(driver, amount):
    # get eur to dollar value
    driver.get("https://www.google.com/search?q=dollaro+euro&rlz=1C1GCEA_enIT930IT930&sxsrf=AOaemvIcNn-9GVM8EnkNqoUnBO-vyl9-cQ%3A1635168102413&ei=Zq92YdqeGKOFlQfuroW4Dw&ved=0ahUKEwja6ZDv0-XzAhWjQuUKHW5XAfcQ4dUDCA4&uact=5&oq=dollaro+euro&gs_lcp=Cgdnd3Mtd2l6EAMyCQgjECcQRhCCAjIFCAAQgAQyBQgAEMsBMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQywEyBQgAEIAEMgUIABCABDoECCMQJzoLCAAQgAQQsQMQgwE6DgguEIAEELEDEMcBEKMCOgsILhCABBDHARCvAToECAAQQzoKCC4QxwEQowIQQzoKCAAQsQMQgwEQQzoICC4QgAQQsQM6CAgAEIAEELEDOgcIABCxAxBDOg4ILhCABBCxAxDHARCvAToOCC4QgAQQsQMQxwEQ0QM6BwgAEIAEEAo6DwgAEIAEEIcCEBQQRhCCAjoKCAAQgAQQhwIQFDoHCAAQsQMQCjoECAAQCkoECEEYAFD1DFiRMGDpMWgCcAJ4AIABqwGIAdgMkgEDNS45mAEAoAEBwAEB&sclient=gws-wiz")
    try:
        EURtoUSD = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[8]/div/div[9]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div/div/div/div[1]/div/div[1]/div[1]/div[2]/span[1]"))
        )
        EURtoUSD = EURtoUSD.text.split(" ")[0].replace(',','.')
        
        myBNBvalueInEUR = float(amount) * float(EURtoUSD)
        return myBNBvalueInEUR
        
    except Exception as e:
        print("Couldnt get EUR to USD value : \n " + e)
        killDriver(driver)
        return None

    


# get poocoin chart link of specific token
def getPoocoinChart(tokenAddress):
    return "https://poocoin.app/tokens/" + tokenAddress

# get dex.guru chart link of specific token
def getDexguruChart(tokenAddress):
    return "https://dex.guru/token/" + tokenAddress + "-bsc"

# get boggedfinance chart link of specific token
def getBoggedChart(tokenAddress):
    return "https://charts.bogged.finance/?token=" + tokenAddress


#######################################################
#                   JSON utility                      #
#######################################################

def getInvestmentOfFromJson(owner, crypto):
    with open("users.json") as f:        
        data = json.load(f)
        try:
           return data[owner]["crypto"][crypto]["investment"]
        except:
            return None


def checkIfUserExists(user):
    with open("users.json") as f:        
        data = json.load(f)
        try:
            if data[user]:
                return True
        except:
            return False


def getAllCryptoForUser(user):
    with open("users.json") as f:
        data = json.load(f)
        try:
            if data[user]:
                return list(data[user]["crypto"].keys())
        except:
            return False


def getCryptoAddressFromJson(crypto):
    with open("contracts.json") as f:        
        data = json.load(f)
        try:
            return data[crypto]
        except:
            return None

def getOwnerAddressFromJson(owner):
    with open("users.json") as f:        
        data = json.load(f)
        try:
            return data[owner]["address"]
        except:
            return None

def addContractToJson(crypto_name, crypto_address):
    json_contract = {
        crypto_name.upper(): crypto_address
    }

    try:
        with open("contracts.json") as f:        
            data = json.load(f)
            data.update(json_contract)
        
        with open("contracts.json", "w") as f:
            json.dump(data, f, indent=4)
    except:
        print("Errore in addContractToJson()")


# returns possible preferences
def getAvailablePreferences():
    return pref_list.keys()


# returns possible values for preference
def getPreferenceValues(pref):
    return pref_list[pref]


# returns True if preference exists
def checkPrefExists(pref):
    if pref in getAvailablePreferences():
        return True
    else:
        return False


# return requested preference value for user, if exists
def getPreference(owner, pref):
    try:
        with open("users.json") as f:
            data = json.load(f)
            if pref in data[owner]["preferences"].keys():
                return data[owner]["preferences"][pref]
            else:
                False
    except:
        return False



# update a preference in the owner json
# correctness of preference and value must be checked before
# returns True/False if it can write to file
def setPreference(owner, pref, value):
    try:
        with open("users.json") as f:
            data = json.load(f)
            data[owner]["preferences"].update({pref: value})

        with open("users.json", "w") as f:
            json.dump(data, f, indent=4)

    except:
        return False

    return True


# returns True if value exists for preference
def checkPrefValueExists(pref, value):
    if value in getPreferenceValues(pref):
        return True
    else:
        return False



def addInvestmentToJson(owner, crypto, amount):
    json_contract = {
        "investment": float(amount)
    }

    try:
        with open("users.json") as f:        
            data = json.load(f)

            try:
                if data[owner]["crypto"][crypto] :
                    json_contract["investment"] += data[owner]["crypto"][crypto]["investment"]
                    data[owner]["crypto"][crypto].update(json_contract)
            except:
                new_json = {
                    crypto: {
                        "investment": amount,
                        "ath": 0
                    }
                }
                data[owner]["crypto"].update(new_json)
        
        with open("users.json", "w") as f: 
            json.dump(data, f, indent=4)
    except Exception as e:
        print(e)


def showInvestments(owner):
    with open("users.json") as f:        
        data = json.load(f)
        return data[owner]["crypto"]


def rmInvestmentFromJson(owner, crypto):

    with open("users.json") as f:        
        data = json.load(f)  
        del data[owner]["crypto"][crypto]
    
    with open("users.json", "w") as f: 
        json.dump(data, f, indent=4)


# default preferences:
#      currency: eur
#      chart: poocoin
def regUser(owner, address):
    j = {
        owner: {
            "address": address,
            "preferences": {
                "currency": "eur",
                "chart": "poocoin",
                "ath": True
            },
            "crypto":{}
        }
    }
    try:
        with open("users.json") as f:        
            data = json.load(f)  
            data.update(j)

        with open("users.json", "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(e)

def getPersonalAth(owner, crypto):
    try:
        with open("users.json") as f:        
            data = json.load(f)

            return data[owner]["crypto"][crypto]["ath"]
    except Exception as e:
        print(e)
        return None

def setPersonalAth(owner, crypto, amount):
    json_contract = {
        "ath": float(amount)
    }
    
    try:
        with open("users.json") as f:        
            data = json.load(f)

            try:
                data[owner]["crypto"][crypto].update(json_contract)
            except Exception as e:
                print(e)
        
        with open("users.json", "w") as f: 
            json.dump(data, f, indent=4)
    except Exception as e:
        print(e)

#set custom quantity for given crypto
def setQ(owner, crypto, amount):
    q = {
        "quantity" : amount
    }

    try:
        with open("users.json") as f:        
            data = json.load(f)

            try:
                data[owner]["crypto"][crypto].update(q)
            except Exception as e:
                print(e)

        with open("users.json", "w") as f: 
                    json.dump(data, f, indent=4)
    except Exception as e:
        print(e)

def getQ(owner, crypto):
    with open("users.json") as f:        
        data = json.load(f)
        
        try:
            return data[owner]["crypto"][crypto]["quantity"]
        except:
            return None

#check if user's crypto has custom quantity set
def checkIfCustomQ(owner, crypto):
    with open("users.json") as f:        
        data = json.load(f)

        try:
            if(data[owner]["crypto"][crypto]["quantity"]):
                return True
        except:
            return False

def addToWatch(crypto, amount):
    json_contract = {
        crypto.upper(): amount
    }

    try:
        with open("toWatch.json") as f:        
            data = json.load(f)
            data.update(json_contract)
        
        with open("toWatch.json", "w") as f:
            json.dump(data, f, indent=4)
    except:
        print("Errore in addToWatch()")

