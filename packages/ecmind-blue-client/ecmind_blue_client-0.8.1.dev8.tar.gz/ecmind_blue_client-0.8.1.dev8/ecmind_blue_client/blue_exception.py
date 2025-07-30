class BlueException(Exception):
    def __init__(self, return_code: int, message: str):
        self.return_code = return_code
        self.message = message
        super(BlueException, self).__init__(message)

    def __repr__(self):
        return f"BlueException ({self.return_code}): {self.message}"
