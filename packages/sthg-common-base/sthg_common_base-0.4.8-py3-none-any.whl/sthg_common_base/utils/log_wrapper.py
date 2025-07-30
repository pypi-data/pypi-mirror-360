import asyncio
import inspect
import os
import time
import functools
import traceback
import json
from typing import Callable, Dict, Any, Type, get_type_hints, get_origin
import ipaddress


import datetime

from sthg_common_base.response.httpCodeEnum import ResponseEnum, HttpStatus
from sthg_common_base.response.response import BaseResponse
from sthg_common_base.response.exception import BaseException
from .access_info import AccessInfo
from .constants import Constants
from .log_util import TraceID, local_trace, Logger, get_module_line, get_main_tracebak, \
    clean_error_message, _request_var, serialize_object, MDC, LoggerUtil
from sthg_common_base.response.exception import CustomException, format_exception_msg
from datetime import datetime
from .utils import get_project_name

from fastapi import (
    Request,
    Response, HTTPException
)

from ..response.json_serializer import EnhancedJSONSerializer


def get_process_time(start_time, end_time):
    milliseconds = int(round(end_time.timestamp() * 1000)) - round(start_time.timestamp() * 1000)
    return milliseconds

def get_log_time(start_time, end_time):
    milliseconds = int(round(end_time.timestamp() * 1000)) - round(start_time.timestamp() * 1000)
    return milliseconds



def http_status(response):
    status = Constants.Str_Place
    if response and type(response) == BaseResponse:
        status = response.code
    if hasattr(response, 'code'):
        status = change_http_code(response.code)
    elif hasattr(response, 'status_code'):
        status = change_http_code(response.status_code)
    elif hasattr(response, 'http_code'):
        status = change_http_code(response.http_code)

    return status


def get_trace_id():
    if hasattr(local_trace, 'trace_id'):
        return local_trace.trace_id
    return ''

def get_ip(request):
    return request.client.host


async def get_request_params(request):
    params =None
    try:
        params = dict(request.query_params) if request.query_params else "-"
        if not params:
            byte_body = await request.body()
            params = json.loads(byte_body.decode()) if byte_body else "-"
    except Exception as e:
        LoggerUtil.error_log(f"日志打印异常 get_request_header:{e}")
    return params


def get_request_header(access_kwargs):
    guid = Constants.Str_Place
    requestId = Constants.Str_Place
    userId = Constants.Str_Place
    host = Constants.Str_Place
    user_ip = Constants.Str_Place
    req_url = Constants.Str_Place
    try:
        request =  _request_var.get()
        user_ip = get_client_ip(request)
        request_header = request.headers
        host = request_header['host']
        req_url = request.url.path
        guid = request_header.get('X-GUID') if request_header.get('X-GUID') else "-"
        requestId = TraceID.get_trace() if TraceID.get_trace() else "-"
        if request_header.get('X-User-ID'):
            userId = request_header.get('X-User-ID')
        elif request_header.get('user_id'):
            userId = request_header.get('user_id')
        else:
            userId = "-"
        if not host:
            host = Constants.Str_Place
        if not guid:
            guid = Constants.Str_Place
        if not requestId:
            requestId = Constants.Str_Place
        if not user_ip:
            user_ip = Constants.Str_Place
        if not req_url:
            req_url = Constants.Str_Place
    except Exception as ex :
        LoggerUtil.error_log(f"日志打印异常 get_request_header:{ex}")

    header = {"user_ip": user_ip, "host": host, 'user_id': userId, "guid": guid,
              "requestId": requestId,"request_url":req_url}
    return header


def get_client_ip(request: Request) -> str:
    try:
        # 从 X-Forwarded-For 头获取 IP 地址
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            # 取第一个 IP 地址
            ips = x_forwarded_for.split(",")
            for ip in ips:
                ip = ip.strip()
                if is_valid_ip(ip):
                    return ip

        # 从 X-Real-IP 头获取 IP 地址
        x_real_ip = request.headers.get("X-Real-IP")
        if x_real_ip and is_valid_ip(x_real_ip):
            return x_real_ip

        # 从 X-Cluster-Client-IP 头获取 IP 地址
        x_cluster_client_ip = request.headers.get("X-Cluster-Client-IP")
        if x_cluster_client_ip and is_valid_ip(x_cluster_client_ip):
            return x_cluster_client_ip

        # 直接从请求对象获取客户端的主机信息
        client_host = request.client.host
        if client_host and is_valid_ip(client_host):
            return client_host
    except Exception as ex:
        LoggerUtil.error_log(f"获取ip失败:{ex}")
        # 如果所有方法都失败，返回空字符串或默认值

    return Constants.Str_Place

