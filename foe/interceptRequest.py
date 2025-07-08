import json
import copy
from signature_generator2 import generateRequestPayloadSignature

def route_interceptor(account, verbose=False):
    async def handler(route, request):
        if "forgeofempires.com/game/json?h=" not in request.url:
            await route.continue_()
            return

        try:
            request_body = request.post_data
            if not request_body:
                if verbose:
                    print("Empty body.")
                await route.continue_()
                return

            request_data = json.loads(request_body)
        except Exception as e:
            print(f"route_interceptor: Error parsing request body: {e}")
            await route.continue_()
            return

        if not isinstance(request_data, list) or not request_data:
            if verbose:
                print("Invalid request structure.")
            await route.continue_()
            return

        request_ids = [entry.get("requestId") for entry in request_data if "requestId" in entry]
        if not request_ids:
            if verbose:
                print("No requestId found.")
            await route.continue_()
            return

        # Track and correct requestId
        if request_ids[0] == 1:
            account.last_request_id = 0

        if request_ids[0] <= account.last_request_id:
            # Fix IDs
            new_request_data = copy.deepcopy(request_data)
            for idx, entry in enumerate(new_request_data):
                entry["requestId"] = account.last_request_id + idx + 1

            corrected_body = json.dumps(new_request_data, separators=(',', ':'))
            corrected_headers = dict(request.headers)

            # Fix headers
            if "signature" in corrected_headers:
                corrected_headers["signature"] = generateRequestPayloadSignature(
                    new_request_data, account.user_key, account.salt
                )
            if "content-length" in corrected_headers: 
                corrected_headers["content-length"] = str(len(corrected_body))

            if verbose:
                print(f"Corrected request IDs: {[e['requestId'] for e in new_request_data]}")

            account.last_request_id = new_request_data[-1]["requestId"]
            
            # print("="*100)
            # print(request_body)
            # print(corrected_body)
            # print(request_body == corrected_body)
            # print("="*100)
            # print(request.headers)
            # print(corrected_headers)
            # print(request.headers == corrected_headers)
            # print("="*100)
            
            # Modify and send the updated request:
            await route.continue_(
                post_data=corrected_body,
                headers=corrected_headers
            )
        else:
            # IDs are fine, just update account
            account.last_request_id = request_ids[-1]
            if verbose:
                print(f"{request.url}: {request_ids}")
            await route.continue_()
    return handler
