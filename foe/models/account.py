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
        self.server_time     = None

    def log_request(self, request):
        self.request_log.append({
            'timestamp': datetime.datetime.now(datetime.UTC).isoformat(),
            'request': request
        })

    def log_response(self, response):
        self.response_log.append({
            'timestamp': datetime.datetime.now(datetime.UTC).isoformat(),
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
                    
    async def get_server_time(self, response=None, verbose=False):
        try:
            request = response.request

            # Decode request body (already string in Playwright)
            request_body = request.post_data
            json_data = json.loads(request_body)

            # Ensure we're looking at LogService requests
            if not any(entry.get("requestClass") == "LogService" for entry in json_data):
                return

            # Await and decompress response
            raw_body = await response.body()
            
            # Decode and parse response
            decoded_response_body = raw_body.decode('utf-8')
            json_response_data = json.loads(decoded_response_body)

            # Find path to the TimeService object
            path = find_key_paths(json_response_data, 'requestClass', 'TimeService')[0][:-1]  # up to parent
            for key in path:
                json_response_data = json_response_data[key]
            
            self.server_time = json_response_data['responseData']['time']
            print(f"Server time updated to {self.server_time}")
            return
            
        except Exception as e:
            print("get_server_time: Could not decode response body:", e)
            return
                                
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

    async def get_salt(self, response, verbose=False):
        extracted_content = None
        try:
            # Playwright's response.body() is async, so await it
            raw_body = await response.body()

            # Get the content-encoding header (lowercase keys in Playwright)
            # encoding = response.headers.get('content-encoding', '')
            # 
            # Decompress if needed
            # if 'br' in encoding:
            #     decompressed_body = brotli.decompress(raw_body)
            # elif 'zstd' in encoding:
            #     dctx = zstd.ZstdDecompressor()
            #     with dctx.stream_reader(io.BytesIO(raw_body)) as reader:
            #         decompressed_body = reader.read()
            # else:
            #     decompressed_body = raw_body
            # 
            # Decode body as UTF-8 text
            # decoded_response_body = decompressed_body.decode('utf-8')
            
            decoded_response_body = raw_body.decode('utf-8')
            
            signature_marker = "this._signatureHash+"
            start_pos = decoded_response_body.find(signature_marker)

            if start_pos == -1:
                print(f"'{signature_marker}' not found in the body.")
                return None

            # Adjust position after marker + 1 (for quote or next char)
            start_pos += len(signature_marker) + 1

            # Find next quote to extract string
            end_pos = decoded_response_body.find('"', start_pos)

            if end_pos == -1:
                print("No closing quote found.")
                return None

            extracted_content = decoded_response_body[start_pos:end_pos]

            if verbose:
                print(f"Salt: {extracted_content}")

        except Exception as e:
            print("get_salt: Could not decode response body:", e)

        return extracted_content