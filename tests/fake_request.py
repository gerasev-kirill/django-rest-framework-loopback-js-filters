

class FakeRequest:
    query_params = {}
    def __init__(self, **kwargs):
        self.query_params = kwargs
