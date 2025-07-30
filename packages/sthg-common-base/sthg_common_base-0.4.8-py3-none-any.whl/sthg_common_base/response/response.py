from typing import Any, Generic, Optional, TypeVar,Collection, Dict

from fastapi.responses import JSONResponse
from pydantic import Field, BaseModel, PrivateAttr

import  json

from sthg_common_base.response.httpCodeEnum import ResponseEnum

from sthg_common_base.response.json_serializer import EnhancedJSONSerializer
from sthg_common_base.utils.constants import Constants
from sthg_common_base.utils.log_util import LoggerUtil, TraceID

T = TypeVar('T')

try:
    from bson import ObjectId
except ImportError:
    ObjectId = None  # 处理未安装pymongo的情况

try:
    import numpy as np
except ImportError:
    np = None  # 处理未安装numpy的情况

class BaseResponse(BaseModel,Generic[T]):
    code: Optional[int] = Field(ResponseEnum.OK.getHttpCode, description="HTTP 状态码")
    busiCode: Optional[str] = Field(ResponseEnum.OK.getBusiCode, description="业务状态码")
    busiMsg: Optional[str] = Field(ResponseEnum.OK.getBusiMsg, description="业务消息")
    exceptionStack: Optional[str] = Field(None, description="关键堆栈异常")
    data: Optional[T] = Field(None, description="返回数据")
    count: Optional[int] = Field(0, description="分页总条数")
    dataCount: Optional[int] = Field(0, description="集合总条数")
    requestId: Optional[str] = Field(Constants.Str_Place, description="全链路ID")
    _resEnum: ResponseEnum = PrivateAttr()

    def __init__(self, resEnum: ResponseEnum = ResponseEnum.OK, data: Any=None, msg: str = None, exceptionStack =None,*args,**kwargs):
        super().__init__(**kwargs)
        self._resEnum = resEnum
        if msg and args:
            msg = msg.format(*args)
        self.code= resEnum.getHttpCode
        self.busiCode= resEnum.getBusiCode
        if msg:
            self.busiMsg = f"{resEnum.getBusiMsg},{msg}"
        else:
            self.busiMsg = f"{resEnum.getBusiMsg}"
        self.data=data
        self.dataCount = self._handle_collection_size(data)
        self.requestId = TraceID.get_trace()
        if exceptionStack:
            self.exceptionStack = exceptionStack
        if kwargs :
            self.count = kwargs.get("count",0)

    def __call__(self, *args) -> JSONResponse:
        return JSONResponse(status_code=self.code,
                            content={
                                "code": self.code,
                                "busiCode": self.busiCode,
                                "busiMsg": self.busiMsg,
                                "data": self.data,
                                "count": self.count,
                                "dataCount": self.dataCount,
                                "requestId": self.requestId,
                                "exceptionStack": self.exceptionStack,
                            })

    @classmethod
    def _handle_collection_size(cls, data: Any) -> Optional[int]:
        leng = 0
        try:
            if data and isinstance(data, Collection) and not isinstance(data, (str, bytes)):
                leng = len(data)
            if data and isinstance(data, Dict):
                leng = len(data)
        except Exception as e:
            LoggerUtil.error_log(f"_handle_collection_size:{e}")

        return leng

    def is_success(self):
        is_success = False
        if self.code < 400:
            is_success = True
        return is_success

    def set_count(self,count):
        if count and count > 0 :
            self.count = count

    def set_exceptionStack(self,exceptionStack):
        if exceptionStack and len(exceptionStack) > 0 :
            self.exceptionStack = exceptionStack

    def build_reset_by_resenum(self, data:any, resEnmu: ResponseEnum, msg=None):
        self.code = resEnmu.getHttpCode
        self.busiCode = resEnmu.getBusiCode
        if msg :
            self.busiMsg = f"{resEnmu.getBusiMsg},{msg}"
        else:
            self.busiMsg = resEnmu.getBusiMsg
        self.data = data
        self.dataCount = 0
        self.exceptionStack = None
        self.count = 0

    def build_reset_by_resp(self,response: 'BaseResponse', msg=None):
        self.code = response.code
        self.busiCode = response.busiCode
        if msg :
            self.busiMsg = f"{response.busiMsg},{msg}"
        else:
            self.busiMsg = response.busiMsg
        self.data = response.data
        self.dataCount = self._handle_collection_size(response.data)
        self.exceptionStack = response.exceptionStack
        self.count = response.dataCount


    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False
        )

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "busiCode": self.busiCode,
            "busiMsg": self.busiMsg,
            "data": self.data,
            "count": self.count,
            "dataCount": self.dataCount,
            "requestId": self.requestId,
            "exceptionStack": self.exceptionStack
        }