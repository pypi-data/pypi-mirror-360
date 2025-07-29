class InvalidURLError(Exception):
    def __init__(self, message: str = "The provided URL is invalid. Please ensure it is properly formatted."):
        self.message = message
        super().__init__(self.message)