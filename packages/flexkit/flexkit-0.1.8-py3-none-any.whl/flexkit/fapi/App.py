import uvicorn
from fastapi import FastAPI
from .ChildPath import ChildPath


class App:
    def __init__(self, app_o: dict, middleware: dict, routers: list[ChildPath]):
        self.app = FastAPI(**app_o)
        self.app.add_middleware(**middleware)
        self.add_routers(routers)

    def add_router(self, child_path: ChildPath):
        self.app.include_router(
            child_path.rt_api, prefix=child_path.path, tags=child_path.tag
        )

    def add_routers(self, routers: list[ChildPath]):
        for router in routers:
            if router.name == "root":
                router.init_root(self.app)
                continue
            self.add_router(router)

    def run(self, host="127.0.0.1", port=8001, *args, **kwargs):
        uvicorn.run(self.app, host=host, port=port, *args, **kwargs)
