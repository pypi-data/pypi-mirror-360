from fastapi import APIRouter, FastAPI

from .Router import Router


class ChildPath:
    def __init__(
        self, name: str, path: str, tag: list = None, rts: list[Router] = None
    ):
        self.name = name
        self.path = path
        self.rt_api = None
        self.tag = tag
        self.rts: list[Router] = rts
        self.init()

    def init(self):
        if self.name == "root":
            return
        self.init_child()

    def init_root(self, app: FastAPI):
        for router in self.rts:
            app.add_api_route(
                path=router.path, methods=[router.method.value], endpoint=router.func
            )

    def init_child(self):
        self.rt_api = APIRouter()
        for router in self.rts:
            self.rt_api.add_api_route(
                path=router.path, methods=[router.method.value], endpoint=router.func
            )
