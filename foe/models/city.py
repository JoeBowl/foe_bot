from find_key_paths import find_key_paths
from collections import deque
import zstandard as zstd
import datetime
import brotli
import json
import copy
import re
import io

class City:
    def __init__(self):
        self.data = None
        self.hidden_rewards_data = None
        self.buildings_data = None
        
    async def get_data(self, response=None, verbose=False):
        try:
            if response is None:
                print("Response must be provided.")
                return

            # Get and parse request body
            decoded_body = response.request.post_data
            json_data = json.loads(decoded_body)

            for data in json_data:
                if data.get('requestMethod') == 'getData':
                    try:
                        # Get and handle compressed response body
                        raw_body = await response.body()
                        
                        # encoding = response.headers.get('content-encoding', '')
                        # if 'br' in encoding:
                        #     decompressed_body = brotli.decompress(raw_body)
                        # else:
                        #     decompressed_body = raw_body
                        # decoded_response_body = decompressed_body.decode('utf-8')
                        
                        decoded_response_body = raw_body.decode('utf-8')
                        json_response_data = json.loads(decoded_response_body)

                        # Save data, skipping the first element
                        self.data = json_response_data[1:]
                        if verbose:
                            print("Data successfully extracted.")
                    except Exception as e:
                        print("get_data: Could not decode response body:", e)
                    break

        except Exception as e:
            print("get_data: Error in get_data:", e)
                    
    async def get_hidden_rewards_data(self, response = None):
        try:
            # Await the async method to get raw bytes
            raw_body = await response.body()
            
            # Decode and parse JSON
            decoded_response_body = raw_body.decode('utf-8')
            json_response_data = json.loads(decoded_response_body)
        
            self.hidden_rewards_data = json_response_data
            
        except Exception as e:
            print("get_hidden_rewards_data: Failed to extract hidden rewards data:", e)
        
    async def get_buildings_data(self, response):
        try:
            # Await the async method to get raw bytes
            raw_body = await response.body()
            
            # Decode and parse JSON
            decoded_response_body = raw_body.decode('utf-8')
            json_response_data = json.loads(decoded_response_body)

            # Extract path to the 'entities' key
            path = find_key_paths(json_response_data, target_key='entities')[0][:-1]

            # Traverse the structure to extract building data
            buildings_data = copy.deepcopy(json_response_data)
            for key in path:
                buildings_data = buildings_data[key]

            self.buildings_data = buildings_data['entities']

        except Exception as e:
            print("get_buildings_data: Failed to extract building data:", e)
        
    async def update_buildings_data(self, response):
        try:
            # Await the async method to get raw bytes
            raw_body = await response.body()
        
            # Decode and parse JSON
            decoded_response_body = raw_body.decode('utf-8')
            json_response_data = json.loads(decoded_response_body)
        
            # Find the paths for the updated entities
            paths = find_key_paths(json_response_data, target_key = 'cityentity_id')
        
            # Load old city data
            old_buildings_data = self.buildings_data
        
            for path in paths:
                # Get the updated data for each building
                updated_building_data = copy.deepcopy(json_response_data)
                for key in path[:-1]:
                    updated_building_data = updated_building_data[key]
                    
                # Replace old information for newer one
                for i, old_building_data in enumerate(old_buildings_data):
                    if updated_building_data["id"] == old_building_data["id"]:
                        # print(json.dumps(old_building_data, indent=2))
                        # print(json.dumps(updated_building_data, indent=2))
                        old_building_data.update(updated_building_data)
                        
        except Exception as e:
            print("update_buildings_data: Failed to update building data:", e)