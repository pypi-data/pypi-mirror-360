import asyncio
import inspect
import logging
import uuid
import os
from datetime import datetime
import threading
from contextvars import ContextVar
from logging.handlers import TimedRotatingFileHandler


from fastapi.routing import APIRoute
from sympy.logic.algorithms.dpll2 import Level
from fastapi import (
    FastAPI,
    Request,
    Response, HTTPException
)

from sthg_common_base.utils.constants import Constants


# 定义线程局部变量类
class LocalTrace(threading.local):
    def __init__(self):
        super().__init__()
        self.trace_id = None  # 预定义 trace_id
        self.request = None   # 预定义 request
# 自定义trace_filter属性名
TRACE_FILTER_ATTR = "trace_filter"
# 当前线程的local_trace, 需要添加全局trace_id, 使用示例：trace.trace_id
local_trace = LocalTrace()
formatter = logging.Formatter(
    '%(asctime)s \t ThreadID=%(thread)d \t ThreadName=%(threadName)s \t %(trace_id)s \t %(name)s \t %(levelname)s \t %(message)s')
_trace_id: ContextVar[str] = ContextVar('x_trace_id', default="-")
_x_request_id: ContextVar[str] = ContextVar('_x_request_id', default="-")
_request_var: ContextVar[Request] = ContextVar('request', default=None)


def serialize_object(obj):
    """
    将对象转换为可序列化的形式
    """
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)


# 日志格式化中通过过滤器获取ContextVar的值
class TraceLogFilter(logging.Filter):
    def filter(self, record):
        record.trace_id = _trace_id.get()
        # 可根据需要添加其他变量
        return True

def register_log_middleware(app: FastAPI):
    @app.middleware("http")
    async def log_middleware(request: Request, call_next):
        # 首先缓存请求体
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                body = await request.body()
                request._cached_body = body
                # 重新包装成新 Request
                async def receive():
                    return {"type": "http.request", "body": body}

                request = Request(request.scope, receive=receive)
            except Exception:
                request._cached_body = b''

        _trace_id_val = request.headers.get("X-Request-Id", None)
        if not _trace_id_val:
            TraceID.new_trace()
            _trace_id_val = TraceID.get_trace()

        # 设置 ContextVar
        trace_token = _trace_id.set(_trace_id_val)
        request_token = _request_var.set(request)

        try:
            response = await call_next(request)
            response.headers["X-Request-Id"] = _trace_id_val
            return response
        finally:
            # 恢复所有上下文
            _trace_id.reset(trace_token)
            _request_var.reset(request_token)
            MDC.clear()  # 关键：恢复 MDC 到中间件入口状态

mdc_context = ContextVar("mdc_context", default=None)

class MDC:
    @staticmethod
    def put(key, value):
        current_ctx = mdc_context.get()
        # 如果当前上下文未初始化，创建新字典
        if current_ctx is None:
            current_ctx = {}
            mdc_context.set(current_ctx)
        # 仅当key不存在时设置
        if key not in current_ctx:
            current_ctx[key] = value

    @staticmethod
    def put_min_replace(key, new_value):
        '''替换最小值'''
        if new_value is None:
            return
        current_ctx = mdc_context.get()
        # 如果当前上下文未初始化，创建新字典
        if current_ctx is None:
            current_ctx = {}
            mdc_context.set(current_ctx)
        # 仅当key不存在时设置
        if key in current_ctx:
            value = current_ctx.get(key)
            if  value is None or value > new_value:
                current_ctx[key] = new_value
        else:
            current_ctx[key] = new_value

    @staticmethod
    def get(key,any):
        current_ctx = mdc_context.get()
        if current_ctx is None:
            return any
        value = current_ctx.get(key)
        if not value:
            value = any
        return value

    @staticmethod
    def clear():
        # 将当前上下文重置为None，确保下次访问时重新初始化
        mdc_context.set(None)

# 自定义日志格式器，用于格式化包含根方法路径的日志消息
class CustomFormatter(logging.Formatter):
    def format(self, record):
        # 定义自定义格式字符串，包含根方法路径
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(root_method_path)s - %(message)s'
        return super().format(record, format_string)


