# Bob-The-Builder

## Pre-req
- Python Version: 3.13.9
- venv
- Perplexity API Key
- Telegram Bot API Key
- *Both perplexity API key and telegram bot API keys are not made know as they are store in a SECRET file. To replicate, please create a `.env` and store secrets in this project root directory.*

`.env` should look like this:
```
TG_BOT_API_TOKEN="KEY HERE"
PERPLEXITY_API_KEY="KEY HERE"
```

## Installation
1. *Create venv for workplace & activate*:
As always, we dont want to mess up the laptop, so we create a venv for us to work in peace
```
# for unix/macos
python3 -m venv .env
source .venv/bin/activate

# for windows
py-m venv .venv
.venv\Scripts\activate

# if you want to deactivate just type the below
dactivate
```

2. *Install dependencies/freezing dependencies*: Install base dependencies from requirement.txt, and if you update, freeze it

```
## install from requirements.txt
# for windows
py -m pip install -r requirements.txt

# for unix/macos
python3 -m pip install -r requirements.txt

## if you install new libaries or dependencies, update requirements.txt
pip freeze > requirements.txt
```

3. *Running the code like nodemon*: If you edit sth and then wanna test the bot, no need to keep typing python main.py. Just do below it repeats upon edits in scripts
```
#do in terminal
pymon main.py
```
# Workspace Structure
```
├── config.py   (handles secret variables from .env file for usage in workspace ltr)
├── handlers    (handlers are like /start, /profile commands you see in your tele bot)
│   ├── __init__.py (use your defined functions and expose them at a package level for modularity)
│   ├── energy.py   (provides thresholds on kcals for user to be recommended better food/snacks)
│   ├── foodSearch.py  (helper functions to extract webn-crawled food data from HPB)
│   ├── profile.py  (handles profile of the user, including creating profile, updating, deleting etc.)
│   ├── response.py (for use to handle responses to and from using perplexity api)
│   ├── states.py  (inits VARS to be used in the proj directories)
│   └── start.py    (defines what happens in the /start function)
├── foodSearch    (web scrapping feature to get food nutrition info from HPB)
│   ├── csvToJson.py (converting webscrapped food details from HPB website to json format)
│   ├── food  (contains all food nutrition info web scrapped in csv format)
│   ├── foodData.json (ontains all food nutrition info web scrapped in json format)
│   └── webscraper.py    (defines functions to webscrap from HPB website)
├── main.py (to run the static hosted bot from this file)
├── perplexityClient.py (defines the perplexity model to be used and the engineered prompt to send to the bot)
├── requirements.txt    (list of dependencies)
├── .env   (im sorry i cant share this...)
├── storeUserData.py    (define methods on how to extract, save, and delete user profile upon request)
└── userData.json   (for first timers, this file will be automatically created after profiling. delete if you wanna create new user. for existing users it should store user metadata)

```


