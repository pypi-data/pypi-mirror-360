class DBException(Exception):
    def __init__(self, typ: str = "ValueError", msg: str = "None"):
        self.typ = typ
        self.msg = msg

    def dump(self):
        return {"type": self.typ, "msg": self.msg}

    def __str__(self):
        return f"{self.typ}: {self.msg}"