class TraceID:
    @staticmethod
    def set(req_id: str) -> ContextVar[str]:
        """设置请求ID，外部需要的时候，可以调用该方法设置
        Returns:
            ContextVar[str]: _description_
        """
        if req_id:
            _x_request_id.set(req_id)
        return _x_request_id

    @staticmethod
    def set_trace(trace_id: str) -> ContextVar[str]:
        """设置trace_id
        Returns:
            ContextVar[str]: _description_
        """
        if trace_id:
            _trace_id.set(trace_id)
        return _trace_id

    @staticmethod
    def new_trace():
        trace_id = uuid.uuid4().hex
        _trace_id.set(trace_id)

    @staticmethod
    def get_trace() -> str:

        """获取trace_id
        Returns:
            str: _description_
        """
        id = Constants.Str_Place
        try:
            id = _trace_id.get()
        except Exception as e:
            LoggerUtil.error_log(f"{e}")

        return id


class TraceFilter(logging.Filter):
    """
    通过在record中添加trace_id, 实现调用跟踪和日志打印的分离
    """

    def __init__(self, name=""):
        """
        init
        @param name: filter name
        """
        super().__init__(name)

    def filter(self, record):
        """
        重写filter方法
        @param record: record
        @return:
        """
        # trace_id = local_trace.trace_id if hasattr(local_trace, 'trace_id') else uuid.uuid1()
        record.trace_id = _trace_id.get()
        return True

class TraceLogger:
    _loggers = {}

    @staticmethod
    def get_log_file_path(logger_name, config):
        # 保持原有路径生成逻辑不变
        log_dir = config.get("log_dir", "./logs")
        current_working_directory = os.getcwd()
        log_dir_path = os.path.join(current_working_directory, log_dir)
        if not os.path.exists(log_dir_path):
            os.makedirs(log_dir_path)
        log_file_name = f"{logger_name}_log.log"
        return os.path.join(log_dir_path, log_file_name)

    @staticmethod
    def get_logger_func(logger_name, config):
        if logger_name in TraceLogger._loggers:
            return TraceLogger._loggers[logger_name]

        logger = logging.getLogger(logger_name)
        logger.setLevel(config["logger_level"])

        # 确保过滤器存在
        if not any(isinstance(f, TraceFilter) for f in logger.filters):
            logger.addFilter(TraceFilter())

        # 文件处理器配置（关键保持逻辑）
        log_file_path = TraceLogger.get_log_file_path(logger_name, config)
        if log_file_path:
            # 防止重复添加文件处理器
            if not any(isinstance(h, TimedRotatingFileHandler) for h in logger.handlers):
                file_handler = TimedRotatingFileHandler(
                    log_file_path,
                    when=config["acc_when"],
                    backupCount=config["backupCount"],
                    interval=config["interval"],
                    encoding="utf-8"
                )
                file_handler.suffix = "%Y-%m-%d"  # 日志文件后缀格式
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)

        # 控制台处理器配置（修复点）
        if config["is_console"]:
            # 精准移除控制台处理器（不影响文件处理器）
            import sys
            console_handlers = [
                h for h in logger.handlers
                if isinstance(h, logging.StreamHandler)
                   and h.stream in (sys.stdout, sys.stderr)
            ]
            for h in console_handlers:
                logger.removeHandler(h)

            # 添加新控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(config["console_level"])
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        TraceLogger._loggers[logger_name] = logger
        return logger

