

class RequestError(Exception):
    def __init__(self, message):
        self.message = message
        
class ValidationError(BaseException):
    def __init__(self, message):
        self.message = message
        
class AuthError(Exception):
    def __init__(self, message):
        self.message = message