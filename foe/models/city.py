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
        
    def get_data(self, request = None, response = None):
        # if request == None and response == None:
        #     for entry in reversed(self.response_log):
        #         request  = entry['request']
        #         response = entry['response']
        #         if "forgeofempires.com/game/json?h=" in request.url:
        #             if "getData" in request.body.decode('utf-8'):
        #                 break
                    
        decoded_body = request.body.decode('utf-8')  # Convert bytes to string
        json_data = json.loads(decoded_body)  # Convert string to Python object
        
        for data in json_data:
            if data['requestMethod'] == 'getData':
                try:
                    # Check if the response is Brotli compressed
                    if 'br' in response.headers.get('content-encoding', ''):
                        decompressed_body = brotli.decompress(response.body)  # Decompress Brotli
                    else:
                        decompressed_body = response.body  # No compression, use raw body
                    
                    # Decode the response (assuming it's UTF-8)
                    decoded_response_body = decompressed_body.decode('utf-8')
                    json_response_data = json.loads(decoded_response_body)
                    
                    self.data = json_response_data[1:]
                except Exception as e:
                    print("Could not decode response body:", e)
                    
    def get_hidden_rewards_data(self, request = None, response = None):
        # Check if the response is Brotli compressed
        if 'br' in response.headers.get('content-encoding', ''):
            decompressed_body = brotli.decompress(response.body)  # Decompress Brotli
        else:
            decompressed_body = response.body  # No compression, use raw body
        
        # Decode the response (assuming it's UTF-8)
        decoded_response_body = decompressed_body.decode('utf-8')
        json_response_data = json.loads(decoded_response_body)
        
        self.hidden_rewards_data = json_response_data
        
        # print(json.dumps(json_response_data, indent=2))
        # print()
        # print(request_body, "\n")
        # checkCollectAllReward(json_response_data, account.server_time)
        
    def get_buildings_data(self, request = None, response = None):
        # Check if the response is Brotli compressed
        if 'br' in response.headers.get('content-encoding', ''):
            decompressed_body = brotli.decompress(response.body)  # Decompress Brotli
        else:
            decompressed_body = response.body  # No compression, use raw body
        
        # Decode the response (assuming it's UTF-8)
        decoded_response_body = decompressed_body.decode('utf-8')
        json_response_data = json.loads(decoded_response_body)
        
        path = find_key_paths(json_response_data, target_key = 'entities')[0][:-1]

        buildings_data = copy.deepcopy(json_response_data)
        for key in path:
            buildings_data = buildings_data[key]
            
        self.buildings_data = buildings_data['entities']
        
    def update_buildings_data(self, request = None, response = None):
        # Check if the response is Brotli compressed
        if 'br' in response.headers.get('content-encoding', ''):
            decompressed_body = brotli.decompress(response.body)  # Decompress Brotli
        else:
            decompressed_body = response.body  # No compression, use raw body
        
        # Decode the response (assuming it's UTF-8)
        decoded_response_body = decompressed_body.decode('utf-8')
        json_response_data = json.loads(decoded_response_body)
        # print(json.dumps(json_response_data, indent=2))
        
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