def is_valid_ip(ip: Any) -> bool:
    """全面验证 IPv4/IPv6 地址，不依赖异常机制"""
    # 前置检查：确保输入为字符串且非空
    if not isinstance(ip, str) or not ip.strip():
        return False

    # 快速过滤明显不符合格式的输入
    if ip.count('.') == 3:  # 疑似 IPv4
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        for part in parts:
            if not part.isdigit() or not 0 <= int(part) <= 255:
                return False
        return True  # 通过快速检查

    elif ip.count(':') >= 2:  # 疑似 IPv6
        # 检查缩写格式（如 ::）
        if ':::' in ip:
            return False
        # 分割各部分并验证长度
        parts = ip.split(':')
        if len(parts) > 8:
            return False
        # 检查十六进制字符
        hex_chars = set('0123456789abcdefABCDEF')
        for part in parts:
            if not part:
                continue  # 允许空段（如 ::）
            if not all(c in hex_chars for c in part):
                return False
            if len(part) > 4:
                return False
        return True  # 通过快速检查

    # 若无法快速判断，使用 ipaddress 库深度验证
    try:
        ipaddress.ip_address(ip)
        return True
    except Exception:
        return False

def change_return_recode(code):
    """
    code:返回code
    """
    recode = Constants.Str_Place

    try:
        if isinstance(code, int):
            bcode = int(code)
            if bcode in (Constants.Code_0,Constants.Code_1):
                recode = Constants.CodeMap[bcode]
            if HttpStatus.CONTINUE < code and code <= HttpStatus.GATEWAY_TIMEOUT:
                for recode, (start, end) in Constants.HttpRangesMap.items():
                    if start <= code <= end:
                        return recode

    except Exception as ex:
        LoggerUtil.error_log(f"转化异常:{ex}")

    return recode

def change_http_code(code):
    httpcode = Constants.Str_Place
    try:
        code = int(code)
        if HttpStatus.CONTINUE < code and code < HttpStatus.INTERNAL_SERVER_ERROR:
            httpcode = str(code)

    except Exception as ex:
        LoggerUtil.error_log(f"转化异常:{code},{ex}")

    return httpcode


def get_response_busicode(response):
    busicode = Constants.Str_Place
    # 拿到 code
    if response and type(response) == BaseResponse:
        busicode = response.busiCode
    elif response and type(response) == dict:
        busicode = response.get('busiCode') or response.get('code') or response.get('Code') or response.get('CODE')


    return busicode


def get_response_msg(response):
    msg = Constants.Str_Place
    if response and type(response) == BaseResponse:
        msg = response.busiMsg
    elif response and type(response) == dict:
        msg = response.get('busiMsg') or response.get('msg') or response.get('message') or response.get('Message')
    return msg

def get_re_code(response):
    recode = Constants.Str_Place
    if response and type(response) == BaseResponse:
        recode = change_return_recode(response.code)
    elif response and type(response) == dict:
        recode_tm = response.get('code') or response.get('Code') or response.get('CODE') or response.get('httpstatus')
        recode = change_return_recode(recode_tm)

    return recode



def get_response_data(response):
    """获取返回的对象数据"""
    data = Constants.Str_Place
    if response and type(response) == BaseResponse:
        data = response.data
    elif response and type(response) == dict:
        if Constants.DATA in response:
            data = response.get(Constants.DATA)
    elif response:
        data = response

    return data


async def get_request_data1(request: Request, args: tuple, kwargs: Dict[str, Any], func) -> Dict[str, Any]:
    params = {}
    if request:
        # 1. 获取查询参数（同步操作）
        query_params = dict(request.query_params)
        params.update(query_params)

        # 2. 获取请求体参数（异步操作）
        try:
            if inspect.iscoroutinefunction(func):
                # 异步函数中获取请求体
                body = await request.json()
                params.update(body)
            else:
                # 同步函数中获取请求体
                body_bytes = await request.body()
                if body_bytes:
                    body_str = body_bytes.decode('utf-8')
                    body_json = json.loads(body_str)
                    params.update(body_json)
        except Exception as e:
            LoggerUtil.error_log(f"Failed to parse request body: {e}")

    # 3. 获取函数参数签名（同步操作）
    sig = inspect.signature(func)
    try:
        bound_args = sig.bind(*args, **kwargs)
    except TypeError as e:
        LoggerUtil.error_log(f"Function signature mismatch: {e}")
        return params
    bound_args.apply_defaults()
    func_params = dict(bound_args.arguments)
    params.update(func_params)

    return params


def get_request_data(request: Request, args: tuple, kwargs: Dict[str, Any], func) -> Dict[str, Any]:
    params = {}

    if request:
        # 1. 获取查询参数（始终同步）
        params.update(dict(request.query_params))
        # 使用缓存的body
        if hasattr(request, "_cached_body"):
            body_bytes = request._cached_body
        else:
            body_bytes = b''

        try:
            if body_bytes:
                content_type = request.headers.get("content-type", "").lower()
                # JSON格式判断
                if "application/json" in content_type:
                    try:
                        params.update( asyncio.run( request.json()))
                    except json.JSONDecodeError as je:
                        LoggerUtil.error_log(f"JSON解析失败，原始数据: {body_bytes.decode()}")
                        params["raw_body"] = body_bytes.decode(errors='replace')
                # Form表单判断
                elif "form-data" in content_type or "x-www-form-urlencoded" in content_type:
                    form_data =   asyncio.run(request.form())
                    params.update({k: v for k, v in form_data.items()})
                # 其他类型保留原始数据
                else:
                    params["raw_body"] = body_bytes.decode(errors='replace')
        except Exception as e:
            LoggerUtil.error_log(f"请求体处理异常: {str(e)}")

    # 3. 函数参数合并（优化同步/异步处理）
    try:
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        params.update(bound_args.arguments)
    except TypeError as te:
        LoggerUtil.error_log(f"函数参数绑定异常: {str(te)}")

    return params



