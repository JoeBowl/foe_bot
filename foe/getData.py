import re
import brotli
import json
import copy
import zstandard as zstd
import io

def getData(log_response):
    for request, response in reversed(log_response):
        if "forgeofempires.com/game/json?h=" in request.url:
            if request.body:  # Ensure there is a body to decode
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

def getLastLog(logs):
    # Initialize a variable to store the last POST request
    last_post_request = None
    
    # Iterate over the logs in reverse order to find the most recent POST request
    for log in reversed(logs):   
        # Extract the request details
        url = log.url
        method = log.method
    
        # Check if the request method is POST
        if method != 'POST':
            continue  # Skip if it's not a POST request
            
        if not("forgeofempires.com/game/json?h=" in url):
            continue  # Skip if it's not from forge of empires
    
        # Found the most recent POST request
        last_post_request = log
        return(last_post_request)  # Exit the loop after finding the last POST request

def getRequestId(logs):
    # Get the last POST request
    last_post_request = getLastLog(logs)
    
    # Check if a POST request was found
    if last_post_request is None:
        print("No POST requests were found.")
        return(0)
    
    # Parse the JSON payload's post data
    try:
        post_data = json.loads(last_post_request.body)[0]
    except json.JSONDecodeError as e:
        print(f"Failed to parse payload' post data JSON: {e}, {last_post_request}")
        return(0)
    
    request_id = post_data['requestId']
    return(request_id+1)

def getUserKey(logs, verbose=False):    
    # Initialize a variable to store the user key
    user_key = None
    
    # Iterate over each entry in the performance logs
    for log in reversed(logs):        
        # Extract the URL from the request parameters
        url = log.url
        
        # Check if the URL contains the 'game/json?h=' pattern
        if not ('game/json?h=' in url):
            continue  # Skip to the next log entry if the pattern is not in the URL
        
        # Use a regular expression to extract the user key from the URL
        match = re.search(r'h=([^&]+)', url)
        if match:
            # If a match is found, extract the user key
            user_key = match.group(1)
            if verbose:
                print(f"The user key is: {user_key}")
            break  # Exit the loop once the user key is found
    
    # Check if the user key was found after iterating through the logs
    if user_key is None:
        print("Could not find the user key.")
    
    return(user_key)

def getSalt(request, response, verbose=False):
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

def intercept_request_id(request, last_request_id, user_key, verbose=False):
    def correct_requestId(request, last_request_id):
        from signature_generator2 import generateRequestPayloadSignature
        
        new_request = copy.deepcopy(request)
        
        # Correct requestId
        new_request_data = json.loads(request.body.decode("utf-8"))
        
        for idx, entry in enumerate(new_request_data):
            entry["requestId"] = last_request_id + idx + 1
                
        # Re-encode and update the body
        new_request_body = json.dumps(new_request_data, separators=(',', ':')).encode("utf-8")
        new_request.body = new_request_body
        
        # Correct the headers for the new requestId
        original_headers = list(request.headers.items())

        for key, value in original_headers:
            del new_request.headers[key]
            if key == "signature":
                new_request.headers[key] = generateRequestPayloadSignature(new_request_data, user_key)
            elif key == "content-length":
                new_request.headers[key] = f"{len(new_request_body)}"
            else:
                new_request.headers[key] = value
                
        return(new_request)
    
    if verbose:
        print(f"Request to {request.url}:")
    
    # Ensure the request body is not empty
    if not request.body:
        print("Request body is empty.")
        return last_request_id # Exit function early
    
    try:
        request_data = json.loads(request.body.decode("utf-8"))  # Decode and parse JSON
    except json.JSONDecodeError:
        print("Request body is not valid JSON.")
    except Exception as e:
        print(f"Error parsing request body: {e}")    
        
        
    if isinstance(request_data, list) and request_data:  # Ensure it's a non-empty list
        request_ids = [entry.get("requestId") for entry in request_data if "requestId" in entry]
    else:
        print("No valid requestId found in request body.")
        return last_request_id
                
    if request_ids[0] == 1:
        last_request_id = 0
        
    if request_ids[0] <= last_request_id:
        new_request = correct_requestId(request, last_request_id)
        print(f"Correcting id from {new_request} to {last_request_id}")
        
        request.body = new_request.body
        request.headers = new_request.headers
                
    if verbose:
        request_data = json.loads(request.body.decode("utf-8"))  # Decode and parse JSON
        request_ids = [entry.get("requestId") for entry in request_data if "requestId" in entry]
        print(request_ids)

    return request_ids[-1]