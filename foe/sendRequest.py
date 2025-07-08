from signature_generator2 import generateRequestPayloadSignature
import json

async def collectTavern(driver, account):
    payload = [
        {
            "__class__": "ServerRequest",
            "requestData": [],
            "requestClass": "FriendsTavernService",
            "requestMethod": "collectReward",
            "requestId": account.last_request_id + 1
        }
    ]
    return await sendRequest(driver, payload, account)

async def getTavernData(driver, account):
    payload = [
        {
            "__class__": "ServerRequest",
            "requestData": [],
            "requestClass": "FriendsTavernService",
            "requestMethod": "getOwnTavern",
            "requestId": account.last_request_id + 1
        }
    ]
    return await sendRequest(driver, payload, account)

async def FriendTavern(friendId, driver, account):
    payload = [
        {
            "__class__": "ServerRequest",
            "requestData": [friendId],
            "requestClass": "FriendsTavernService",
            "requestMethod": "getOtherTavern",
            "requestId": account.last_request_id + 1
        }
    ]
    return await sendRequest(driver, payload, account)

async def collectAutoAid(autoAidId, driver, account):
    payload = [
        {
            "__class__": "ServerRequest",
            "requestData": [autoAidId],
            "requestClass": "AutoAidService",
            "requestMethod": "collect",
            "requestId": account.last_request_id + 1
        }
    ]
    return await sendRequest(driver, payload, account)

async def startAutoAid(autoAidId, driver, account):
    payload = [
        {
            "__class__": "ServerRequest",
            "requestData": [autoAidId],
            "requestClass": "AutoAidService",
            "requestMethod": "start",
            "requestId": account.last_request_id + 1
        }
    ]
    return await sendRequest(driver, payload, account)

async def collectQuest(questId, driver, account):
    payload = [
        {
            "__class__": "ServerRequest",
            "requestData": [questId],
            "requestClass": "QuestService",
            "requestMethod": "advanceQuest",
            "requestId": account.last_request_id + 1
        }
    ]
    return await sendRequest(driver, payload, account)

# Sends a collectReward request and returns the server's response
async def collectReward(hiddenRewardId, driver, account):
    payload = [
        {
            "__class__": "ServerRequest",
            "requestData": [hiddenRewardId],
            "requestClass": "HiddenRewardService",
            "requestMethod": "collectReward",
            "requestId": account.last_request_id + 1
        }
    ]
    return await sendRequest(driver, payload, account)

# Sends a pickupProduction request and returns the server's response
async def pickupProduction(building_ids, driver, account):
    payload = [
        {
            "__class__": "ServerRequest",
            "requestData": [building_ids],
            "requestClass": "CityProductionService",
            "requestMethod": "pickupProduction",
            "requestId": account.last_request_id + 1
        }
    ]
    return await sendRequest(driver, payload, account)

# Sends a startProduction request and returns the server's response
async def startProduction(building_id, production_time, driver, account):
    payload = [
        {
            "__class__": "ServerRequest",
            "requestData": [building_id, production_time],
            "requestClass": "CityProductionService",
            "requestMethod": "startProduction",
            "requestId": account.last_request_id + 1
        }
    ]
    return await sendRequest(driver, payload, account)
        
    
      


def get_header(account, signature):    
    # Get the last POST request (to copy headers)
    last_post_request = account.get_last_log(url="forgeofempires.com/game/json?h=", method="POST")['request']
    
    # Check if a POST request was found
    if last_post_request is None:
        raise RuntimeError("Fatal Error: No POST requests found in the logs at function sendRequest.get_header.")
    
    # print(last_post_request.headers)
    headers_dict = last_post_request.headers
    
    keys_to_include = [
        "accept",
        "accept-language",
        "client-identification",
        "content-type",
        "priority",
        "user-agent",
        "sec-ch-ua",
        "sec-ch-ua-mobile",
        "sec-ch-ua-platform",
        "sec-fetch-dest",
        "sec-fetch-mode",
        "sec-fetch-site"
    ]
    
    filtered_headers = {key: headers_dict[key] for key in keys_to_include if key in headers_dict}
    filtered_headers['signature'] = signature
    return filtered_headers

def get_url(logs):
    for request in reversed(logs):
        if "forgeofempires.com/game/json?h=" in request.url:
            return request.url[0:35]

async def sendRequest(driver, payload, account):
    user_key = account.user_key
    logs = account.get_log_request_old()

    signature = generateRequestPayloadSignature(payload, account.user_key, account.salt)
    print(payload, user_key, signature)

    payload_json = json.dumps(payload, separators=(',', ':'))  # remove unnecessary whitespace
    headers = get_header(account, signature)
    url = get_url(logs)
    
    full_url = f"{url}/json?h={user_key}"

    # print(full_url)
    # print(type(full_url))
    # print(payload_json)
    # print(type(payload_json))
    # print(headers)
    # print(type(headers))
    
    # Use Playwright's request API
    try:
        response = await driver.context.request.post(
            full_url,
            data=payload_json,
            headers=headers,
            # You can also add extra options here like timeout, etc.
        )
        response_json = await response.json()
        
        return(response_json)

    except Exception as e:
        print(f"sendRequest: Request failed with exception: {e}")
        return None