import datetime
from time import sleep
from typing import Optional

from DateTime import DateTime

from sthg_common_base.response.exception import CustomException
from sthg_common_base.response.httpCodeEnum import ResponseEnum
from sthg_common_base.response.response import BaseResponse
from sthg_common_base.utils.log_wrapper import service_log
from pydantic import BaseModel,Field

from sthg_common_base.utils.request_util import RequestUtil


# 注册自定义异常
class AccessDeniedError(Exception):
    pass

class Person(BaseModel):
    ID: Optional[str] = Field(None, description="HTTP 状态码")      # 声明字段类型
    name: Optional[str] = Field(None, description="HTTP 状态码")       # 声明字段类型

    # 不需要自定义 __init__，Pydantic 会自动处理

    def get_id(self):
        return self.ID

    def get_name(self):
        return self.name

    def set_id(self, new_id):
        self.ID = new_id

    def set_name(self, new_name):
        self.name = new_name

    def __str__(self):
        return f"Person(ID={str(self.ID)}, name='{self.name}')"


class Person2():
    def __init__(self, ID, name):
        self.ID = ID
        self.name = name

    def get_id(self):
        return self.ID

    def get_name(self):
        return self.name

    def set_id(self, new_id):
        self.ID = new_id

    def set_name(self, new_name):
        self.name = new_name

    def __str__(self):
        return f"Person(ID={self.ID}, name='{self.name}')"



@service_log(printReq=True,printResp=True)
def get_Object333(id:str)->Person:
    per = Person2("1","1231")

    return per

@service_log(printReq=True,printResp=True)
def get_Object(id:str)->BaseResponse:
    per = Person(ID="1",name="1231")
    RequestUtil.get("http://www.baidu.com")
    RequestUtil.post("http://www.baidu.com")
    return  BaseResponse(ResponseEnum.OK,per)

@service_log(printReq=True,printResp=True)
def get_Object_rasie1(id:str)->Person:
    per = Person(ID="1",name="1231")
    raise AccessDeniedError

@service_log(printReq=True,printResp=True)
def get_baseRes(id:str)->BaseResponse:
    per = Person(ID="2",name="anne2")
    result = BaseResponse(ResponseEnum.OK,per)

    return result


@service_log(printReq=True, printResp=True)
def get_Object_Exception(id: str) -> BaseResponse:
    per = Person(ID="2",name="anne2")

    raise CustomException(ResponseEnum.InternalError,None)

    return result


@service_log(printReq=True, printResp=True,throwException=False)
def get_Object_Exception2(id: str) -> BaseResponse:
    per = Person(ID="2",name="anne2")

    raise CustomException(ResponseEnum.InternalError,None)

    return result

@service_log(printReq=True, printResp=True)
def get_Object_MaxRt(id: str) -> BaseResponse:
    per = Person(ID="2",name="anne2")

    result = BaseResponse(ResponseEnum.OK, per)
    sleep(1)
    return result

@service_log(printReq=True,printResp=True)
async def get_Object_ansyc(id:str)->Person:
    per = Person(ID="2",name="anne2")
    return per

@service_log(printReq=True,printResp=True)
async def get_baseRes_ansyc(id:str)->BaseResponse:
    per = Person(ID="2",name="anne2")
    result = BaseResponse(ResponseEnum.OK,per)

    return result

@service_log(printReq=True, printResp=True)
async def get_Object_Exception_ansyc(id: str) -> BaseResponse:
    per = Person(ID="2",name="anne2")

    raise CustomException(ResponseEnum.InternalError,None)

    return result


@service_log(printReq=True, printResp=True,throwException=False)
async def get_Object_Exception2_ansyc(id: str) -> BaseResponse:
    per = Person(ID="2",name="anne2")

    raise CustomException(ResponseEnum.InternalError,None)

    return result

@service_log(printReq=True, printResp=True)
async def get_Object_MaxRt_ansyc(id: str) -> BaseResponse:
    per = Person(ID="2",name="anne2")

    result = BaseResponse(ResponseEnum.OK, per)
    sleep(1)
    return result
