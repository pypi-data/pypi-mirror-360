"""
@Author  ：duomei
@File    ：code_utils.py
@Time    ：2025/3/11 13:48
"""
import inspect
import os
import re
import traceback


def exception_module_func(request,exc,project_folder):
    moduler_func_line = '_'
    route = request.scope.get("route")
    project_root = ""
    main_error = "-"
    method_name = "_"
    line = "-"
    if route:
        endpoint = route.endpoint
        # 获取函数的定义信息
        method_name = endpoint.__name__
        module_file = inspect.getmodule(endpoint).__file__
        _,line = inspect.getsourcelines(endpoint)

        # 获取模块对应的文件路径
        project_root = os.path.dirname(os.path.abspath(module_file))
        relative_path = os.path.relpath(module_file, project_root)
        module_path = relative_path.replace(os.sep, '.')[:-3]  # 去除 .py 扩展名
        moduler_func_line = "{}.{}".format(module_path.replace('...',''), method_name)
    else:
        pass
        # method_name = request.scope.get("endpoint").__name__
        # moduler_func_line = "{}.{}".format(project_folder, method_name)
    if project_root:
        exc_type = type(exc)
        exc_value = exc
        exc_tb = exc.__traceback__
        # 调用 format_exception 函数格式化异常信息
        formatted_exception = traceback.format_exception(exc_type, exc_value, exc_tb)
        # project_path = os.path.dirname(os.path.abspath(project_root))
        # 打印格式化后的异常信息
        main_error = get_main_tracebak(''.join(formatted_exception), project_path=project_root)

    return moduler_func_line,main_error,method_name,project_root,line



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


# 假设的判断是否为标准结构体的函数
def is_standard_structure(response):
    """
    判断结果是否为标准结构体
    :param response: 方法返回的结果
    :return: True 表示是标准结构体，False 表示不是
    """
    # 这里简单假设标准结构体是字典且包含 'status' 和 'business_code' 字段
    if isinstance(response, dict):
        # 假设标准结构体必须包含 'code' 和'message' 键
        if 'code' in response or 'http_code' in response:
            return True
    return False


# 假设的获取 HTTP 状态码的函数
def get_http_status_code(response):
    """
    从结果中获取 HTTP 状态码
    :param response: 方法返回的结果
    :return: HTTP 状态码，如果不存在则返回 None
    """
    return response.get('http_status_code') if isinstance(response, dict) else None


def get_main_traceback(stack_trace):
    # 定义正则表达式模式，匹配最后一个 raise 语句及相关文件行信息
    pattern = r'File "(.*?)", line (\d+), in (.*?)\s+raise (.*)'
    matches = re.findall(pattern, stack_trace)

    if matches:
        # 取最后一个匹配结果
        file_path, line_number, function_name, raise_statement = matches[-1]
        main_error = f'Traceback (most recent call last):\n File\t"{file_path}",\tline{line_number},\tin\t{function_name}\traise\t{raise_statement}'
    else:
        main_error = "-"
    return main_error

