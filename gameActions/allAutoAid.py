from find_key_paths import find_key_paths
from sendRequest import collectAutoAid
from sendRequest import startAutoAid
import json

# From data, checks all hidden rewards and collects them
def allAutoAid(data, driver, user_key, request_id):
    paths = find_key_paths(data, 'requestClass', 'AutoAidService')
    
    for path in paths:        
        for autoAidInfo in data[path[0]][path[1]]['responseData']:
            autoAidId = autoAidInfo['id']
            state = autoAidInfo['__class__']
            
            if state == 'AutoAidFinishedState':
                collectAutoAid(autoAidId, driver, user_key, request_id)
                print(autoAidId, "auto aid collected")
                request_id += 1
                break
                
        for autoAidInfo in data[path[0]][path[1]]['responseData']:
            autoAidId = autoAidInfo['id']
            state = autoAidInfo['__class__']
            
            if 'availablePeers' in autoAidInfo:
                startAutoAid(autoAidId, driver, user_key, request_id)
                print(autoAidId, "auto aid started")
                request_id += 1
                break
        
    return(request_id)


# From data, checks all hidden rewards
def checkallAutoAid(data):
    paths = find_key_paths(data, 'requestClass', 'AutoAidService')
    
    for path in paths:        
        for autoAidInfo in data[path[0]][path[1]]['responseData']:
            autoAidId = autoAidInfo['id']
            state = autoAidInfo['__class__']
            
            if state == 'AutoAidFinishedState':
                print("Name:", autoAidId, "state:", "Finished")
                continue
            
        for autoAidInfo in data[path[0]][path[1]]['responseData']:
            autoAidId = autoAidInfo['id']
            state = autoAidInfo['__class__']
            
            if 'availablePeers' in autoAidInfo:
                print("Name:", autoAidId, "state:", "Idle", "availablePeers:", autoAidInfo['availablePeers'])
                continue
                
            # print(json.dumps(autoAidInfo, indent=2))
            
if __name__ == "__main__":
    checkallAutoAidService(data)