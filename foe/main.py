import time
import json

from seleniumwire import webdriver  # note the change here
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException

from signature_generator2 import generateRequestPayloadSignature
from sendRequest import getTavernData
from getData import getData, getRequestId, getUserKey, getSalt, intercept_request_id
from gameActions.pickupAllProduction import pickupAllProduction, pickupBestPFProduction, checkPickupAllProduction, checkPickupBestPFProduction, pickupBlueGalaxyAndBestPFProduction
from gameActions.startAllProduction import startAllProduction, checkStartAllProduction
from gameActions.startAllProduction import startAllGoods, checkStartAllGoods
from gameActions.startAllProduction import startAllMilitary, checkStartAllMilitary
from gameActions.collectAllReward import collectAllReward, checkCollectAllReward
from gameActions.collectAllQuest import collectAllQuest, checkCollectAllQuest
from gameActions.allAutoAid import allAutoAid, checkallAutoAid
from gameActions.allFriendTavern import allFriendTavern, checkAllFriendTavern
from gameActions.collectFullTavern import collectFullTavern, checkCollectFullTavern

# Load credentials from the config.json file
with open('config.json') as f:
    config = json.load(f)
LOGIN_URL = config["URL"]
worldname = config["worldname"]
username = config["username"]
password = config["password"]

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument("--mute-audio")
# chrome_options.add_argument('--auto-open-devtools-for-tabs')

driver = webdriver.Chrome(options=chrome_options)

log_request = []
log_response = []
last_request_time = time.time()  # Track the last request timestamp
last_request_id = 0
user_key = None
salt = None

# Define the request interceptor function
def request_interceptor(request):
    global last_request_time, last_request_id, user_key
    log_request.append(request)
    last_request_time = time.time()
    
    # Check if the request URL contains 'forgeofempires.com/game/json?h='
    if "forgeofempires.com/game/json?h=" in request.url:
        last_user_key = user_key
        user_key = getUserKey(log_request)
        if last_user_key != user_key:
            
            print(f"The user key is: {user_key}")
            
        last_request_id = intercept_request_id(request, last_request_id, user_key, verbose=True)

# Define the response interceptor function with two parameters: request and response
def response_interceptor(request, response):
    global salt
    log_response.append([request, response])
    
    if 'ForgeHX' in request.url:
        salt = getSalt(request, response, verbose=True)


# Set the interceptors
driver.request_interceptor = request_interceptor
driver.response_interceptor = response_interceptor

# Navigate to the website
driver.get(LOGIN_URL)
wait = WebDriverWait(driver, 30)  # Wait up to 30 seconds
max_wait_time = 30  # Maximum time to wait in seconds
poll_interval = 1   # Time to wait between retries in seconds
start_time = time.time()

while True:
    try:
        # Attempt to find the username and password fields
        username_field = wait.until(EC.element_to_be_clickable((By.ID, 'page_login_always-visible_input_player-identifier')))
        password_field = wait.until(EC.element_to_be_clickable((By.ID, 'page_login_always-visible_input_password')))
        break  # Elements found, exit loop
    except ElementNotInteractableException:
        elapsed_time = time.time() - start_time
        if elapsed_time > max_wait_time:
            print("Login fields did not become interactable in time.")
            break  # Exit loop
        time.sleep(poll_interval)  # Retry after a short delay
            
# Enter credentials
username_field.send_keys(username)
password_field.send_keys(password)

# Submit the login form
login_button = wait.until(EC.element_to_be_clickable((By.ID, 'page_login_always-visible_button_login')))
login_button.click()

# Wait for the 'Play Now' button and click it
play_now_button = wait.until(EC.element_to_be_clickable((By.ID, 'play_now_button')))
play_now_button.click()

# Wait for the world selection button to be clickable
world_button = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[@class='world_select_button' and text()='{worldname}']")))
world_button.click()



# Wait until 5 seconds have passed with no new requests
timeout = 5  # Time to wait for inactivity
while True:
    if time.time() - last_request_time >= timeout:
        print("No new requests for 5 seconds. Continuing execution.")
        break
    time.sleep(0.5)  # Check every 0.5 seconds