"""
"time":请求时间
,"traceId":全链路Id
,"method":访问方法
,"status":http状态码
,"code":业务状态码
,"msg": 返回描述，当异常时，可以把简略堆栈放里面
,"resRT": 响应时长
,"logRT": 日志打印耗时
,"guid": 留空
,"requestId":用户访问唯一码
,"userId": 用户id
,"extObj": 扩展信息：包含用Ip,和请求header
,"reqParams": 请求参数
,"reData": 返回参数
"""

# 异常注册表
_exception_registry: Dict[Type[Exception], ResponseEnum] = {}

def register_exception(exc_type: Type[Exception], resEnum: ResponseEnum):
    """注册异常类型与响应枚举的关联"""
    _exception_registry[exc_type] = resEnum


# 依赖函数，用于获取所有类型的参数
async def request_params(request):
    # # 路径参数
    path_params = request.path_params
    # 查询参数
    query_params = dict(request.query_params)

    content_type = request.headers.get('content-type') if request.headers.get('content-type') else ''
    # 表单数据
    form_data = {}
    #不可识别数据
    others = ''
    # 请求体数据
    body_data = {}
    try:
        if content_type and 'application/json' in content_type:
            body_data = await request.body()
            body_data = json.dumps(body_data.decode())
        elif content_type and 'multipart/form-data' in content_type:
            if 'multipart/form-data; boundary=' in content_type:
                form = await asyncio.wait_for(request.form(), timeout=10)
                has_file = False
                filename = '-'
                for field_name, value in form.items():
                    if hasattr(field_name, 'filename'):
                        has_file = True
                        break
                if has_file:
                    form_data["file_upload"] = 1
                else:
                   form = await request.form()
                   form_data = {key: value for key, value in form.items()}
            else:
                form = await request.form()
                form_data = {key: value for key, value in form.items()}
        elif content_type and 'application/x-www-form-urlencoded' in content_type:
            form = await request.form()
            form_data = {key: value for key, value in form.items()}
        else:
            others = '-'
    except Exception as e:
        pass
    params_input = {}
    if query_params:
        params_input['params'] = query_params
    if form_data:
        params_input['form_data'] = form_data
    if body_data:
        params_input['body'] = body_data
    if others:
        params_input['others'] = others
    return params_input


def get_module_func_by_router(request):
    route = request.scope.get("route")
    if route:
        endpoint = route.endpoint
        # 获取函数的定义信息
        source_lines, start_line = inspect.getsourcelines(endpoint)
        method_name = endpoint.__name__
        module_file = inspect.getmodule(endpoint).__file__
        return module_file, method_name, start_line
    else:
        # pass
        raise HTTPException(status_code=404,detail='路由未找到，请检查请求的 URL 是否正确。')

