from ..err import MException
from .Model import Model


class Models:
    def __init__(self):
        self.models: dict[str, "Model"] = {}

    def add_model(self, model: "Model"):
        if model.name in self.models:
            raise MException(
                "ValiDataModel.AddModelsError", f"模型({model.name}) 已存在，添加失败"
            )
        self.models[model.name] = model

    def add_models(self, models: list["Model"]):
        for model in models:
            self.add_model(model)

    def get(self, m_name: str):
        if m_name not in self.models:
            raise MException("ValiDataModel.GetModelError", f"模型({m_name})未定义")
        return self.models[m_name]
