from find_key_paths import find_key_paths
from sendRequest import collectTavern
import json

# From data
def collectFullTavern(tavern_data, driver, user_key, request_id):
    paths = find_key_paths(tavern_data, 'requestMethod', 'getOwnTavern')
    
    for path in paths:
        tavernInfo = tavern_data[path[0]][path[1]]['responseData']['view']
        unlockedChairs = tavernInfo['unlockedChairs']
        n_visitors = len(tavernInfo['visitors'])
        availableChairs = unlockedChairs - n_visitors
        
        if availableChairs == 0:
            collectTavern(driver, user_key, request_id)
            print("Tavern collected!")
            request_id += 1
        
    return(request_id)


# From data
def checkCollectFullTavern(tavern_data):
    paths = find_key_paths(tavern_data, 'requestMethod', 'getOwnTavern')
    
    for path in paths:
        tavernInfo = tavern_data[path[0]][path[1]]['responseData']['view']
        unlockedChairs = tavernInfo['unlockedChairs']
        n_visitors = len(tavernInfo['visitors'])
        availableChairs = unlockedChairs - n_visitors
        
        if availableChairs == 0:
            print("Tavern Full!")
        else:
            print("Unlocked Tavern Chairs:", unlockedChairs)
        
        
if __name__ == "__main__":
    checkCollectFullTavern(tavern_data)