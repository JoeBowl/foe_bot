import hashlib
import json

def generateRequestPayloadSignature(payload, account):
    signatureHash = account.user_key
    salt = account.salt
    
    # Convert payload to JSON string
    json_payload = json.dumps(payload).replace(' ', '')
    
    # Step 1: Concatenate components
    concatenated_string = signatureHash + salt + json_payload
    
    # Step 2: Encode the concatenated string (replace with correct encoding if necessary)
    encoded_string = hashlib.md5(concatenated_string.encode()).hexdigest()  # Adjust encoding method if needed
    
    # Step 3: Extract substring from the encoded string
    signature = encoded_string[1:11]

    return signature


if __name__ == "__main__":
    # Define your components
    signatureHash = 'uY9Y8ltFhBxQyakYYPmLJzkw'
    
    payload = [
        {
            "__class__": "ServerRequest",
            "requestData": [[51]],
            "requestClass": "CityProductionService",
            "requestMethod": "pickupProduction",
            "requestId": 17
        }
    ]
    
    signature = generateRequestPayloadSignature(payload, signatureHash)
    
    print("Generated Signature:", signature)
    
    print("Actual Signature:   ", "afe973361f")