def get_module_line(e: any,project_path=None):
    # tb = e.__traceback__
    # # 遍历到最内层的调用栈
    # while tb.tb_next:
    #     tb = tb.tb_next
    #
    # # 获取真正出错的模块名
    # module_name = tb.tb_frame.f_code.co_filename.split("/")[-1].replace(".py", "")
    # # 获取出错行号
    # line_number = tb.tb_lineno
    # # 获取出错方法名
    # method_name = tb.tb_frame.f_code.co_name
    #
    # module_line = "{}.{}".format(module_name, method_name, line_number)
    # return module_line

    # 解析堆栈信息
    relative_path = '-'
    module_path = '-'
    stack_lines = e.strip().split('\n')
    project_root = project_path if  project_path else os.getcwd()  # 假设项目根目录为当前工作目录
    for line in stack_lines:
        if line.startswith('  File'):
            parts = line.split('"')
            if len(parts) > 1:
                file_path = parts[1]
                if file_path.startswith(project_root):
                    relative_path = os.path.relpath(file_path, project_root)
                    module_path = relative_path.replace(os.sep, '.')[:-3]  # 去除 .py 扩展名
                    # 从 parts 中进一步提取方法名
                    function_part = parts[-1].strip()
                    if function_part.startswith(', line'):
                        sub_parts = function_part.split(',')
                        if len(sub_parts) > 2 and sub_parts[2].strip().startswith('in '):
                            function_name = sub_parts[2].strip().split(' ')[-1]
    return f"{module_path}.{function_name}"


def get_process_funcname(app, request):
    moduler_func_line = None
    func_module, func_name, func_line = None, None, None
    try:
        for route in app.routes:
            if route.path.startswith("/docs") or route.path.startswith("/redoc") or route.path.startswith("/openapi.json"):
                continue
            match, matched_path_params = route.matches(request.scope)
            if match:
                methods = set()
                if isinstance(route, APIRoute):
                    methods = route.methods

                if request.method.lower() in [method.lower() for method in methods]:
                #     print(f"匹配到的路由路径: {route.path}")  # 调试信息
                    # func_name = route.endpoint.__name__
                    if request.scope.get('path') == route.path:
                        endpoint = route.endpoint
                        func_name = endpoint.__name__ if hasattr(endpoint, '__name__') else str(endpoint)
                    else:
                        continue
                    try:
                        source_lines, start_line = inspect.getsourcelines(route.endpoint)
                        func_line = start_line
                        module = inspect.getmodule(route.endpoint)
                        if module:
                            full_module_name = module.__name__
                            if '.' in full_module_name:
                                func_module = full_module_name.split('.')[-1]
                            else:
                                func_module = full_module_name
                        else:
                            func_module = "无法获取模块"
                    except (TypeError, OSError) as e:
                        pass
                    break
    except Exception as e:
        pass
    if func_module and func_name and func_line:
        moduler_func_line = "{}.{}".format(func_module, func_name)
    return moduler_func_line,func_module,func_name,func_line


