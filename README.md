# Crypto Profit Tracker Telegram Bot v1.2

## W.I.P.
Currently under development. Working on :
- Reliability
- More functionalities

## Description
Telegram Bot used to check your profit on BSC based shitcoins. Keeps track of users/investments and coins/tokens via json files.
Gathers info via scraping on different sites and returns your profit (total value of your wallet - investment) in Euro.

⚒ **C O M M A N D S** ⚒" 

👤
**/reg*** [your wallet address] <br>
*ex : /reg 0x1234567890asdfgh* <br>
*Register your user with wallet address* <br><br>

💸
**/add** [token/coin name] [investment] <br>
*ex : /add feg 25* <br>
*Add an investment you made (BSC only for now)* <br><br>

🗑
**/rm** [token/coin name] <br>
*ex : /rm feg* <br>
*Remove an investment you made (BSC only for now)* <br><br>

📈
**/addcontract** [token/coin name] [contract address] <br> 
*ex : /addcontract reth 0x00000000* <br>
*Add a contract to contract list (BSC only for now)* <br><br>

🚀
**/[cryptoname]** <br>
*ex : /feg* <br> 
*Check your profit on that crypto* <br> <br>

⚙️
**/[pref]** [preference] [value] <br>
*ex : /pref currency usd* <br>
*Set a profile preference* <br><br>

📋️
**/[portfolio]** <br>
List status of all the user's crypto


### **/...**
 
 ![](/media/cryptoname.png)

## Setup
Install chrome driver for python : 
[**Download**](https://sites.google.com/a/chromium.org/chromedriver/downloads)

Create your own env for this project: 
```sh
$ python -m venv cpt-env
$ ./cpt-env/Scripts/activate
```
Install dependencies from the *requirements.txt*. You **MUST** be in the same folder as the .txt file
```sh
$ pip install -r requirements.txt
```
Create 2 files for user and contracts :
```sh
$ touch users.json
$ touch contracts.json
```
Create a '.env' file in the project folder. And follow the current syntax need :
```sh
CHROME_DRIVER_PATH=<chromedriver.exe path>
API_KEY=<telegram bot api key>
```
## How to use
Open cmd (or any terminal) and go to the project folder and launch the **main** script. As long as the script is running the bot will reply to your commands
```sh
$ cd D:\Documents\Dev\crypto-profit-tracker-telebot
$ python .\main.py 
```

 
