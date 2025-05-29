from find_key_paths import find_key_paths
from collections import deque
import zstandard as zstd
import datetime
import brotli
import json
import re
import io

class Account:
    def __init__(self, user_key=None, salt=None, last_request_id=0, log_limit=1000):
        self.user_key        = user_key
        self.salt            = salt
        self.last_request_id = last_request_id
        self.request_log     = deque(maxlen=log_limit)
        self.response_log    = deque(maxlen=log_limit)
        self.data            = None
        self.server_time     = None

    def log_request(self, request):
        self.request_log.append({
            'timestamp': datetime.datetime.now(datetime.UTC).isoformat(),
            'request': request
        })

    def log_response(self, request, response):
        self.response_log.append({
            'timestamp': datetime.datetime.now(datetime.UTC).isoformat(),
            'request': request,
            'response': response
        })

    def get_request_log(self):
        return list(self.request_log)

    def get_response_log(self):
        return list(self.response_log)
    
    def get_log_request_old(self):
        # Return all requests without timestamps
        return [entry['request'] for entry in self.request_log]
    
    def get_log_response_old(self):
        # Return all requests without timestamps
        return [[entry['request'], entry['response']]  for entry in self.request_log]
    
    def get_last_log(self, url = None, method = None):
        # Iterate over the logs in reverse order to find the most recent POST request
        for entry in reversed(self.request_log):   
            request = entry['request']
            
            if (url != None) and (not url in request.url):
                continue
            
            if (method != None) and (method != request.method):
                continue
            
            return entry
        return None
    
    def get_last_request_time(self):
        last_request = self.get_last_log(url="forgeofempires.com/game/json?h=", method="POST")
        if last_request is None:
            return None
        else:
            return datetime.datetime.fromisoformat(last_request['timestamp']).replace(tzinfo=datetime.UTC)
        
    def get_data(self, request = None, response = None):
        if request == None and response == None:
            for entry in reversed(self.response_log):
                request  = entry['request']
                response = entry['response']
                if "forgeofempires.com/game/json?h=" in request.url:
                    if "getData" in request.body.decode('utf-8'):
                        break
                    
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
                    
                    return(json_response_data[1:])
                except Exception as e:
                    print("Could not decode response body:", e)
                    
    def get_server_time(self, request = None, response = None):
        if request == None and response == None:
            for entry in reversed(self.response_log):
                request  = entry['request']
                response = entry['response']
                if "forgeofempires.com/game/json?h=" in request.url:
                    if "LogService" in request.body.decode('utf-8'):
                        break
                    
        decoded_body = request.body.decode('utf-8')  # Convert bytes to string
        json_data = json.loads(decoded_body)  # Convert string to Python object
        
        for data in json_data:
            if data['requestClass'] == 'LogService':
                try:
                    # Check if the response is Brotli compressed
                    if 'br' in response.headers.get('content-encoding', ''):
                        decompressed_body = brotli.decompress(response.body)  # Decompress Brotli
                    else:
                        decompressed_body = response.body  # No compression, use raw body
                    
                    # Decode the response (assuming it's UTF-8)
                    decoded_response_body = decompressed_body.decode('utf-8')
                    json_response_data = json.loads(decoded_response_body)
                    
                    path = find_key_paths(json_response_data, 'requestClass', 'TimeService')[0][:-1]  # remove the last key to get to the parent object
                    for key in path:
                        json_response_data = json_response_data[key]
                    
                    return(json_response_data['responseData']['time'])
                except Exception as e:
                    print("Could not decode response body:", e)
                                
    def get_user_key(self, verbose=False):    
        last_request = self.get_last_log(url="forgeofempires.com/game/json?h=", method="POST")
             
        # Extract the URL from the request parameters
        url = last_request['request'].url
        
        # Use a regular expression to extract the user key from the URL
        match = re.search(r'h=([^&]+)', url)
        if match:
            # If a match is found, extract the user key
            user_key = match.group(1)
            if verbose:
                print(f"The user key is: {user_key}")
            return user_key
        else:
            if verbose:
                print("Could not find the user key.")
            return None

    def get_salt(self, request, response, verbose=False):
        try:
            encoding = response.headers.get('content-encoding', '')
            
            # Check if the response compressed
            if 'br' in encoding:
                decompressed_body = brotli.decompress(response.body)
            elif 'zstd' in encoding:
                dctx = zstd.ZstdDecompressor()
                with dctx.stream_reader(io.BytesIO(response.body)) as reader:
                    decompressed_body = reader.read()  # Read the entire decompressed stream
            else:
                decompressed_body = response.body
            
            # Decode the response (assuming it's UTF-8)
            decoded_response_body = decompressed_body.decode('utf-8')
            # print(decoded_response_body)
            
            signature_marker = "this._signatureHash+"
            start_pos = decoded_response_body.find(signature_marker)
            
            if start_pos == -1:
                print(f"'{signature_marker}' not found in the body.")
            
            # Move the position after "this._signatureHash+"
            start_pos += len(signature_marker)+1

            # Now, we look for the next quote after this position
            end_pos = decoded_response_body.find('"', start_pos)

            if end_pos == -1:
                print("No closing quote found.")
                
            # Extract the string between the quotes
            extracted_content = decoded_response_body[start_pos:end_pos]
            if verbose:
                print(f"Salt: {extracted_content}")
        except Exception as e:
            print("Could not decode response body:", e)
        return(extracted_content)