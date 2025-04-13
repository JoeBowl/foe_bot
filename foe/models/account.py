from collections import deque
from datetime import datetime

class Account:
    def __init__(self, user_key=None, salt=None, headers=None, log_limit=1000):
        self.user_key = user_key
        self.salt = salt
        self.headers = headers
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