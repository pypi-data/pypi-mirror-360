import datetime
import uvicorn
from fastapi import FastAPI
from datetime import datetime, date, time
from fastapi.responses import JSONResponse
from decimal import Decimal



from uuid import UUID

from sthg_common_base import format_exception_msg, EnhancedJSONSerializer
from sthg_common_base.example.test_service import get_Object, get_baseRes, get_Object_Exception, get_Object_MaxRt, \
    get_Object_Exception2, \
    get_Object_ansyc, get_baseRes_ansyc, get_Object_Exception_ansyc, get_Object_Exception2_ansyc, \
    get_Object_MaxRt_ansyc, get_Object333, AccessDeniedError,get_Object_rasie1
from sthg_common_base.response.exception import BaseException, register_exception_handlers
from sthg_common_base.response.httpCodeEnum import ResponseEnum, ResCode
from sthg_common_base.response.response import BaseResponse
from sthg_common_base.utils.log_util import Logger, register_log_middleware, LoggerUtil
from sthg_common_base.utils.log_wrapper import access_log, register_exception
from sthg_common_base.response.httpCodeEnum import HttpStatus

app = FastAPI(
    default_response_class=JSONResponse,
    json_encoders={
        datetime: lambda dt: dt.isoformat(),
        Decimal: lambda d: float(d),
        UUID: lambda u: str(u),
        # 添加其他自定义类型的处理
    }
)
logger = LoggerUtil()
register_exception(AccessDeniedError,ResponseEnum.AccessDenied)
register_exception_handlers(app)
register_log_middleware(app)

@app.get("/get_Object_rasie", name="测试返回")
@access_log()
def get_Object_rasie():
    per = get_Object_rasie1("1")
    #BaseResponse(resEnum=ResponseEnum.OK, data=fields)

    return BaseResponse(ResponseEnum.OK,per,count=10)


@app.get("/get_Object_test", name="测试返回")
@access_log()
def get_Object_test():
    per = get_Object("1")
    #BaseResponse(resEnum=ResponseEnum.OK, data=fields)

    return per

@app.get("/get_Object333_test", name="测试返回")
@access_log()
def get_Object_test():
    per = get_Object333("1")
    #BaseResponse(resEnum=ResponseEnum.OK, data=fields)

    return BaseResponse(ResponseEnum.OK,per)



@app.get("/get_baseRes_test", name="测试添加msg")
@access_log()
def get_baseRes_test():
    baseRes = get_baseRes("2")

    return baseRes


@app.get("/get_no_print", name="测试只打印异常日志")
@access_log(onlyPrintError=True)
def get_no_print():
    baseRes = get_baseRes("2")

    return baseRes


@app.get("/get_exception_test", name="测试异常数据")
@access_log(onlyPrintError=True)
def get_exception_test():
    base = get_Object_Exception(1)

    return BaseResponse(ResponseEnum.OK, data=[{"id": 1}], msg="正确返回")

@app.get("/get_exception_test2", name="测试异常数据")
@access_log(onlyPrintError=True,throwException=True)
def get_exception_test2():
    base = get_Object_Exception(1)

    return BaseResponse(ResponseEnum.OK, data=[{"id": 1}], msg="正确返回")

@app.get("/get_exception_test3", name="测试全链路打印异常数据")
@access_log(onlyPrintError=True)
def get_exception_test3():
    base = get_Object_Exception2(1)

    return BaseResponse(ResponseEnum.OK, data=[{"id": 1}], msg="正确返回")

@app.get("/get_exception_test4", name="测试无异常不打印")
@access_log(onlyPrintError=True)
def get_exception_test4():
    base = get_baseRes(1)
    return BaseResponse(ResponseEnum.OK, data=[{"id": 1}], msg="正确返回",exceptionStack=format_exception_msg(None))



@app.get("/get_maxrt_test", name="测试只打印大于指定响应的日志")
@access_log(onlyPrintMaxRt=100)
def get_maxrt_test():
    re = BaseResponse(ResponseEnum.OK,None)
    result = get_Object_MaxRt("1")
    re.build_reset_by_resp(result)

    return re
@app.get("/get_maxrt_test2", name="测试只打印大于指定响应的日志")
@access_log(onlyPrintMaxRt=200000)
def get_maxrt_test2():
    re = BaseResponse(ResponseEnum.OK,None)
    result = get_Object_MaxRt("1")
    re.build_reset_by_resp(result)

    return re


@app.get("/test_reset_response_msg", name="测试重制返回")
@access_log()
def test_response():
    old_base = BaseResponse(ResponseEnum.OK, data=[{"id": 1}], msg="正确返回")
    old_base.build_reset_by_resenum(data=[{"id": 1}],resEnmu=ResponseEnum.OK, msg="重制返回")
    return old_base


