from collections import deque
import datetime
import re

class Account:
    def __init__(self, user_key=None, salt=None, last_request_id=0, log_limit=1000):
        self.user_key = user_key
        self.salt = salt
        self.last_request_id = last_request_id
        self.request_log = deque(maxlen=log_limit)
        self.response_log = deque(maxlen=log_limit)

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
