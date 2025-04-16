import re
import brotli
import json
import copy
import zstandard as zstd
import io

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