class AsanakWebCallException(Exception):
    pass

class AsanakHttpException(AsanakWebCallException):
    def __init__(self, status_code, response_text):
        super().__init__(f"HTTP {status_code}: {response_text}")
