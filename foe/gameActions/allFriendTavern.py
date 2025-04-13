from find_key_paths import find_key_paths
from sendRequest import FriendTavern
import json

# From data, checks all hidden rewards and collects them
def allFriendTavern(data, driver, user_key, request_id):
    paths = find_key_paths(data, 'requestMethod', 'getOtherTavernStates')
    
    for path in paths:
        for friendsTavernInfo in data[path[0]][path[1]]['responseData']:
            ownerId = friendsTavernInfo['ownerId']
            player_name = getPlayerName(ownerId, data)
            
            if 'state' in friendsTavernInfo:
                continue
            
            FriendTavern(ownerId, driver, user_key, request_id=0)
            request_id += 1
            print(f"Sat on {player_name}'s tavern, id: {ownerId}")
        
    return(request_id)


# From data, checks all hidden rewards
def checkAllFriendTavern(data):
    paths = find_key_paths(data, 'requestMethod', 'getOtherTavernStates')
    
    for path in paths:
        for friendsTavernInfo in data[path[0]][path[1]]['responseData']:
            ownerId = friendsTavernInfo['ownerId']
            player_name = getPlayerName(ownerId, data)
            
            if 'state' in friendsTavernInfo:
                continue
            
            print("name:", player_name, "id:", ownerId)
            # print(json.dumps(friendsTavernInfo, indent=2))
        
def getPlayerName(player_id, data):
    paths = find_key_paths(data, 'player_id', player_id)
    
    for path in paths:
        player_info = data[path[0]][path[1]][path[2]][path[3]][path[4]]
        
        if 'name' in player_info:
            return(player_info['name'])
        
    return('Name not found')


if __name__ == "__main__":
    checkAllFriendTavern(data)