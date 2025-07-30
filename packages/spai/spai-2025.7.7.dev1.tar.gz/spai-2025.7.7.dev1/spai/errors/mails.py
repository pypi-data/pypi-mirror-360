class MailError(Exception):
    def __init__(self, message="Mail could not be sent"):
        self.message = message
        super().__init__(self.message)