# 记录api执行日志
def access_log(printReq = True,printResp = True, onlyPrintMaxRt = 0 , onlyPrintError = False, throwException = False,exceptionStack=False):
    """
       printReq:是否打印请求参数
       printResp:是否打印返回参数
       onlyPrintMaxRt:打印方法Rt大于MaxRt的日志(前提是printReq,printResp开启了打印) 毫秒(ms)
       onlyPrintError:打印出现错误的方法日志(前提是printReq,printResp开启了打印)
       exceptionStack:是否在标准返回baseResepone 中填充关键异常信息
       throwException:是否抛出异常
    """

    def decorator(func: Callable) -> Callable:
        # 获取返回类型信息
        return_type = get_type_hints(func).get('return', None)
        origin = get_origin(return_type)
        is_base_response = origin is not None and issubclass(origin, BaseResponse)
        #Accesslog必须返回BaseResponse

        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                MDC.put("printReq", printReq)
                MDC.put("printResp", printResp)
                MDC.put("exceptionStack", exceptionStack)
                if onlyPrintMaxRt > 0:
                    MDC.put_min_replace("printMaxRt", onlyPrintMaxRt)
                MDC.put("printError", onlyPrintError)

                start_time = datetime.now()
                # 尝试从参数中获取 Request 对象
                header = get_request_header(kwargs)
                request_url = header['request_url']
                moduler_func_line = Constants.Str_Place
                process_time = 0
                log_time = 0
                custom_stack = Constants.Str_Place
                resp_data = Constants.Str_Place
                params = Constants.Str_Place
                busimsg = ResponseEnum.OK.getBusiMsg
                busicode = ResponseEnum.OK.getBusiCode
                log_time_start = None
                response = None
                throwEx = None

                access_info = AccessInfo(header, process_time, Constants.SUCCESS, busicode,
                                         busimsg, moduler_func_line, params, resp_data, log_time, custom_stack,request_url
                                         )
                request = None
                # response = None
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
                if not request:
                    request = _request_var.get()

                try:
                    params =  get_request_data(request,args, kwargs,func)
                    method_name = func.__name__
                    module = inspect.getmodule(func)
                    if module is not None and hasattr(module, '__file__'):
                        # 获取模块对应的文件路径
                        project_root = os.getcwd()
                        # current_dir = os.path.dirname(os.path.abspath(project_root))
                        module_file = module.__file__
                        relative_path = os.path.relpath(module_file, project_root)
                        module_path = relative_path.replace(os.sep, '.')[:-3]  # 去除 .py 扩展名
                        new_module_path = module_path.split('.')[-1]
                        moduler_func_line = "{}.{}".format(new_module_path, method_name)
                except Exception as ex:
                    LoggerUtil.error_log(
                        f"初始化日志异常:method_name:{method_name},module:{module},moduler_func_line:{moduler_func_line},{ex}")
                try:
                    if asyncio.iscoroutinefunction(func) or 'function' not in str(type(func)):
                        response = await func(*args, **kwargs)
                        if response and not isinstance(response, dict):
                            response = response
                    process_time = get_process_time(start_time, datetime.now())
                    access_info.process_time = process_time
                except Exception as ex:
                    throwEx = ex
                    process_time = get_process_time(start_time, datetime.now())
                    LoggerUtil.error_log(
                        f"方法执行异常:method_name:{method_name},module:{module},moduler_func_line:{moduler_func_line},{ex}")
                    log_time_start = datetime.now()
                    matched_enum = next(
                        (enum for exc_type, enum in _exception_registry.items() if isinstance(ex, exc_type)),
                        None
                    )
                    if matched_enum:
                        busimsg = matched_enum.getBusiMsg
                        recode = change_return_recode(matched_enum.getHttpCode)
                        busicode = matched_enum.getBusiCode
                        # 封装统一返回结构体
                        response = BaseResponse(ResponseEnum.from_code(busicode), data=None)
                    elif isinstance(ex, BaseException):
                        busimsg = ex.busiMsg
                        recode = change_return_recode(ex.code)
                        busicode = ex.busiCode
                        # 封装统一返回结构体
                        response = BaseResponse(ResponseEnum.from_code(busicode), data=None)
                    elif isinstance(ex, CustomException):
                        busimsg = ex.busiMsg
                        recode = change_return_recode(ex.code)
                        busicode = ex.busiCode
                        # 封装统一返回结构体
                        response = BaseResponse(ResponseEnum.from_code(busicode), data=None)
                    else:
                        busimsg = f"{ex.args}"
                        recode = Constants.ERROR
                        busicode = ResponseEnum.InternalError.getBusiCode
                        # 封装统一返回结构体
                        response = BaseResponse(ResponseEnum.InternalError, data=None)
                    file_path = inspect.getfile(func)
                    # 获取文件所在的目录路径
                    current_dir = os.path.dirname(os.path.abspath(file_path))
                    moduler_func_line = moduler_func_line if moduler_func_line else get_module_line(
                        traceback.format_exc(),
                        project_path=current_dir)
                    custom_stack = get_exception_msg(ex, file_path)

                    access_info.process_time = process_time
                    access_info.log_time = log_time
                    access_info.busi_msg = busimsg
                    access_info.re_code = recode
                    access_info.busi_code = busicode
                    access_info.custom_stack = custom_stack
                try:
                    access_info.moduler_func_line = moduler_func_line
                    access_info.param_input = params
                    if not log_time_start:
                        log_time_start = datetime.now()

                    if response:
                        if isinstance(response, BaseResponse):
                            access_info.re_code = get_re_code(response)
                            access_info.busi_code = get_response_busicode(response)
                            access_info.busi_msg = get_response_msg(response)
                            access_info.resp_data = get_response_data(response)
                            if exceptionStack:
                                exmsg = format_exception_msg(throwEx)
                                response.set_exceptionStack(exmsg)
                        else:
                            access_info.resp_data = response
                    else:
                        access_info.resp_data = response

                    log_time = get_log_time(log_time_start, datetime.now())
                    access_info.log_time = log_time
                    await get_access_log_str(access_info)
                except Exception as ex:
                    LoggerUtil.error_log(f"日志执行异常:{ex}")
                if  throwEx and throwException:
                    raise  throwEx

                return response
            return wrapper
        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                MDC.put("printReq", printReq)
                MDC.put("printResp", printResp)
                MDC.put("exceptionStack", exceptionStack)
                x = MDC.get("exceptionStack", False)
                if onlyPrintMaxRt > 0:
                    MDC.put_min_replace("printMaxRt", onlyPrintMaxRt)
                MDC.put("printError", onlyPrintError)

                start_time = datetime.now()
                # 尝试从参数中获取 Request 对象
                header = get_request_header(kwargs)
                request_url = header['request_url']
                moduler_func_line = Constants.Str_Place
                process_time = 0
                log_time = 0
                custom_stack = Constants.Str_Place
                resp_data = Constants.Str_Place
                params = Constants.Str_Place
                busimsg = ResponseEnum.OK.getBusiMsg
                busicode = ResponseEnum.OK.getBusiCode
                log_time_start = None
                response = None
                throwEx = None

                access_info = AccessInfo(header,process_time, Constants.SUCCESS,busicode,
                   busimsg, moduler_func_line, params, resp_data, log_time, custom_stack,request_url
                )
                request = None
                # response = None
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
                if not request:
                    request =  _request_var.get()

                try:
                    params =  get_request_data(request,args, kwargs,func)
                    method_name = func.__name__
                    module = inspect.getmodule(func)
                    if module is not None and hasattr(module, '__file__'):
                        # 获取模块对应的文件路径
                        project_root = os.getcwd()
                        # current_dir = os.path.dirname(os.path.abspath(project_root))
                        module_file = module.__file__
                        relative_path = os.path.relpath(module_file, project_root)
                        module_path = relative_path.replace(os.sep, '.')[:-3]  # 去除 .py 扩展名
                        new_module_path = module_path.split('.')[-1]
                        moduler_func_line = "{}.{}".format(new_module_path, method_name)
                except Exception as ex:
                    LoggerUtil.error_log(
                        f"初始化日志异常:method_name:{method_name},module:{module},moduler_func_line:{moduler_func_line},{ex}")
                try:
                    response = func(*args, **kwargs)
                    process_time = get_process_time(start_time, datetime.now())
                    access_info.process_time = process_time
                except Exception as ex:
                    throwEx = ex
                    process_time = get_process_time(start_time, datetime.now())
                    LoggerUtil.error_log(
                        f"方法执行异常:method_name:{method_name},module:{module},moduler_func_line:{moduler_func_line},{traceback.format_exc()}")
                    log_time_start = datetime.now()

                    matched_enum = next(
                        (enum for exc_type, enum in _exception_registry.items() if isinstance(ex, exc_type)),
                        None
                    )
                    if matched_enum:
                        busimsg = matched_enum.getBusiMsg
                        recode = change_return_recode(matched_enum.getHttpCode)
                        busicode = matched_enum.getBusiCode
                        # 封装统一返回结构体
                        response = BaseResponse(ResponseEnum.from_code(busicode), data=None)
                    elif isinstance(ex, CustomException):
                        busimsg = ex.busiMsg
                        recode = change_return_recode(ex.code)
                        busicode = ex.busiCode
                        #封装统一返回结构体
                        response = BaseResponse(ResponseEnum.from_code(busicode), data=None)
                    else:
                        busimsg = f"{ex.args}"
                        recode = Constants.ERROR
                        busicode = ResponseEnum.InternalError.getBusiCode
                        # 封装统一返回结构体
                        response = BaseResponse(ResponseEnum.InternalError,data=None)

                    file_path = inspect.getfile(func)
                    # 获取文件所在的目录路径
                    current_dir = os.path.dirname(os.path.abspath(file_path))
                    moduler_func_line = moduler_func_line if moduler_func_line else get_module_line(
                        traceback.format_exc(),
                        project_path=current_dir)
                    custom_stack = get_exception_msg(ex, file_path)

                    access_info.process_time = process_time
                    access_info.log_time = log_time
                    access_info.busi_msg = busimsg
                    access_info.re_code = recode
                    access_info.busi_code = busicode
                    access_info.custom_stack = custom_stack
                try:
                    access_info.moduler_func_line = moduler_func_line
                    access_info.param_input = params
                    if not log_time_start:
                        log_time_start = datetime.now()
                    if response:
                        if isinstance(response, BaseResponse):
                            access_info.re_code = get_re_code(response)
                            access_info.busi_code = get_response_busicode(response)
                            access_info.busi_msg = get_response_msg(response)
                            access_info.resp_data = get_response_data(response)
                            if exceptionStack:
                                exmsg = format_exception_msg(throwEx)
                                response.set_exceptionStack(exmsg)
                        else:
                            access_info.resp_data = response
                    else:
                        access_info.resp_data = response

                    log_time = get_log_time(log_time_start, datetime.now())
                    access_info.log_time = log_time
                    asyncio.run(get_access_log_str(access_info))
                except Exception as ex:
                    LoggerUtil.error_log(f"日志异常:{ex}")
                if throwEx and throwException:
                    raise  throwEx

                return response

            return wrapper

    return decorator

