from time import sleep
from dotenv import load_dotenv
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

load_dotenv()
chromeDriverPath = os.getenv("CHROME_DRIVER_PATH")

options = Options()
options.add_argument("--headless")
options.add_argument("--log-level=3")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--mute-audio")
driver = webdriver.Chrome(chromeDriverPath, options=options)

#get token balance, specifying token contract adress and wallet adress
def getTokenBalanceFromBSCscan(tokenAdress, walletAdress):
    try:
        driver.get("https://bscscan.com/token/" + tokenAdress + "?a=" + walletAdress)
        
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

#trade your_crypto for bnb simulation, than extract trade info
def simulateTradeToBUSD(tokenAddress, amount):
    driver.get("https://exchange.pancakeswap.finance/#/swap")
    
    #insert HODL as starting crypto
    try:
        fromButton = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"swap-currency-input\"]/div/div[2]/button"))
        )
        fromButton.click()
    except Exception as e:
        print("Couldnt click 'From crypto button'")
        return None
    
    #enter for confirming hodl adress
    try:
        fromWhatCryptoInput = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"token-search-input\"]"))
        )
        fromWhatCryptoInput.send_keys(tokenAddress)
        sleep(1)
        fromWhatCryptoInput.send_keys(Keys.RETURN)
    except Exception as e:
        print("Error inserting token adress")
        return None

    #insert hodl amount
    try:  
        amountCryptoInput = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"swap-currency-input\"]/div/div[2]/input"))
        )
        amountCryptoInput.click()
        sleep(1)
        amountCryptoInput.send_keys(amount.replace(",",""))
    except:
        print("Error inserting hodl amount")
        return None

    #select busd as output
    try:
        bnbSelectButton = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"swap-currency-output\"]/div/div[2]/button"))
        )
        bnbSelectButton.click()
        bnbSelectInput = driver.find_element_by_xpath("//*[@id=\"token-search-input\"]")
        bnbSelectInput.send_keys("BUSD")
        bnbSelectInput.send_keys(Keys.ENTER)
        sleep(1)
    except Exception as e:
        print("Couldnt select busd as output")
        return None

    #extracting busd amount from transaction
    try:
        outputBUSDAmount = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"root\"]/div[2]/div[1]/div/div[2]/div/div[3]/div[3]/div/div/div/div[1]/div[2]/div"))
        )
        return outputBUSDAmount.text.split(" ")[0]
    except Exception as e:
        print("Couldnt print output balance.\n" + e)
        return None

#change from bnb to eur
def BUSDtoEUR(amount):

    #get eur to dollar value
    driver.get("https://www.xe.com/it/currencyconverter/convert/?Amount=1&From=USD&To=EUR")
    try:
        EURtoUSD = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"__next\"]/div[2]/div[2]/section/div[2]/div/main/form/div[2]/div[1]/p[2]"))
        )
        EURtoUSD = EURtoUSD.text.split(" ")[0].replace(',','.')
        #print(" ➜   USD to EUR rate : " + EURtoUSD)
    except Exception as e:
        print("Couldnt get EUR to USD value")
        return None

    myBNBvalueInEUR = float(amount) * float(EURtoUSD)
    return myBNBvalueInEUR

#######################################################
#                   JSON utility                      #
#######################################################
def getInvestmentOfFromJson(owner, crypto):
    with open("users.json") as f:        
        data = json.load(f)
        for user in data:
            if(user == owner):
                for entry in data[user]:
                    entries = list(entry.items())
                    for key, value in entries:
                        if(key == "crypto" and value == crypto):
                            return entries[+1][1]
        
    return None

def updateJson(json_data):
    with open("users.json") as f:        
        data = json.load(f)
        #check if user exists and update only
        for user in data:
            if(user == str(json_data)[2:].split("'")[0]):
                data[user].append((json_data[str(json_data)[2:].split("'")[0]])[0])
                return data

        #if user not found create it
        data.update(json_data)        
        return data

def rewriteJson(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

def checkIfUserExists(user):
    with open("users.json") as f:        
        data = json.load(f)
        #check if user exists and update only
        for _user in data:
            if(_user == user):
                return True
        
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
            return data[owner][0]["address"]
        except:
            return None

def addContractToJson(crypto_name, crypto_address):
    json_contract = {
        crypto_name.upper() : crypto_address
    }

    with open("contracts.json") as f:        
        data = json.load(f)
        data.update(json_contract)
    
    with open("contracts.json", "w") as f:
        json.dump(data, f, indent=4)
