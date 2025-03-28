from find_key_paths import find_key_paths
from sendRequest import collectReward
import json

# From data, checks all hidden rewards and collects them
def collectAllReward(data, driver, user_key, request_id):
    paths = find_key_paths(data, '__class__', 'HiddenReward')
    
    for path in paths:
        hiddenRewardInfo = data[path[0]][path[1]][path[2]][path[3]][path[4]]
        name = hiddenRewardInfo['type']
        hiddenRewardId = hiddenRewardInfo['hiddenRewardId']
        rarity = hiddenRewardInfo['rarity']
        
        collectReward(hiddenRewardId, driver, user_key, request_id)
        request_id += 1
        
        print(name, rarity, "collected")
            
    return(request_id)


# From data, checks all hidden rewards
def checkCollectAllReward(data):
    paths = find_key_paths(data, '__class__', 'HiddenReward')
    
    for path in paths:
        hiddenRewardInfo = data[path[0]][path[1]][path[2]][path[3]][path[4]]
        hiddenRewardId = hiddenRewardInfo['hiddenRewardId']
        name = hiddenRewardInfo['type']
        rarity = hiddenRewardInfo['rarity']
        
        print("Name:", name, "rarity:", rarity, "id:", hiddenRewardId)
        # print(json.dumps(hiddenRewardInfo, indent=2))
        
if __name__ == "__main__":
    checkCollectAllReward(data)