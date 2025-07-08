import tkinter as tk
import threading
import asyncio
import json
import logging
import threading
from playwright.async_api import async_playwright

# Class and script imports
from models.account import Account
from models.city import City
from sendRequest import getTavernData
from interceptRequest import route_interceptor
from gameActions.pickupAllProduction import pickupAllProduction, pickupBestPFProduction, checkPickupAllProduction, checkPickupBestPFProduction, pickupBlueGalaxyAndBestPFProduction
from gameActions.startAllProduction import startAllProduction, checkStartAllProduction
from gameActions.startAllProduction import startAllGoods, checkStartAllGoods
from gameActions.startAllProduction import startAllMilitary, checkStartAllMilitary
from gameActions.collectAllReward import collectAllReward, checkCollectAllReward
from gameActions.collectAllQuest import collectAllQuest, checkCollectAllQuest
from gameActions.allAutoAid import allAutoAid, checkallAutoAid
from gameActions.allFriendTavern import allFriendTavern, checkAllFriendTavern
from gameActions.collectFullTavern import collectFullTavern, checkCollectFullTavern

def start_async_loop():
    loop = asyncio.new_event_loop()
    threading.Thread(target=loop.run_forever, daemon=True).start()
    return loop
    
# Global background asyncio loop
ASYNC_LOOP = start_async_loop()
    
