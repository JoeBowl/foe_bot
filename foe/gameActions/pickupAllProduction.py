from find_key_paths import find_key_paths
from sendRequest import pickupProduction

# From data, checks all building that have finished production and collects them
def pickupAllProduction(data, driver, account, verbose=False):
    building_ids = checkPickupAllProduction(data, verbose=False)
        
    if building_ids != []:
        response = pickupProduction(building_ids, driver, account)
    else:
        response = None
        
    if verbose == True:
        print(response)
        
    return response

# From data, checks all building that have finished production and collects them
def checkPickupAllProduction(data, verbose=True):
    paths = find_key_paths(data, '__class__', 'ProductionFinishedState')
    
    building_ids = []
    for path in paths:
        buildingInfo = data[path[0]][path[1]][path[2]][path[3]][path[4]]
        name = buildingInfo['cityentity_id']
        building_id = buildingInfo['id']
            
        building_ids.append(building_id)
        
        if verbose:
            print("Name:", name, "id:", building_id)
            
    return building_ids



# From data, checks all building that have finished production and collects them
def pickupBestPFProduction(data, driver, account, top_n=15, verbose=False):
    building_ids = checkPickupBestPFProduction(data, top_n, verbose=False)
        
    if building_ids != []:
        response = pickupProduction(building_ids, driver, account)
    else:
        response = None
    
    if verbose == True:
        print(response)
        
    return response

# From data, checks all building that have finished production and collects them
def checkPickupBestPFProduction(data, top_n=15, verbose=True):
    paths = find_key_paths(data, '__class__', 'ProductionFinishedState')
    
    building_pf_list = []  # List to store tuples of (building_id, name, PFs)

    for path in paths:
        buildingInfo = data[path[0]][path[1]][path[2]][path[3]][path[4]]
        building_id = buildingInfo['id']
        name = buildingInfo['cityentity_id']  # Extract building name
        
        if ('state' in buildingInfo and
            'productionOption' in buildingInfo['state'] and
            'products' in buildingInfo['state']['productionOption']):
            
            for product in buildingInfo['state']['productionOption']['products']:
                if (
                    'playerResources' in product and
                    'resources' in product['playerResources'] and
                    'strategy_points' in product['playerResources']['resources']
                ):
                    PFs = product['playerResources']['resources']['strategy_points']
                    building_pf_list.append((building_id, name, PFs))  # Store all info
    
    # Sort by PFs in descending order and get the top n
    top_buildings = sorted(building_pf_list, key=lambda x: x[2], reverse=True)[:top_n]

    # Print results
    if verbose:
        print(f"Top {top_n} Buildings with Highest PFs:")
        for building_id, name, pfs in top_buildings:
            print("Name:", name, "id:", building_id, "PFs:", pfs)
            
    # Print results
    building_ids = []
    for building_id, name, pfs in top_buildings:
        building_ids.append(building_id)
    
    return building_ids


def getBlueGalaxyId(data, verbose=False):
    paths = find_key_paths(data, '__class__', 'ProductionFinishedState')
    
    for path in paths:
        buildingInfo = data[path[0]][path[1]][path[2]][path[3]][path[4]]
        building_id = buildingInfo['id']
        name = buildingInfo['cityentity_id']  # Extract building name
        
        if name == "X_OceanicFuture_Landmark3":
            return(building_id)
        
def pickupBlueGalaxyAndBestPFProduction(data, driver, account, top_n=15, verbose=False):
    best_building_ids = checkPickupBestPFProduction(data, top_n, verbose=False)
    blue_galaxy_id = getBlueGalaxyId(data)
    
    building_ids = [blue_galaxy_id] + best_building_ids
        
    if building_ids != []:
        response = pickupProduction(building_ids, driver, account)
    else:
        response = None
    
    if verbose == True:
        print(response)
        
    return response

        
if __name__ == "__main__":
    print(checkPickupBestPFProduction(data))
    print(checkPickupAllProduction(data))
    
    print(getBlueGalaxyId(data))
    