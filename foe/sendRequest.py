from signature_generator2 import generateRequestPayloadSignature
import json

def collectTavern(driver, account):
    request_id = account.last_request_id + 1
    payload = [
        {
            "__class__": "ServerRequest",
            "requestData": [],
            "requestClass": "FriendsTavernService",
            "requestMethod": "collectReward",
            "requestId": request_id
        }
    ]
    return(sendRequest(driver, payload, account))

def getTavernData(driver, account):
    request_id = account.last_request_id + 1
    payload = [
        {
            "__class__": "ServerRequest",
            "requestData": [],
            "requestClass": "FriendsTavernService",
            "requestMethod": "getOwnTavern",
            "requestId": request_id
        }
    ]
    return(sendRequest(driver, payload, account))

def FriendTavern(friendId, driver, account):
    request_id = account.last_request_id + 1
    payload = [
        {
            "__class__": "ServerRequest",
            "requestData": [friendId],
            "requestClass": "FriendsTavernService",
            "requestMethod": "getOtherTavern",
            "requestId": request_id
        }
    ]
    return(sendRequest(driver, payload, account))

def collectAutoAid(autoAidId, driver, account):
    request_id = account.last_request_id + 1
    payload = [
        {
            "__class__": "ServerRequest",
            "requestData": [autoAidId],
            "requestClass": "AutoAidService",
            "requestMethod": "collect",
            "requestId": request_id
        }
    ]
    return(sendRequest(driver, payload, account))

def startAutoAid(autoAidId, driver, account):
    request_id = account.last_request_id + 1
    payload = [
        {
            "__class__": "ServerRequest",
            "requestData": [autoAidId],
            "requestClass": "AutoAidService",
            "requestMethod": "start",
            "requestId": request_id
        }
    ]
    return(sendRequest(driver, payload, account))

def collectQuest(questId, driver, account):
    request_id = account.last_request_id + 1
    payload = [
        {
            "__class__": "ServerRequest",
            "requestData": [questId],
            "requestClass": "QuestService",
            "requestMethod": "advanceQuest",
            "requestId": request_id
        }
    ]
    return(sendRequest(driver, payload, account))

# Sends a collectReward request and returns the server's response
def collectReward(hiddenRewardId, driver, account):
    request_id = account.last_request_id + 1
    payload = [
        {
            "__class__": "ServerRequest",
            "requestData": [hiddenRewardId],
            "requestClass": "HiddenRewardService",
            "requestMethod": "collectReward",
            "requestId": request_id
        }
    ]
    return(sendRequest(driver, payload, account))

# Sends a pickupProduction request and returns the server's response
def pickupProduction(building_ids, driver, account):
    request_id = account.last_request_id + 1
    payload = [
        {
            "__class__": "ServerRequest",
            "requestData": [building_ids],
            "requestClass": "CityProductionService",
            "requestMethod": "pickupProduction",
            "requestId": request_id
        }
    ]
    return(sendRequest(driver, payload, account))

# Sends a startProduction request and returns the server's response
def startProduction(building_id, production_time, driver, account):
    request_id = account.last_request_id + 1
    payload = [
        {
            "__class__": "ServerRequest",
            "requestData": [building_id, production_time],
            "requestClass": "CityProductionService",
            "requestMethod": "startProduction",
            "requestId": request_id
        }
    ]
    return(sendRequest(driver, payload, account))
        
    
      



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
    return json.dumps(filtered_headers)

def get_url(logs):
    for request in reversed(logs):
        if "forgeofempires.com/game/json?h=" in request.url:
            return request.url[0:35]

def sendRequest(driver, payload, account):
    user_key = account.user_key
    logs = account.get_log_request_old()
    
    signature = generateRequestPayloadSignature(payload, account.user_key, account.salt)
    print(payload, user_key, signature)
    
    # Serialize the payload to a JSON string
    payload_json = json.dumps(payload).replace(' ', '')
    
    headers = get_header(account, signature)
    url = get_url(logs)
    
    # Define the fetch request as an asynchronous script
    fetch_script = f"""
    var callback = arguments[arguments.length - 1];
    fetch("{url}/json?h={user_key}", {{
      "headers": {headers},
      "referrer": "{url}/index?",
      "referrerPolicy": "strict-origin-when-cross-origin",
      "body": JSON.stringify({payload_json}),
      "method": "POST",
      "mode": "cors",
      "credentials": "include"
    }})
    .then(response => response.json())
    .then(data => {{
        callback({{'status': 'success', 'data': data}});
    }})
    .catch(error => {{
        callback({{'status': 'error', 'message': error.toString()}});
    }});
    """

    # Execute the asynchronous fetch request
    result = driver.execute_async_script(fetch_script)

    # Handle the result in Python
    if result['status'] == 'success':
        # print("Fetch request successful!")
        return(result)
    else:
        print("Fetch request failed!")
        print("Error Message:", result['message'])
        
if __name__ == "__main__":
    user_key = "pvmVvLRrE_Hs_iPykfMuDomD"
    payload = [
        {
            "__class__": "ServerRequest",
            "requestData": [37,1],
            "requestClass": "CityProductionService",
            "requestMethod": "startProduction",
            "requestId": 11
        }
    ]
    
    data = sendRequest(driver, payload, user_key, log_request)