class IntelliwDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get_dict = None


class Request:
    """
    intelliw server request
    """

    def __init__(self, **kwargs) -> None:
        self.header = None
        self.json = ""
        self.query = {}
        self.form = IntelliwDict()
        self.files = {}
        self.body = ""
        self.batch_params = {}
        self.context = None
        self.raw = None
        self.method = "GET"
        self.url = None

        for k, v in kwargs.items():
            setattr(self, k, v)
