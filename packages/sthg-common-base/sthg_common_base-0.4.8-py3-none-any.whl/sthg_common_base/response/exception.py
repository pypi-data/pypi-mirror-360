#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author  ：DongQing
@File    ：exception.py
@Time    ：2025/3/31
@Desc    ：
"""
__all__ = [
    'BaseException',
    'CustomException',
    'register_exception_handlers'
]

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError, StarletteHTTPException
from pydantic import ValidationError
from starlette.responses import JSONResponse

from sthg_common_base.response.httpCodeEnum import HttpStatus, ResponseEnum
from sthg_common_base.utils.constants import Constants
from sthg_common_base.utils.log_util import Logger, LoggerUtil, TraceID, MDC
import inspect
import os
import traceback

ERROR_TYPE_MAPPING = {
    "value_error.number.not_ge": "{},值不能小于:{}",
    "value_error.list.min_items": "{},元素个数至少为:{}",
    "value_error.str": "{},元素个数至少为:{}",
    "value_error.missing": "字段必填",
    "type_error.integer": "必须是整数类型",
    "value_error.number.not_gt": "必须大于 {limit_value}",
}

KeyErrorChineseDict = {
    "": ""
}


# 定义一个自定义异常类
class BaseException(Exception):
    code: int
    busiMsg: str
    busiCode: str
    exceptionStack: str
    requestId: str

    def __init__(self, resEnum: ResponseEnum, msg: str = None, *args):
        if msg and args:
            msg = msg.format(*args)
        self.code = resEnum.getHttpCode
        self.busiCode = resEnum.getBusiCode
        if msg:
            self.busiMsg = f"{resEnum.getBusiMsg},{msg}"
        else:
            self.busiMsg = resEnum.getBusiMsg

        super().__init__(self.busiMsg)

    def __call__(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.code,
            content={
                "code": self.code,
                "busiCode": self.busiCode,
                "busiMsg": self.busiMsg,
                "data": None,
                "requestId": self.requestId,
                "exceptionStack": self.exceptionStack,
            }
        )


class CustomException(BaseException):
    """自定义异常类，继承自 BaseException"""
    pass


def register_exception_handlers(app: FastAPI):
    # 覆盖原生 HTTPException 处理器（处理其他 HTTP 错误）
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        LoggerUtil.error_log(f"Unhandled http_exception_handler: {exc}")
        excFlag = MDC.get("exceptionStack", False)
        exmsg = None
        if excFlag:
            exmsg = format_exception_msg(exc)

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "busiMsg": str(exc.detail),
                "busiCode": exc.status_code,
                "data": None,
                "requestId": TraceID.get_trace(),
                "exceptionStack": exmsg
            },
        )

    # Pydantic 模型校验错误（如直接调用 Pydantic 模型时）
    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(request: Request, exc: ValidationError):
        error_details = [f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors()]
        excFlag = MDC.get("exceptionStack", False)
        exmsg = None
        if excFlag:
            exmsg = format_exception_msg(exc)
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "code": HttpStatus.BAD_REQUEST,
                "busiMsg": f"{ResponseEnum.InvalidRequest.getBusiMsg},{error_details}",
                "busiCode": ResponseEnum.InvalidRequest.getBusiCode,
                "data": None,
                "requestId": TraceID.get_trace(),
                "exceptionStack": exmsg
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        LoggerUtil.error_log(f"Unhandled validation_exception_handler: {exc}")
        error_messages = ""
        excFlag = MDC.get("exceptionStack", False)
        exmsg = None
        if excFlag:
            exmsg = format_exception_msg(exc)
        try:
            errors = exc.errors()
            error_messages = []
            for error in errors:
                error_type = error.get("type")
                msg_template = ERROR_TYPE_MAPPING.get(error_type, "{},验证失败")

                msg = ""
                if "{}" in msg_template:
                    msg = msg_template.format(error_type + " " + error.get("msg"),
                                              error.get("ctx", {}).get("limit_value", ""))
                else:
                    msg = error_type + " " + '.'.join(map(str, error['loc'])) + ":" + msg_template

                error_messages.append(msg)
        except Exception as ex:
            LoggerUtil.error_log(f"捕获异常逻辑失败: {ex}")

        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "code": HttpStatus.BAD_REQUEST,
                "busiMsg": "; ".join(error_messages),
                "busiCode": ResponseEnum.InvalidArgument.getBusiCode,
                "data": None,
                "requestId": TraceID.get_trace(),
                "exceptionStack": exmsg
            },
        )

    # 自定义异常处理
    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        LoggerUtil.error_log(f"Unhandled custom_exception_handler: {exc}")
        res = ResponseEnum.from_code(exc.busiCode)
        status_code = HttpStatus.INTERNAL_SERVER_ERROR
        busiMsg = ResponseEnum.InternalError.getBusiMsg
        busiCode = ResponseEnum.InternalError.getBusiCode
        if res:
            status_code = res.getHttpCode
            busiMsg = res.getBusiMsg
            busiCode = res.getBusiCode
        excFlag = MDC.get("exceptionStack", False)
        exmsg = None
        if excFlag:
            exmsg = format_exception_msg(exc)

        return JSONResponse(
            status_code=status_code,
            content={
                "code": status_code,
                "busiMsg": busiMsg,
                "busiCode": busiCode,
                "data": None,
                "requestId": TraceID.get_trace(),
                "exceptionStack": exmsg
            }
        )

    # 自定义异常处理
    @app.exception_handler(BaseException)
    async def custom_exception_handler(request: Request, exc: BaseException):
        LoggerUtil.error_log(f"Unhandled custom_exception_handler: {exc}")
        excFlag = MDC.get("exceptionStack", False)
        exmsg = None
        if excFlag:
            exmsg = format_exception_msg(exc)
        res = ResponseEnum.from_code(exc.busiCode)
        status_code = HttpStatus.INTERNAL_SERVER_ERROR
        busiMsg = ResponseEnum.InternalError.getBusiMsg
        busiCode = ResponseEnum.InternalError.getBusiCode
        if res:
            status_code = res.getHttpCode
            busiMsg = res.getBusiMsg
            busiCode = res.getBusiCode

        return JSONResponse(
            status_code=status_code,
            content={
                "code": status_code,
                "busiMsg": busiMsg,
                "busiCode": busiCode,
                "data": None,
                "requestId": TraceID.get_trace(),
                "exceptionStack": exmsg
            }
        )

    # 全局异常兜底处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # 记录完整的错误堆栈
        LoggerUtil.error_log(f"Unhandled exception: {exc}")
        excFlag = MDC.get("exceptionStack", False)
        exmsg = None
        if excFlag:
            exmsg = format_exception_msg(exc)
        return JSONResponse(
            status_code=ResponseEnum.InternalError.getHttpCode,
            content={
                "code": ResponseEnum.InternalError.getHttpCode,
                "busiMsg": ResponseEnum.InternalError.getBusiMsg,
                "busiCode": ResponseEnum.InternalError.getBusiCode,
                "data": None,
                "requestId": TraceID.get_trace(),
                "exceptionStack": exmsg
            }
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        # 记录完整的错误堆栈
        uri = request.url.path
        if Constants.Favicon != uri:
            LoggerUtil.error_log(f"Unhandled exception: {uri},{exc}")
        excFlag = MDC.get("exceptionStack", False)
        exmsg = None
        if excFlag:
            exmsg = format_exception_msg(exc)
        return JSONResponse(
            status_code=ResponseEnum.InvalidRequest.getHttpCode,
            content={
                "code": ResponseEnum.InvalidRequest.getHttpCode,
                "busiMsg": exc.detail,
                "busiCode": ResponseEnum.InvalidRequest.getBusiCode,
                "data": None,
                "requestId": TraceID.get_trace(),
                "exceptionStack": exmsg
            }
        )


def get_project_root_name(file_path: str) -> str:
    """
    通过文件路径回溯获取项目根目录名称
    示例输入: /Users/edy/.../sthg_common_base_0422/sthg_common_base/utils/some_file.py
    返回: sthg_common_base_0422
    """
    # 获取调用文件的绝对路径并提取目录
    current_dir = os.path.dirname(os.path.abspath(file_path))

    # 向上回溯两级目录（根据项目结构调整层级）
    project_root_path = os.path.dirname(os.path.dirname(current_dir))

    # 提取最后一级目录名作为项目名称
    return os.path.basename(project_root_path)


def format_exception_msg(exc: Exception, printEx: bool = True) -> str:
    exmsg = None
    """
    将异常堆栈信息压缩为单行字符串，并聚焦关键错误位置
    :param exc: Exception实例
    :return: 单行格式化的错误信息
    """
    if printEx:
        LoggerUtil.error_log(f"Internal exception: {exc}")

    if not exc:
        return exmsg

    try:
        # 自动获取调用者文件路径
        frame = inspect.currentframe().f_back
        file_path = inspect.getframeinfo(frame).filename

        # 动态获取项目根目录名称
        project_name = get_project_root_name(file_path)

        # 获取完整堆栈
        tb = traceback.format_exception(type(exc), exc, exc.__traceback__)

        # 过滤并格式化关键堆栈
        error_lines = []
        for line in tb:
            line_clean = line.strip()
            if (
                    f"site-packages{os.sep}" not in line_clean  # 过滤第三方库
                    and project_name in line_clean  # 聚焦本项目
            ):
                error_lines.append(line_clean.replace("\n", " "))

        if error_lines and len(tb)>0 and   len(error_lines)<len(tb):
            error_lines.append(tb[-1])
        # 提取核心错误（最后一行）并合并为单行
        if error_lines and len(error_lines) > 0:
            exmsg = ",\n    ".join(error_lines)

    except Exception as e:
        return LoggerUtil.error_log(f"{e}")
    return exmsg
