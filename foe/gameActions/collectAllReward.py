from find_key_paths import find_key_paths
from sendRequest import collectReward
import json
import copy

# From data, checks all hidden rewards and collects them
def collectAllReward(data, driver, account, verbose=False):
    reward_ids = checkCollectAllReward(data, verbose=False)
    
    if reward_ids == []:
        return None
        
    for hiddenRewardId in reward_ids:
        response = collectReward(hiddenRewardId, driver, account)
        
        if verbose == True:
            print(response)
                
    return response


# From data, checks all hidden rewards
def checkCollectAllReward(data, verbose = True, debug_verbose = False):
    paths = find_key_paths(data, 'requestClass', 'HiddenRewardService')
    server_time = getServerTime(data)
    
    # Pick the first path
    path = paths[0][:-1]  # remove the last key 'requestClass' to get to the parent object
    
    # Get the hidden rewards data
    rewards_data = copy.deepcopy(data)
    for key in path:
        rewards_data = rewards_data[key]
    
    reward_ids = []
    for reward_data in rewards_data["responseData"]["hiddenRewards"]:
        reward_startTime = reward_data["startTime"]
        
        if server_time >= reward_startTime and server_time < reward_data["expireTime"]:
            reward_name = reward_data["type"]
            reward_id = reward_data["hiddenRewardId"]
            
            reward_ids.append(reward_id)
            
            if verbose:
                print(reward_id, reward_name)
        
    if debug_verbose:
        print(json.dumps(rewards_data, indent=2))
        print(paths)
        print(data[13] == data[22])
        print(path)
            
    return reward_ids
        
def getServerTime(data, verbose = False):
    paths = find_key_paths(data, 'requestClass', 'TimeService')
    
    if not paths:
        raise ValueError("getServerTime: No matching path found for requestClass = 'TimeService'")
    
    # Pick the first path
    path = paths[0][:-1]  # remove the last key 'requestClass' to get to the parent object
    
    # Get the time data
    time_data = copy.deepcopy(data)
    for key in path:
        time_data = time_data[key]

    time = int(time_data["responseData"]["time"])
    
    if verbose:
        print(paths)
        print(path)
        print(json.dumps(time_data, indent=2))
        print(time)
    
    return time
        
if __name__ == "__main__":
    print(checkCollectAllReward(data, verbose=True))
    # getServerTime(data)