# wait_for_input = input("Click to start:")



# Get city data
data = getData(log_response)

checkPickupBestPFProduction(data)
collectBestPFs = input("collect best? (yes) or (no)")
if collectBestPFs == "yes":
    data = getData(log_response)
    pickupBestPFProduction(data, driver, user_key, log_request, verbose=True)
    time.sleep(500/1000)
    driver.refresh()
    
    # Wait until 5 seconds have passed with no new requests
    timeout = 5  # Time to wait for inactivity
    while True:
        if time.time() - last_request_time >= timeout:
            print("No new requests for 5 seconds. Continuing execution.")
            break
        time.sleep(0.1)  # Check every 0.1 seconds

checkPickupAllProduction(data)
collectAllPFs = input("collect all? (yes) or (no)")
if collectAllPFs == "yes":
    data = getData(log_response)
    pickupAllProduction(data, driver, user_key, log_request, verbose=True)
    time.sleep(500/1000)
    driver.refresh()
    
    
    

checkPickupBestPFProduction(data)
collectBestPFs = input("collect best blue galaxy test? (yes) or (no)")
if collectBestPFs == "yes":
    data = getData(log_response)
    pickupBlueGalaxyAndBestPFProduction(data, driver, user_key, log_request, verbose=True)
    time.sleep(500/1000)
    driver.refresh()
    
# blue galaxy - X_OceanicFuture_Landmark3

"""
tavern_data = getTavernData(driver, user_key, request_id)
request_id += 1



# Debug
## Print finished production buildings
print("\nFinished Production Buildings:")
checkPickupAllProduction(data)

## Print idle production buildings
print("\nIdle Production Buildings:")
checkStartAllProduction(data)
checkStartAllGoods(data)
checkStartAllMilitary(data)

# Print hidden rewards
print("\nHidden Rewards:")
checkCollectAllReward(data)

# Print quests
print("\nQuests State:")
checkCollectAllQuest(data)

# Print aid services state
print("\nAuto Aid State:")
checkallAutoAid(data)

# Check friend's taverns
print("\nFriends with available chairs:")
checkAllFriendTavern(data)

# Check if tavern is full
print("\nAvailable seats on own tavern")
checkCollectFullTavern(tavern_data)




production_time = "5 m"
goods_time = "8 h"

production_dict = {"5 m":  1, "15 m": 2, "1 h":  3, "4 h":  4, "8 h":  5, "1 d":  6}
goods_dict = {"4 h":  1, "8 h": 2, "1 d":  3, "2 d":  4}



start = wait_for_input = input("Type \"start\" to start: ")

if start == "start":    
    ## Pick up hidden rewards
    collectAllReward(data, driver, user_key, request_id)
    
    # Loop
    while True:
        data = getData(driver, user_key, request_id)
        request_id += 1
        
        ## Pick up all gold production, goods and military
        request_id = pickupAllProduction(data, driver, user_key, request_id)
        
        data = getData(driver, user_key, request_id)
        request_id += 1
        
        ## Start idle production buildings
        request_id = startAllProduction(data, production_dict[production_time], driver, user_key, request_id)
        request_id = startAllGoods(data, goods_dict[goods_time], driver, user_key, request_id)
        request_id = startAllMilitary(data, driver, user_key, request_id)
        
        ## Collect completed quests
        request_id = collectAllQuest(data, driver, user_key, request_id)
        
        ## Start or collect aid services to neighbors, guild and friends
        request_id = allAutoAid(data, driver, user_key, request_id)
        
        ## Sit on friend's taverns
        request_id = allFriendTavern(data, driver, user_key, request_id)
        
        ## Get own tavern data
        tavern_data = getTavernData(driver, user_key, request_id)
        request_id += 1
        
        ## Collect own tavern, if full
        request_id = collectFullTavern(tavern_data, driver, user_key, request_id)
    
        sleep_time = random.uniform(300, 330)
        print(f"Sleeping for {sleep_time} seconds")
        time.sleep(sleep_time)
        """
# driver.close()  # Closes the browser and stops the WebDriver
a = 1