from collections import deque
from datetime import datetime

class Account:
    def __init__(self, user_key=None, salt=None, log_limit=1000):
        self.user_key = user_key
        self.salt = salt
        self.request_log = deque(maxlen=log_limit)
        self.response_log = deque(maxlen=log_limit)

    def log_request(self, request):
        self.request_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'request': request
        })

    def log_response(self, request, response):
        self.response_log.append({
            'timestamp': datetime.utcnow().isoformat(),
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
