class HttpMethod:
    def __init__(self, method: str = None):
        self.value = "get"
        if isinstance(method, str):
            self.from_str(method)

    def from_str(self, value: str):
        value = value.strip().lower()
        if value == "get":
            self.GET()
            return
        if value == "post":
            self.POST()
            return
        if value == "put":
            self.PUT()
            return
        if value == "delete":
            self.DELETE()
            return
        else:
            raise ValueError(f"Invalid HTTP Method: {value}")

    def GET(self):
        self.value = "get"

    def POST(self):
        self.value = "post"

    def PUT(self):
        self.value = "put"

    def DELETE(self):
        self.value = "delete"


class Router:
    def __init__(
        self, func, path: str, method: HttpMethod = HttpMethod("GET"), *args, **kwargs
    ):
        self.func = func
        self.path = path
        self.method = method
        self.args = args
        self.kwargs = kwargs
