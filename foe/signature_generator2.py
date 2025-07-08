import hashlib
import json

def generateRequestPayloadSignature(payload, signatureHash, salt):
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
    signatureHash = 'I3gIBhktlY9uB1xHg-UqYKyI'
    salt = "WJRuPsdvuFgz4P33MHc7Yi6lOSowHi8zpNbUfTDt55Kg/Pb1iYWHWcNc3TFWxSL2qVZ2haAy/xYDOkUryqKdOw=="
    
    payload = [
  {
    "__class__": "ServerRequest",
    "requestData": [
      {
        "__class__": "ViewportMetrics",
        "stageWidth": 1280,
        "stageHeight": 800,
        "bufferWidth": 1280,
        "bufferHeight": 800,
        "displayWidth": 1281,
        "displayHeight": 801,
        "contentsScaleFactor": 1
      }
    ],
    "requestClass": "LogService",
    "requestMethod": "logViewportMetrics",
    "requestId": 1
  },
  {
    "__class__": "ServerRequest",
    "requestData": [],
    "requestClass": "StartupService",
    "requestMethod": "getData",
    "requestId": 2
  }
]
    
    signature = generateRequestPayloadSignature(payload, signatureHash, salt)
    
    print("Generated Signature:", signature)
    
    print("Actual Signature:   ", "3817fd070b")



