class PlatformNotDefined(Exception):
    """When when a platform is not defined within the config.py or is set to False.

    Attributes:
        message: explanation of the error
    """

    def __init__(self, message:str, status_code=417, payload=None):
        self.message = message
        super().__init__(self.message)
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def __str__(self):
        return f'{self.message}'

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv