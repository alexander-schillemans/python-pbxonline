class APIEndpoint:

    def __init__(self, api: object, endpoint: str) -> None:

        self.api = api
        self.endpoint = endpoint