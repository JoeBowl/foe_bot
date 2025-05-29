from find_key_paths import find_key_paths
from sendRequest import collectReward
import json
import copy

# From data, checks all hidden rewards and collects them
def collectAllReward(data, server_time, driver, account, verbose=False):
    _, reward_ids = checkCollectAllReward(data, server_time, verbose=False)
    
    if reward_ids == []:
        return None
        
    for hiddenRewardId in reward_ids:
        response = collectReward(hiddenRewardId, driver, account)
        
        if verbose == True:
            print(response)
                
    return response


# From data, checks all hidden rewards
def checkCollectAllReward(data, server_time, verbose = True, debug_verbose = False):
    paths = find_key_paths(data, 'requestClass', 'HiddenRewardService')
    
    # Pick the first path
    path = paths[0][:-1]  # remove the last key to get to the parent object
    
    # Get the hidden rewards data
    rewards_data = copy.deepcopy(data)
    for key in path:
        rewards_data = rewards_data[key]
    
    reward_names = []
    reward_ids = []
    for reward_data in rewards_data["responseData"]["hiddenRewards"]:
        reward_startTime = reward_data["startTime"]
        
        if server_time >= reward_startTime and server_time < reward_data["expireTime"]:
            reward_name = reward_data["type"]
            reward_id = reward_data["hiddenRewardId"]
            
            reward_names.append(reward_name)
            reward_ids.append(reward_id)
            
            if verbose:
                print(reward_id, reward_name)
        
    if debug_verbose:
        print(json.dumps(rewards_data, indent=2))
        print(paths)
        print(data[13] == data[22])
        print(path)
            
    return reward_names, reward_ids
        




if __name__ == "__main__":
    print(checkCollectAllReward(data, verbose=True))
    # getServerTime(data)