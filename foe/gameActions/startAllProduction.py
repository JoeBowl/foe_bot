from find_key_paths import find_key_paths
from sendRequest import startProduction
import json

# From data, checks all idle production buildings and starts production
def startAllProduction(data, production_time, driver, user_key, request_id):
    paths = find_key_paths(data, 'type', 'production')
    
    for path in paths:
        if path[3] != 'city_map':
            continue
        
        buildingInfo = data[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]]
        state_class = buildingInfo['state']['__class__']
        
        if state_class != 'IdleState':
            continue
        
        name = buildingInfo['cityentity_id']
        building_id = buildingInfo['id']
        
        startProduction(building_id, production_time, driver, user_key, request_id)
        request_id += 1
        
        print(name, "started")
    
    return(request_id)


# From data, checks all idle production buildings
def checkStartAllProduction(data):
    paths = find_key_paths(data, 'type', 'production')
    
    for path in paths:
        if path[3] != 'city_map':
            continue
        
        buildingInfo = data[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]]
        state_class = buildingInfo['state']['__class__']
        
        if state_class != 'IdleState':
            continue
        
        name = buildingInfo['cityentity_id']
        building_id = buildingInfo['id']
            
        print("Name:", name, "id:", building_id)
        # print(json.dumps(buildingInfo, indent=2))
    

# From data, checks all idle production buildings and starts production
def startAllGoods(data, production_time, driver, user_key, request_id):
    paths = find_key_paths(data, 'type', 'goods')
    
    for path in paths:
        if path[3] != 'city_map':
            continue
        
        buildingInfo = data[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]]
        state_class = buildingInfo['state']['__class__']
        
        if state_class != 'IdleState':
            continue
        
        name = buildingInfo['cityentity_id']
        building_id = buildingInfo['id']
        
        startProduction(building_id, production_time, driver, user_key, request_id)
        request_id += 1
        
        print(name, "started")
    
    return(request_id)


# From data, checks all idle production buildings
def checkStartAllGoods(data):
    paths = find_key_paths(data, 'type', 'goods')
    
    for path in paths:
        if path[3] != 'city_map':
            continue
        
        buildingInfo = data[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]]
        state_class = buildingInfo['state']['__class__']
        
        if state_class != 'IdleState':
            continue
        
        name = buildingInfo['cityentity_id']
        building_id = buildingInfo['id']
            
        print("Name:", name, "id:", building_id)
        # print(json.dumps(buildingInfo, indent=2))
        
        
# From data, checks all idle production buildings and starts production
def startAllMilitary(data, driver, user_key, request_id):
    paths = find_key_paths(data, 'type', 'military')
    
    for path in paths:
        if path[3] != 'city_map':
            continue
        
        buildingInfo = data[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]]
        state_class = buildingInfo['state']['__class__']
        
        if state_class != 'IdleState':
            continue
        
        name = buildingInfo['cityentity_id']
        building_id = buildingInfo['id']
        
        free_slot = -1
        for slot in buildingInfo['unitSlots']:
            if ('unit' in slot) or ('unlocked' not in slot):
                continue
            
            if ('nr' not in slot):
                free_slot = slot['nr']
            else:
                free_slot = slot['nr']
            break
            
        if free_slot != -1:
            startProduction(building_id, free_slot, driver, user_key, request_id)
            request_id += 1
            print(name, "started")
    
    return(request_id)


# From data, checks all idle production buildings
def checkStartAllMilitary(data):
    paths = find_key_paths(data, 'type', 'military')
    
    for path in paths:
        if path[3] != 'city_map':
            continue
        
        buildingInfo = data[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]]
        state_class = buildingInfo['state']['__class__']
        
        if state_class != 'IdleState':
            continue
        
        name = buildingInfo['cityentity_id']
        building_id = buildingInfo['id']
        
        free_slot = -1
        for slot in buildingInfo['unitSlots']:
            if ('unit' in slot) or ('unlocked' not in slot):
                continue
            
            if ('nr' not in slot):
                free_slot = slot['nr']
            else:
                free_slot = slot['nr']
            break
        
        if free_slot != -1:
            print("Name:", name, "id:", building_id, 'free slot:', free_slot)
            # print(json.dumps(buildingInfo, indent=2))
        
        
if __name__ == "__main__":
    # checkStartAllProduction(data)
    # checkStartAllGoods(data)
    checkStartAllMilitary(data)