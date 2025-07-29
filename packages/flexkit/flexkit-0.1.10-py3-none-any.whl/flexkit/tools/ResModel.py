from pydantic import BaseModel, Field
from typing import Union


class ResModel(BaseModel):
    status: bool = Field(False, description="状态")
    msg: str = Field("", description="消息")
    data: Union[dict, list] = Field({}, description="数据")

    @staticmethod
    def success(msg="", data={}):
        return ResModel(status=True, msg=msg, data=data)

    @staticmethod
    def error(msg="", data={}):
        return ResModel(status=False, msg=msg, data=data)
