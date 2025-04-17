import json
import copy

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