@app.get("/test_reset_is_success", name="测试is_success")
@access_log()
def test_response():
    old_base = BaseResponse(ResponseEnum.OK, data=[{"id": 1}], msg="正确返回")
    data = old_base.is_success()
    return BaseResponse(ResponseEnum.OK, data={"data": data})


@app.get("/test_expection", name="测试报错")
@access_log()
def test_expection():
    return BaseException(ResponseEnum.AccessDenied)


@app.get("/get_exception_test5", name="测试异常数据")
@access_log(onlyPrintError=True,throwException=True,exceptionStack=True)
def get_exception_test5():
    base = get_Object_Exception(1)

    return BaseResponse(ResponseEnum.OK, data=[{"id": 1}], msg="正确返回")



@app.get("/get_Object_test_ansyc", name="测试返回")
@access_log()
async def get_Object_test_ansyc():
    per = await get_Object_ansyc("1")
    return BaseResponse(resEnum=ResponseEnum.OK,data=per)


@app.get("/get_baseRes_test_ansyc", name="测试添加msg")
@access_log()
async def get_baseRes_test_ansyc():
    baseRes = await get_baseRes_ansyc("2")

    return baseRes


@app.get("/get_no_print_ansyc", name="测试只打印异常日志")
@access_log(onlyPrintError=True)
async def get_no_print_ansyc():
    baseRes = await get_baseRes_ansyc("2")

    return baseRes


@app.get("/get_exception_test_ansyc", name="测试异常数据")
@access_log(onlyPrintError=True)
async def get_exception_test_ansyc():
    base = await get_Object_Exception_ansyc(1)

    return BaseResponse(ResponseEnum.OK, data=[{"id": 1}], msg="正确返回")

@app.get("/get_exception_test2_ansyc", name="测试异常数据")
@access_log(onlyPrintError=True,throwException=True)
async def get_exception_test2_ansyc():
    base = await get_Object_Exception_ansyc(1)

    return BaseResponse(ResponseEnum.OK, data=[{"id": 1}], msg="正确返回")

@app.get("/get_exception_test3_ansyc", name="测试全链路打印异常数据")
@access_log(onlyPrintError=True)
async def get_exception_test3_ansyc():
    base = await get_Object_Exception2_ansyc(1)

    return BaseResponse(ResponseEnum.OK, data=[{"id": 1}], msg="正确返回")

@app.get("/get_exception_test4_ansyc", name="测试全链路打印异常数据")
@access_log(onlyPrintError=True)
async def get_exception_test4_ansyc():
    base = await get_baseRes_ansyc(1)

    return BaseResponse(ResponseEnum.OK, data=[{"id": 1}], msg="正确返回")


@app.get("/get_maxrt_test_ansyc", name="测试只打印大于指定响应的日志")
@access_log(onlyPrintMaxRt=10)
async def get_maxrt_test_ansyc():
    re = BaseResponse(ResponseEnum.OK,None)
    result = await get_Object_MaxRt_ansyc("1")
    re.build_reset_by_resp(result)

    return re
@app.get("/get_maxrt_test2_ansyc", name="测试只打印大于指定响应的日志")
@access_log(onlyPrintMaxRt=200000)
async def get_maxrt_test2_ansyc():
    re = BaseResponse(ResponseEnum.OK,None)
    result = await get_Object_MaxRt_ansyc("1")
    re.build_reset_by_resp(result)

    return re

@app.get("/get_exception_test5_ansyc", name="测试异常数据")
@access_log(onlyPrintError=True,throwException=True,exceptionStack=True)
async def get_exception_test5_ansyc():
    base = await get_Object_Exception_ansyc(1)

    return BaseResponse(ResponseEnum.OK, data=[{"id": 1}], msg="正确返回")

@app.get("/get_customer_test5_ansyc", name="测试异常数据")
@access_log(onlyPrintError=True,throwException=True,exceptionStack=True)
async def get_customer_test5_ansyc():
    base = await get_baseRes_ansyc(1)

    return BaseResponse(ResponseEnum.GitError, data=[{"id": 1}], msg="正确返回")


class UserDefinedErrorEnmu():
    GitError = ResCode("GitError", "git产生错误！！", HttpStatus.GATEWAY_TIMEOUT)

if __name__ == '__main__':
    ResponseEnum.update_response_enum(UserDefinedErrorEnmu)
    EnhancedJSONSerializer.MAX_DEPTH = 5
    uvicorn.run('test_fastapi:app', port=7080, host='0.0.0.0', proxy_headers=False,
                timeout_keep_alive=300)