def get_main_tracebak(stack_trace,project_path=None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 定义你的项目路径
    project_path = project_path if project_path else os.getcwd()

    # 分割堆栈跟踪信息为行
    lines = stack_trace.splitlines()

    # 提取主要堆栈内容
    main_stack = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if project_path in line:
            main_stack.append(line)
            if i + 1 < len(lines):
                main_stack.append(lines[i + 1])
            i += 2  # 跳过下一行，因为已经添加了
        else:
            i += 1
    # 打印主要堆栈内容
    main_tracebak = ''.join(main_stack).replace('\t','').replace('\n','') + lines[-1] if len(lines) > 0 else ''
    return main_tracebak

def clean_error_message(error_message):
    # 将换行符替换为空格
    error_message = error_message.replace('\n', ' ')
    # 将制表符替换为空格
    error_message = error_message.replace('\t', ' ')
    # 将两个及以上的连续空格替换为一个空格
    while '  ' in error_message:
        error_message = error_message.replace('  ', ' ')
    return error_message

async def get_params(request):
    # 获取 URL 中的参数
    query_params = dict(request.query_params) if request else {}
    params = {}
    if query_params:
        params['query_params'] = query_params
    content_type = request.headers.get('Content-Type', '')
    if 'multipart/form-data' in content_type:
        # 处理包含文件上传的表单数据
        try:
            form = await asyncio.wait_for(request.form(), timeout=10)
            has_file = False
            filename = '-'
            for field_name, value in form.items():
                if hasattr(field_name, 'filename'):
                    has_file = True
                    filename = value.filename
                    break
            if has_file:
                params['file'] = filename
            else:
                params['form'] = await request.form()
        except asyncio.TimeoutError:
            form = "上传大文件"
            params['form'] = form

    elif 'application/x-www-form-urlencoded' in content_type:
        params['form'] = await request.form()
    elif 'application/json' in content_type:
        body_params = await request.json()
        params['body_params'] = body_params
    else:
        params['others'] = ""
    return params



class Logger:
    __acc_logger = None
    __server_logger = None
    __error_logger = None
    __all_info_logger = None

    def __init__(self, config=None):
        self.default_config = {
            "access": {
                "is_console": True,
                "is_msg": False,
                "is_request": False,
                "is_response": False,
                "logger_level": logging.DEBUG,
                "console_level": logging.INFO,
                "acc_when": "midnight",
                "interval": 1,
                "backupCount": 7,
                "log_dir": "./logs"
            },
            "error": {
                "is_console": True,
                "is_msg": False,
                "is_request": False,
                "is_response": False,
                "logger_level": logging.ERROR,
                "console_level": logging.ERROR,
                "acc_when": "midnight",
                "interval":1,
                "backupCount": 7,
                "log_dir": "./logs"
            },
            "all_info": {
                "is_console": True,
                "is_msg": False,
                "is_request": False,
                "is_response": False,
                "logger_level": logging.INFO,
                "console_level": logging.INFO,
                "acc_when": "midnight",
                "backupCount": 7,
                "interval": 1,
                "log_dir": "./logs"
            },
            "server": {
                "is_console": True,
                "is_msg": False,
                "is_request": False,
                "is_response": False,
                "logger_level": logging.DEBUG,
                "console_level": logging.INFO,
                "acc_when": "midnight",
                "backupCount": 7,
                "interval": 1,
                "log_dir": "./logs"
            }
        }
        if config:
            self.default_config.update(config)

        acc_config = self.default_config["access"]
        server_config = self.default_config["server"]
        error_config = self.default_config["error"]
        info_config = self.default_config["all_info"]

        # 初始化日志记录器并添加 TraceLogFilter
        Logger.__acc_logger = self._get_logger_with_filter("access", acc_config)
        Logger.__server_logger = self._get_logger_with_filter("server", server_config)
        Logger.__error_logger = self._get_logger_with_filter("error", error_config)
        Logger.__all_info_logger = self._get_logger_with_filter("info", info_config)




    def _get_logger_with_filter(self, name, config):
        # 假设 TraceLogger.get_logger_func 返回一个配置好的日志记录器
        logger = TraceLogger.get_logger_func(name, config)

        # 添加 TraceLogFilter 到日志记录器的所有处理器中
        trace_filter = TraceLogFilter()
        for handler in logger.handlers:
            handler.addFilter(trace_filter)

        # 可选：将过滤器直接添加到 Logger 对象
        # logger.addFilter(trace_filter)

        return logger

    @classmethod
    def acc_log(cls, message):
        if cls.__acc_logger:
            cls.__acc_logger.info(message)

    @classmethod
    def service_log(cls, message):
        if cls.__server_logger:
            cls.__server_logger.info(message)

    @classmethod
    def error_log(cls, message):
        if cls.__error_logger:
            cls.__error_logger.error(message,exc_info=True)

    @classmethod
    def info_log(cls, message):
        if cls.__all_info_logger:
            cls.__all_info_logger.info(message)



class LoggerUtil:
    def __init__(self, config=None):
        self.logger = Logger(config)

    @classmethod
    def info_log(self, message):
        Logger.info_log(message)

    @classmethod
    def error_log(self, message):
        Logger.error_log(message)


# 使用示例
if __name__ == "__main__":
    loger = Logger()
    # 记录普通错误信息
    loger.error_log("这是一个错误消息")

    loger.info_log("测试 logger info ")

    # 记录格式化消息
    #LoggerUtil.error_log("用户 {} 操作失败，错误代码：{}", "user123")

    # 模拟一个异常
    try:
        result = 10 / 0
    except Exception as e:
        # 记录异常信息
        iu = "dsfasdf"
        LoggerUtil.error_log(f"发生了一个异常:{e}")