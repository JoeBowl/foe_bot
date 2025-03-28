from find_key_paths import find_key_paths
from sendRequest import collectQuest
import json

# From data, checks all hidden rewards and collects them
def collectAllQuest(data, driver, user_key, request_id):
    paths = find_key_paths(data, '__class__', 'Quest')
    
    for path in paths:
        questInfo = data[path[0]][path[1]][path[2]][path[3]]
        name = questInfo['headline']
        questId = questInfo['id']
        state = questInfo['state']
        
        if state == 'collectReward':
            collectQuest(questId, driver, user_key, request_id)
            request_id += 1
        
    return(request_id)


# From data, checks all hidden rewards
def checkCollectAllQuest(data):
    paths = find_key_paths(data, '__class__', 'Quest')
    
    for path in paths:
        questInfo = data[path[0]][path[1]][path[2]][path[3]]
        name = questInfo['headline']
        questId = questInfo['id']
        state = questInfo['state']
        
        print("Name:", name, "id:", questId, "state:", state)
        # print(json.dumps(questInfo, indent=2))
        
if __name__ == "__main__":
    checkCollectAllQuest(data)