def get_exception_msg(exc,file_path):
    try:
        current_dir = os.path.dirname(os.path.abspath(file_path))
        exc_type = type(exc)
        exc_value = exc
        exc_tb = exc.__traceback__
        # 调用 format_exception 函数格式化异常信息
        formatted_exception = traceback.format_exception(exc_type, exc_value, exc_tb)
        # 打印格式化后的异常信息
        main_error = "Traceback (most recent call last):\n" + get_main_tracebak(''.join(formatted_exception),
                                                                                project_path=current_dir)
    except Exception as e:
        LoggerUtil.error_log(f"日志打印异常get_exception_msg:{e}")

    return main_error

"""
"time":请求时间
,"traceId":全链路Id
,"method":访问方法
,"status":http状态码
,"code":业务状态码
,"msg": 返回描述，当异常时，可以把简略堆栈放里面
,"resRT": 响应时长
,"logRT": 日志打印耗时
,"reqParams": 请求参数
,"reData": 返回参数
"""


# 记录方法执行日志
def service_log(printReq:bool = True,printResp:bool = True, onlyPrintMaxRt:int = 0 , onlyPrintError: bool = False,throwException = True,exceptionStack=False):
    """
       printReq:是否打印请求参数
       printResp:是否打印返回参数
       onlyPrintMaxRt:打印方法Rt大于MaxRt的日志(前提是printReq,printResp开启了打印) 毫秒(ms)
       onlyPrintError:打印出现错误的方法日志(前提是printReq,printResp开启了打印)
      exceptionStack:是否在标准返回baseResepone 中填充关键异常信息
      throwException:是否抛出异常
    """
    def decorator(func: Callable) -> Callable:
        # 获取返回类型信息
        return_type = get_type_hints(func).get('return', None)
        origin = get_origin(return_type)
        is_base_response = origin is not None and issubclass(origin, BaseResponse)

        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                MDC.put("printReq", printReq)
                MDC.put("printResp", printResp)
                MDC.put("exceptionStack",exceptionStack)
                if onlyPrintMaxRt > 0:
                    MDC.put_min_replace("printMaxRt", onlyPrintMaxRt)
                MDC.put("printError", onlyPrintError)

                moduler_func_line = Constants.Str_Place
                process_time = 0
                log_time = 0
                custom_stack = Constants.Str_Place
                resp_data = Constants.Str_Place
                recode = Constants.SUCCESS
                busimsg = ResponseEnum.OK.getBusiMsg
                busicode = ResponseEnum.OK.getBusiCode
                params = get_request_data(None,args, kwargs,func)
                method_name = func.__name__
                module = None
                log_time_start = None
                response = None
                throwEx = None

                try:
                    module = inspect.getmodule(func)
                    if module is not None and hasattr(module, '__file__'):
                        # 获取模块对应的文件路径
                        project_root = os.getcwd()
                        module_file = module.__file__
                        relative_path = os.path.relpath(module_file, project_root)
                        module_path = relative_path.replace(os.sep, '.')[:-3]  # 去除 .py 扩展名
                        new_module_path = module_path.split('.')[-1]
                        moduler_func_line = "{}.{}".format(new_module_path, method_name)
                except Exception as ex:
                    LoggerUtil.error_log(f"getmodule方法执行异常:method_name:{method_name},module:{module},ex:{ex}")
                start_time = datetime.now()
                try:
                    response = await func(*args, **kwargs)
                    if not isinstance(response, dict):
                        response = response
                    process_time = get_process_time(start_time, datetime.now())
                except Exception as ex:
                    throwEx = ex
                    process_time = get_process_time(start_time, datetime.now())
                    LoggerUtil.error_log(
                        f"方法执行异常:method_name:{method_name},module:{module},moduler_func_line:{moduler_func_line},{ex}")
                    log_time_start = datetime.now()
                    matched_enum = next(
                        (enum for exc_type, enum in _exception_registry.items() if isinstance(ex, exc_type)),
                        None
                    )
                    if matched_enum:
                        busimsg = matched_enum.getBusiMsg
                        recode = change_return_recode(matched_enum.getHttpCode)
                        busicode = matched_enum.getBusiCode
                    elif isinstance(ex, CustomException):
                        busimsg = ex.busiMsg
                        recode = change_return_recode(ex.code)
                        busicode = ex.busiCode
                    else:
                        busimsg = f"{ex.args}"
                        recode = Constants.ERROR
                        busicode = ResponseEnum.InternalError.getBusiCode
                    if is_base_response:
                        # 封装统一返回结构体
                        response = BaseResponse(ResponseEnum.from_code(busicode), data=None)
                    file_path = inspect.getfile(func)
                    # 获取文件所在的目录路径
                    current_dir = os.path.dirname(os.path.abspath(file_path))
                    moduler_func_line = moduler_func_line if moduler_func_line else get_module_line(
                        traceback.format_exc(),
                        project_path=current_dir)
                    custom_stack = get_exception_msg(ex,file_path)

                try:
                    if not log_time_start:
                        log_time_start = datetime.now()
                    if response:
                        if isinstance(response, BaseResponse):
                            recode = get_re_code(response)
                            busicode = get_response_busicode(response)
                            busimsg = get_response_msg(response)
                            resp_data = get_response_data(response)
                            if exceptionStack:
                                exmsg = format_exception_msg(throwEx)
                                response.set_exceptionStack(exmsg)
                        else:
                            resp_data = response
                    else:
                        resp_data = response

                    log_time = get_log_time(log_time_start, datetime.now())

                    get_service_log_str(moduler_func_line, process_time, log_time, recode, busicode,
                                              busimsg, params, resp_data, custom_stack)
                except Exception as ex:
                    LoggerUtil.error_log(f"service日志异常:{ex}")
                if throwEx and throwException:
                    raise  throwEx
                return response

            return wrapper
        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                MDC.put("printReq", printReq)
                MDC.put("printResp", printResp)
                MDC.put("exceptionStack", exceptionStack)
                x = MDC.get("exceptionStack", False)
                if onlyPrintMaxRt > 0:
                    MDC.put_min_replace("printMaxRt", onlyPrintMaxRt)
                MDC.put("printError", onlyPrintError)

                moduler_func_line = Constants.Str_Place
                process_time = 0
                log_time = 0
                recode = Constants.SUCCESS
                custom_stack = Constants.Str_Place
                resp_data = Constants.Str_Place
                busimsg = ResponseEnum.OK.getBusiMsg
                busicode = ResponseEnum.OK.getBusiCode
                params = get_request_data(None,args, kwargs,func)
                method_name = func.__name__
                module = None
                log_time_start = None
                response = None
                throwEx = None  # 全局异常

                try:
                    module = inspect.getmodule(func)
                    if module is not None and hasattr(module, '__file__'):
                        # 获取模块对应的文件路径
                        project_root = os.getcwd()
                        module_file = module.__file__
                        relative_path = os.path.relpath(module_file, project_root)
                        module_path = relative_path.replace(os.sep, '.')[:-3]  # 去除 .py 扩展名
                        new_module_path = module_path.split('.')[-1]
                        moduler_func_line = "{}.{}".format(new_module_path, method_name)
                except Exception as ex:
                    LoggerUtil.error_log(f"getmodule方法执行异常:method_name:{method_name},module:{module},ex:{ex}")
                start_time = datetime.now()
                try:
                    response = func(*args, **kwargs)
                    process_time = get_process_time(start_time, datetime.now())
                except Exception as ex:
                    throwEx = ex
                    process_time = get_process_time(start_time, datetime.now())
                    LoggerUtil.error_log(
                        f"方法执行异常:method_name:{method_name},module:{module},moduler_func_line:{moduler_func_line},{ex}")
                    log_time_start = datetime.now()
                    matched_enum = next(
                        (enum for exc_type, enum in _exception_registry.items() if isinstance(ex, exc_type)),
                        None
                    )
                    if matched_enum:
                        busimsg = matched_enum.getBusiMsg
                        recode = change_return_recode(matched_enum.getHttpCode)
                        busicode = matched_enum.getBusiCode
                    elif isinstance(ex, CustomException):
                        busimsg = ex.busiMsg
                        recode = change_return_recode(ex.code)
                        busicode = ex.busiCode
                    else:
                        busimsg = f"{ex.args}"
                        recode = Constants.ERROR
                        busicode = ResponseEnum.InternalError.getBusiCode
                    if is_base_response:
                        # 封装统一返回结构体
                        response = BaseResponse(ResponseEnum.from_code(busicode), data=None)
                    file_path = inspect.getfile(func)
                    # 获取文件所在的目录路径
                    current_dir = os.path.dirname(os.path.abspath(file_path))
                    moduler_func_line = moduler_func_line if moduler_func_line else get_module_line(
                        traceback.format_exc(),
                        project_path=current_dir)
                    custom_stack = get_exception_msg(ex,file_path)

                try:
                    if not log_time_start:
                        log_time_start = datetime.now()
                    if response:
                        if isinstance(response, BaseResponse):
                            recode = get_re_code(response)
                            busicode = get_response_busicode(response)
                            busimsg = get_response_msg(response)
                            resp_data = get_response_data(response)
                            if exceptionStack:
                                exmsg = format_exception_msg(throwEx)
                                response.set_exceptionStack(exmsg)
                        else:
                            resp_data = response
                    else:
                        resp_data = response

                    log_time = get_log_time(log_time_start, datetime.now())

                    # asyncio.run(get_service_log_str(moduler_func_line, process_time, log_time, recode, busicode,
                    #                           busimsg, params, resp_data, custom_stack))
                    get_service_log_str(moduler_func_line, process_time, log_time, recode, busicode,
                                        busimsg, params, resp_data, custom_stack)
                except Exception as ex:
                    LoggerUtil.error_log(f"service日志异常:{ex}")
                    #抛出整异常
                if throwException and throwEx:
                    raise throwEx

                return response

            return wrapper

    return decorator