class App:
    def __init__(self, root, city, account):
        self.root = root
        self.city = city
        self.account = account
        self.driver = None  # Will hold the Playwright page object
        self.current_action = 0

        self.root.title("Simple Button UI")
        self.root.geometry("600x400")

        self.display_frame = tk.Frame(root)
        self.display_frame.place(x=10, y=10, width=580, height=150)

        self.scrollbar = tk.Scrollbar(self.display_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.display_area = tk.Text(self.display_frame, yscrollcommand=self.scrollbar.set, state='disabled')
        self.display_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.display_area.yview)

        # Buttons
        self.btn1 = tk.Button(root, text="Show top 15 pf", command=self.button1_action, height=2, width=20)
        self.btn2 = tk.Button(root, text="Collect top 15 pf", command=self.button2_action, height=2, width=20)
        self.btn3 = tk.Button(root, text="Show finished prod.", command=self.button3_action, height=2, width=20)
        self.btn4 = tk.Button(root, text="Collect finished prod.", command=self.button4_action, height=2, width=20)
        self.btn5 = tk.Button(root, text="Show hidden rewards", command=self.button5_action, height=2, width=20)
        self.btn6 = tk.Button(root, text="Collect hidden rewards", command=self.button6_action, height=2, width=20)

        self.btn1.place(x=10, y=170)
        self.btn2.place(x=440, y=170)
        self.btn3.place(x=10, y=220)
        self.btn4.place(x=440, y=220)
        self.btn5.place(x=10, y=270)
        self.btn6.place(x=440, y=270)

        # Start Playwright in background
        self.playwright_thread = threading.Thread(target=self.start_playwright, daemon=True)
        self.playwright_thread.start()

    def display_message(self, message):
        self.display_area.configure(state='normal')
        self.display_area.insert(tk.END, message + "\n")
        self.display_area.configure(state='disabled')
        self.display_area.see(tk.END)

    def check_size(self, button):
        button.update_idletasks()
        return (button.winfo_width(), button.winfo_height())

    def button1_action(self):
        top_n = 15
        building_ids, building_names, building_pfs = checkPickupBestPFProduction(self.city.buildings_data, top_n, verbose=False)
        msg = f"Top {top_n} Buildings with Highest PFs:"
        for building_id, name, pfs in zip(building_ids, building_names, building_pfs):
            msg += f"\nName: {name} id: {building_id} PFs: {pfs}"
        self.display_message(msg)

    def button2_action(self):
        self.current_action = 2

    def button3_action(self):
        building_ids, building_names = checkPickupAllProduction(self.city.buildings_data, verbose=False)
        msg = f"Buildings Ready to Pick Up:"
        for building_id, name in zip(building_ids, building_names):
            msg += f"\nName: {name} id: {building_id}"
        self.display_message(msg)

    def button4_action(self):
        self.current_action = 4

    def button5_action(self):
        reward_names, reward_ids = checkCollectAllReward(self.city.hidden_rewards_data, self.account.server_time, verbose=False)
        msg = f"Hidden Rewards Ready to Collect:"
        for reward_name, reward_id in zip(reward_names, reward_ids):
            msg += f"\nName: {reward_name} id: {reward_id}"
        self.display_message(msg)
        
    def button6_action(self):
        self.current_action = 6

    def start_playwright(self):
        asyncio.run(self.playwright_task())

    async def playwright_task(self):
        with open('config.json') as f:
            config = json.load(f)

        LOGIN_URL = config["URL"]
        worldname = config["worldname"]
        username = config["username"]
        password = config["password"]

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                devtools=True,              # 👈 Open DevTools automatically
                args=["--mute-audio"]       # Optional: mute browser audio
            )
            context = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context.new_page()
            self.driver = page  # Save the driver for button actions
            
            async def request_interceptor(request):
                account.log_request(request)
                
                if "forgeofempires.com/game/json?h=" in request.url:
                    user_key = account.get_user_key()
                    if account.user_key != user_key:
                        account.user_key = user_key
                        print(f"The user key is: {user_key}")
        
            async def response_interceptor(response):
                account.log_response(response)
                
                if 'ForgeHX' in response.request.url:
                    account.salt = await account.get_salt(response, verbose=True)

                if "forgeofempires.com/game/json?h=" in response.request.url:
                    request_body = response.request.post_data
                    
                    if "getData" in request_body:
                        await city.get_data(response)
                        await city.get_buildings_data(response)
                        print("Data updated!")
                        print("Buildings data updated!")
                        
                    if "LogService" in request_body:
                        await account.get_server_time(response, verbose=True)
                        # print("Server time updated!")
                        
                    if ("HiddenRewardService" in request_body) or ("getData" in request_body):
                        await city.get_hidden_rewards_data(response)
                        print("Hidden rewards data updated!")
                        
                    if ("pickupProduction" in request_body) or ("UseItemOnBuildingPayload" in request_body) or ("UseGridItemPayload" in request_body):
                        await city.update_buildings_data(response)
                        print("Buildings data updated!")

            # Add interceptors
            page.on("request", request_interceptor)
            page.on("response", response_interceptor)
            
            # Add route handler
            await page.route("**/*", route_interceptor(account, verbose=True))

            # Navigate to the website
            await page.goto(LOGIN_URL)

            # Playwright automatically waits for elements to be visible and interactable
            username_field = await page.wait_for_selector('#page_login_always-visible_input_player-identifier', timeout=30000)
            password_field = await page.wait_for_selector('#page_login_always-visible_input_password', timeout=30000)

            await username_field.fill(username)
            await password_field.fill(password)

            # Click login button
            login_button = await page.wait_for_selector('#page_login_always-visible_button_login', timeout=30000)
            await login_button.click()

            # Wait and click 'Play Now' button
            play_now_button = await page.wait_for_selector('#play_now_button', timeout=30000)
            await play_now_button.click()

            # Wait and click world selection button
            world_button = await page.wait_for_selector(f"//a[@class='world_select_button' and text()='{worldname}']", timeout=30000)
            await world_button.click()

            print("Login complete. Listening for requests...")
            
            try:
                while True:
                    await asyncio.sleep(1)
                    
                    if self.current_action == 2:
                        top_n = 15
                        await pickupBestPFProduction(self.city.buildings_data, self.driver, self.account, top_n=top_n, verbose=True)
                        self.display_message(f"Top {top_n} Buildings Collected!")
                        self.current_action = 0
                        
                    elif self.current_action == 4:
                        await pickupAllProduction(self.city.buildings_data, self.driver, self.account, verbose=True)
                        self.display_message(f"All Finished Productions Collected!")
                        self.current_action = 0
                        
                    elif self.current_action == 6:
                        await collectAllReward(self.city.hidden_rewards_data, self.account.server_time, self.driver, self.account, verbose=True)
                        self.display_message(f"All Hidden Rewards Collected!")
                        self.current_action = 0
                        
            except asyncio.CancelledError:
                await browser.close()
                print("Browser closed.")


# ----------- Launch the App ----------- #
if __name__ == "__main__":
    city = City()
    account = Account()

    root = tk.Tk()
    app = App(root, city, account)
    root.mainloop()