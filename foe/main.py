# General imports
import datetime
import pathlib
import time
import json
import os

# Get the directory where the current script is located
script_dir = pathlib.Path(__file__).parent.resolve()  # Works in Python 3.6+
os.chdir(script_dir)    # Change the working directory to the script's directory

# Selenium imports, used to open the browser and have access to requests and responses
from seleniumwire import webdriver  # note the change here
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException

# Class and script imports
from models.account import Account
from models.city import City
from sendRequest import getTavernData
from interceptRequest import intercept_request_id
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
city = City()
account = Account()

last_request_time = time.time()  # Track the last request timestamp

# Define the request interceptor function
def request_interceptor(request):
    global last_request_time
    last_request_time = time.time()
    account.log_request(request)
    
    if "forgeofempires.com/game/json?h=" in request.url:
        last_user_key = account.user_key
        user_key = account.get_user_key()
        if last_user_key != user_key:
            account.user_key = user_key
            print(f"The user key is: {user_key}")
            
        last_request_id = intercept_request_id(request, account, verbose=True)
        account.last_request_id = last_request_id

# Define the response interceptor function with two parameters: request and response
def response_interceptor(request, response):
    account.log_response(request, response)
    
    if 'ForgeHX' in request.url:
        account.salt = account.get_salt(request, response, verbose=True)
        
    if "forgeofempires.com/game/json?h=" in request.url:
        request_body = request.body.decode('utf-8')
        
        if "getData" in request_body:
            city.get_data(request, response)
            city.get_buildings_data(request, response)
            print("Data updated!")
            print("Buildings data updated!")
            
        if "LogService" in request_body:
            account.server_time = account.get_server_time(request, response)
            print("Server time updated!")
            
        if ("HiddenRewardService" in request_body) or ("getData" in request_body):
            city.get_hidden_rewards_data(request, response)
            print("Hidden rewards data updated!")
            
        if "pickupProduction" in request_body:
            city.update_buildings_data(request, response)
            print("Buildings data updated!")


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







import tkinter as tk

def button1_action():
    top_n = 15
    building_ids, building_names, building_pfs = checkPickupBestPFProduction(city.buildings_data, top_n, verbose=False)
    
    # Print results
    msg = f"Top {top_n} Buildings with Highest PFs:"
    for building_id, name, pfs in zip(building_ids, building_names, building_pfs):
        msg = msg + "\n" + f"Name: {name} id: {building_id} PFs: {pfs}"
    display_message(msg)
    # width, height = check_size(btn1)
    # display_message(f"Button 1 size: {width}x{height}px")

def button2_action():
    top_n = 15
    pickupBestPFProduction(city.buildings_data, driver, account, top_n=top_n, verbose=True)
    display_message(f"Top {top_n} Buildings Collected!")
    
def button3_action():
    building_ids, building_names = checkPickupAllProduction(city.buildings_data, verbose=False)
    
    # Print results
    msg = f"Buildings Ready to Pick Up:"
    for building_id, name in zip(building_ids, building_names):
        msg = msg + "\n" + f"Name: {name} id: {building_id}"
    display_message(msg)
    
def button4_action():
    pickupAllProduction(city.buildings_data, driver, account, verbose=True)
    display_message(f"All Finished Productions Collected!")
    
def button5_action():
    reward_names, reward_ids = checkCollectAllReward(city.hidden_rewards_data, account.server_time, verbose = False)
    
    # Print results
    msg = f"Hidden Rewards Ready to Collect:"
    for reward_name, reward_id in zip(reward_names, reward_ids):
        msg = msg + "\n" + f"Name: {reward_name} id: {reward_id}"
    display_message(msg)
    
def button6_action():
    collectAllReward(city.hidden_rewards_data, account.server_time, driver, account, verbose=True)
    display_message(f"All Hidden Rewards Collected!")
    
def check_size(button):
    button.update_idletasks()
    return(button.winfo_width(), button.winfo_height())

# NEW FUNCTION: Add messages to display
def display_message(message):
    display_area.configure(state='normal')  # Enable editing
    display_area.insert(tk.END, message + "\n")  # Add message
    display_area.configure(state='disabled')  # Disable editing
    display_area.see(tk.END)  # Auto-scroll to bottom

# Create main window
root = tk.Tk()
root.title("Simple Button UI")
root.geometry("600x400")  # Increased height for display area

# NEW: Create display area with scrollbar
display_frame = tk.Frame(root)
display_frame.place(x=10, y=10, width=580, height=150)

scrollbar = tk.Scrollbar(display_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

display_area = tk.Text(display_frame, yscrollcommand=scrollbar.set, state='disabled')
display_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=display_area.yview)

# Create buttons (adjusted y-positions)
btn1 = tk.Button(root, text="print best pf production", command=button1_action, height=2, width=20)
btn2 = tk.Button(root, text="collect best production", command=button2_action, height=2, width=20)
btn3 = tk.Button(root, text="print finished production", command=button3_action, height=2, width=20)
btn4 = tk.Button(root, text="collect finished production", command=button4_action, height=2, width=20)
btn5 = tk.Button(root, text="print hidden rewards", command=button5_action, height=2, width=20)
btn6 = tk.Button(root, text="collect hidden rewards", command=button6_action, height=2, width=20)

# Place buttons (positioned below display area)
btn1.place(x=10, y=170)    # 170 instead of 10
btn2.place(x=440, y=170)   # 170 instead of 10
btn3.place(x=10, y=220)    # 220 instead of 60
btn4.place(x=440, y=220)   # 220 instead of 60
btn5.place(x=10, y=270)    # 220 instead of 60
btn6.place(x=440, y=270)   # 220 instead of 60

root.mainloop()



# checkPickupBestPFProduction(data, top_n=15)
# collectBestPFs = input("collect best? (yes) or (no)")
# if collectBestPFs == "yes":
#     pickupBestPFProduction(data, driver, account, top_n=15, verbose=True)
#     time.sleep(500/1000)
#     driver.refresh()
#     
# 
# checkPickupAllProduction(data)
# collectAllPFs = input("collect all? (yes) or (no)")
# if collectAllPFs == "yes":
#     pickupAllProduction(data, driver, account, verbose=True)
#     time.sleep(500/1000)
#     driver.refresh()
#     
#     
# checkPickupBestPFProduction(data)
# collectBestPFs = input("collect best blue galaxy test? (yes) or (no)")
# if collectBestPFs == "yes":
#     pickupBlueGalaxyAndBestPFProduction(data, driver, account, verbose=True)
#     time.sleep(500/1000)
#     driver.refresh()
    
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