#
def class_decorator(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        msg = "-"
        reData = '-'
        params = get_request_data(args, kwargs)

        method_name = func.__name__
        module = inspect.getmodule(func)
        if module is not None and hasattr(module, '__file__'):
            # 获取模块对应的文件路径
            project_root = os.getcwd()
            current_dir = os.path.dirname(os.path.abspath(project_root))
            module_file = module.__file__
            relative_path = os.path.relpath(module_file, current_dir)
            module_path = relative_path.replace(os.sep, '.')[:-3]  # 去除 .py 扩展名
            new_module_path = module_path.split('.')[-1]
            moduler_func_line = "{}.{}".format(new_module_path, method_name)
        start_time = time.time()
        response = func(*args, **kwargs)
        process_time = get_process_time(start_time, time.time())
        log_time_start = time.time()
        reData = response if response else reData
        get_service_log_str(moduler_func_line, process_time, log_time_start, "SUCCESS", 'OK', '业务处理成功', msg,
                                  params, reData)
        return response

    return wrapper


def class_log(cls):
    for name, method in vars(cls).items():
        if callable(method) and name != '__init__':  # 排除__init__方法
            setattr(cls, name, class_decorator(method))
    return cls



async def get_access_log_str(access_info):
    # acc_logger, server_logger, error_logger, all_info = create_loggers(default_config)
    try:
        custom_stack = clean_error_message(access_info.custom_stack)
        moduler_func_line = str(access_info.moduler_func_line).replace('...', '')
        re_code = access_info.re_code
        busi_code = access_info.busi_code
        process_time = access_info.process_time
        param_input = access_info.param_input
        respData = access_info.resp_data
        busi_msg = access_info.busi_msg
        logRT = access_info.log_time
        header = access_info.header
        guid = Constants.Str_Place
        userId = Constants.Str_Place
        requestId = Constants.Str_Place
        request_url = access_info.request_url
        if header and type(header) == dict :
            guid = header.get('guid',Constants.Str_Place)
            userId = header.get('userId',Constants.Str_Place)
            requestId = header.get('requestId',Constants.Str_Place)

        printReq = MDC.get("printReq",False)
        printResp =MDC.get("printResp",False)
        printMaxRt = MDC.get("printMaxRt",0)
        printError = MDC.get("printError",False)
        linkPrint = MDC.get("linkPrint",False)

        if not printReq:
            param_input = Constants.Str_Place
        if not printResp:
            respData = Constants.Str_Place

        if respData is not None and Constants.Str_Place != respData:
            respData = EnhancedJSONSerializer.json_serializer(respData)
        if param_input is not None and Constants.Str_Place != param_input:
            param_input = EnhancedJSONSerializer.json_serializer(param_input)

        project_name = get_project_name()

        info_msg = f"""{project_name}\t {moduler_func_line}\t reqUrl:{request_url}\t {re_code}\t {busi_code}\t {busi_msg}\t RT:{process_time}\t logRt:{logRT}\t {guid}\t {userId}\t {requestId}\t header:{header}\t reqParam:{param_input}\t respParam:{respData}\t {custom_stack}"""
        isPrint = True

        #如果设置了只打印失败的日志,或者RT超过阈值的日志,那么其他情况不打印日志
        if printError or printMaxRt > 0:
            isPrint = False
            if printError and Constants.ERROR == re_code:
                isPrint = True
                linkPrint = True
            if process_time > 0 and process_time > printMaxRt and printMaxRt > 0:
                isPrint = True
                linkPrint = True
        if isPrint or linkPrint:
            Logger.acc_log(str(info_msg))
            MDC.put("linkPrint",linkPrint)

    except Exception as e:
        LoggerUtil.error_log('access log error :{}'.format(str(e)))

def get_service_log_str(method, process_time, logRT, re_code, busicode, busimsg, reqParam,
                              reData,custom_stack):
    # acc_logger, server_logger, error_logger, all_info = create_loggers(default_config)
    try:
        custom_stack = clean_error_message(custom_stack)
        printReq = MDC.get("printReq",False)
        printResp = MDC.get("printResp",False)
        printMaxRt = MDC.get("printMaxRt",0)
        printError = MDC.get("printError",False)
        linkPrint = MDC.get("linkPrint",False)


        if not method or method == "":
            method = Constants.Str_Place
        if not re_code or re_code == "":
            re_code = Constants.Str_Place
        if not busicode or busicode == "":
            busicode = Constants.Str_Place
        if not busimsg or busimsg == "":
            busimsg = Constants.Str_Place
        if not reqParam:
            reqParam = Constants.Str_Place
        if not reData :
            reData = Constants.Str_Place
        if not custom_stack or method == "":
            method = Constants.Str_Place

        if not printReq:
            reData = Constants.Str_Place
        if not printResp:
            reqParam = Constants.Str_Place

        if reData is not None and Constants.Str_Place != reData:
            reData = EnhancedJSONSerializer.json_serializer(reData)
        if reqParam is not None and Constants.Str_Place != reqParam:
            reqParam = EnhancedJSONSerializer.json_serializer(reqParam)

        project_name = get_project_name()

        service_msg = f"""{project_name}\t {method}\t {re_code}\t {busicode}\t {busimsg}\t RT:{process_time}\t logRT:{logRT}\t reqParam:{reqParam}\t respParam:{reData}\t {custom_stack}"""

        isPrint = True
        # 如果设置了只打印失败的日志,或者RT超过阈值的日志,那么其他情况不打印日志
        if printError or printMaxRt > 0:
            isPrint = False
            if printError and Constants.ERROR == re_code:
                isPrint = True
                linkPrint = True
            if process_time > 0 and process_time > printMaxRt and printMaxRt > 0:
                isPrint = True
                linkPrint = True
        if isPrint or linkPrint:
            Logger.service_log(str(service_msg))
            MDC.put("linkPrint",linkPrint)

    except Exception as e:
        LoggerUtil.error_log(f"service log error :{e}")

def set_access_info(access_info: dict,process_time,log_time,
                    remsg,recode,busicode,custom_stack,moduler_func_line,params,
                    return_desc,resp_data) -> dict:
    if process_time:
        access_info['process_time'] = process_time
    if log_time:
        access_info['log_time'] = log_time
    if remsg:
        access_info['msg'] = remsg
    if recode:
        access_info['re_code'] = recode
    if busicode:
        access_info['busi_code'] = busicode
    if custom_stack:
        access_info['custom_stack'] = custom_stack
    if moduler_func_line:
        access_info['moduler_func_line'] = moduler_func_line
    if params:
        access_info['param_input'] = params
    if return_desc:
        access_info['return_desc'] = return_desc
    if resp_data:
        access_info['resp_data'] = resp_data

    return access_info
