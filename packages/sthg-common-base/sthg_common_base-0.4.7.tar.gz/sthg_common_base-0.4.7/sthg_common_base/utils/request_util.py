"""
@Author  ：duomei
@File    ：request_util.py
@Time    ：2025/4/28 16:07
"""
import json
from contextvars import ContextVar

import requests
from requests.exceptions import ConnectionError, ConnectTimeout, ReadTimeout, TooManyRedirects, URLRequired, InvalidURL, \
    InvalidHeader, InvalidProxyURL
from starlette.datastructures import Headers, MutableHeaders

from sthg_common_base import BaseResponse, ResponseEnum, format_exception_msg, access_log, LoggerUtil
from sthg_common_base.utils.sthg_common_constants import SthgCommonConstants


class RequestUtil:

    @staticmethod
    @access_log()
    def get(url: str, headers=None, params=None, encoding=None, timeout=30):
        """
        同步get
        :param url: 请求的URL
        :param headers: 请求头
        :param timeout: 超时时间，默认为10秒
        :param params: URL参数
        :param encoding: 编码方式
        :return: 解析后的JSON响应
        """
        try:
            new_headers=RequestUtil.builder_headers(headers)
            response = requests.get(url, headers=new_headers, params=params, timeout=timeout)
            if encoding:
                response.encoding = encoding
            text = response.text
            return BaseResponse(data=json.loads(text), resEnum=ResponseEnum.OK, msg=f"请地址url:{url}")
        except ReadTimeout as e:
            return BaseResponse(resEnum=ResponseEnum.RequestTimeout, msg=f"请地址url:{url}",
                                exceptionStack=format_exception_msg(e))
        except TooManyRedirects as e:
            return BaseResponse(resEnum=ResponseEnum.Too_Many_Redirects, msg=f"请地址url:{url}",
                                exceptionStack=format_exception_msg(e))
        except URLRequired as e:
            return BaseResponse(resEnum=ResponseEnum.InvalidRequest, msg=f"请地址url:{url}",
                                exceptionStack=format_exception_msg(e))
        except InvalidURL as e:
            return BaseResponse(resEnum=ResponseEnum.InvalidURI, msg=f"请地址url:{url}",
                                exceptionStack=format_exception_msg(e))
        except InvalidHeader as e:
            return BaseResponse(resEnum=ResponseEnum.Invalid_Header, msg=f"请地址url:{url}",
                                exceptionStack=format_exception_msg(e))
        except InvalidProxyURL as e:
            return BaseResponse(resEnum=ResponseEnum.Invalid_Proxy_URL, msg=f"请地址url:{url}",
                                exceptionStack=format_exception_msg(e))
        except ConnectionError as e:
            return BaseResponse(resEnum=ResponseEnum.ConnectionError, msg=f"请地址url:{url}",
                                exceptionStack=format_exception_msg(e))
        except ConnectTimeout as e:
            return BaseResponse(resEnum=ResponseEnum.ConnectionTimeout, msg=f"请地址url:{url}",
                                exceptionStack=format_exception_msg(e))
        except Exception as e:
            return BaseResponse(resEnum=ResponseEnum.InternalError, msg=f"请地址url:{url}",
                                exceptionStack=format_exception_msg(e))

    @staticmethod
    @access_log()
    def post(url: str, headers=None, json_data=None, encoding=None, timeout=30):
        """
        同步post
        :param url: 请求的URL
        :param headers: 请求头
        :param timeout: 超时时间，默认为10秒
        :param json_data: 要发送的JSON数据
        :param encoding: 编码方式
        :return: 解析后的JSON响应
        """
        try:
            new_headers = RequestUtil.builder_headers(headers)
            result = requests.post(url, headers=new_headers, json=json_data, timeout=timeout)
            if encoding:
                result.encoding = encoding
            text = result.text
            return BaseResponse(data=json.loads(text), resEnum=ResponseEnum.OK, msg=f"请地址url:{url}")
        except ReadTimeout as e:
            return BaseResponse(resEnum=ResponseEnum.RequestTimeout, msg=f"请地址url:{url}",
                                exceptionStack=format_exception_msg(e))
        except TooManyRedirects as e:
            return BaseResponse(resEnum=ResponseEnum.Too_Many_Redirects, msg=f"请地址url:{url}",
                                exceptionStack=format_exception_msg(e))
        except URLRequired as e:
            return BaseResponse(resEnum=ResponseEnum.InvalidRequest, msg=f"请地址url:{url}",
                                exceptionStack=format_exception_msg(e))
        except InvalidURL as e:
            return BaseResponse(resEnum=ResponseEnum.InvalidURI, msg=f"请地址url:{url}",
                                exceptionStack=format_exception_msg(e))
        except InvalidHeader as e:
            return BaseResponse(resEnum=ResponseEnum.Invalid_Header, msg=f"请地址url:{url}",
                                exceptionStack=format_exception_msg(e))
        except InvalidProxyURL as e:
            return BaseResponse(resEnum=ResponseEnum.Invalid_Proxy_URL, msg=f"请地址url:{url}",
                                exceptionStack=format_exception_msg(e))
        except ConnectionError as e:
            return BaseResponse(resEnum=ResponseEnum.ConnectionError, msg=f"请地址url:{url}",
                                exceptionStack=format_exception_msg(e))
        except ConnectTimeout as e:
            return BaseResponse(resEnum=ResponseEnum.ConnectionTimeout, msg=f"请地址url:{url}",
                                exceptionStack=format_exception_msg(e))
        except Exception as e:
            return BaseResponse(resEnum=ResponseEnum.InternalError, msg=f"请地址url:{url}",
                                exceptionStack=format_exception_msg(e))

    @staticmethod
    @access_log()
    def builder_headers(headers=None):

        """
        x-request-id:7d5e4ea0-e2dd-48bb-a8bb-91a9fd99841d-1749629043413
        x-user-id:1904456484926791700
            "x-user-id": "test_user",  # 添加用户ID
            "x-forwarded-for": "127.0.0.1",  # 添加有效的IP地址
            "x-request-id": "test_request_id",
            "x-trace-id": "test_trace_id"
        """
        try:
            # 如果是request.headers
            if isinstance(headers, Headers):
                headers = MutableHeaders(headers)


            request_id: str = headers.get(SthgCommonConstants.header_x_request_id_key)
            if request_id is None or len(request_id) == 0:
                headers[SthgCommonConstants.header_x_request_id_key] = ContextVar(
                    SthgCommonConstants.context_request_id_key, default="").get()

            user_id: str = headers.get(SthgCommonConstants.header_x_user_id_key)
            if user_id is None or len(user_id) == 0:
                user_id = headers.get(SthgCommonConstants.header_user_id_key)
            if user_id is None or len(user_id) == 0:
                headers[SthgCommonConstants.header_x_user_id_key] = ContextVar(SthgCommonConstants.context_user_id_key,
                                                                               default="").get()
                headers[SthgCommonConstants.header_user_id_key] = ContextVar(SthgCommonConstants.context_user_id_key,
                                                                             default="").get()

            trace_id: str = headers.get(SthgCommonConstants.header_x_trace_id_key)
            if trace_id is None or len(trace_id) == 0:
                headers[SthgCommonConstants.header_x_trace_id_key] = ContextVar(SthgCommonConstants.context_trace_id_key,
                                                                                default="").get()

            x_guid: str = headers.get(SthgCommonConstants.header_x_guid_id_key)
            if x_guid is None or len(x_guid) == 0:
                headers[SthgCommonConstants.header_x_guid_id_key] = ContextVar(SthgCommonConstants.context_guid_id_key,
                                                                               default="").get()

            return headers
        except Exception as e:
            LoggerUtil.error_log(f"builder_headers error "+str(e))
            return headers


if __name__ == "__main__":
    # # 测试http_get方法 - 成功案例
    # print("测试http_get - 成功案例:")
    # get_result = RequestUtil.get(
    #     url="https://httpbin.org/get",
    #     params={"test": "value"},
    #     headers={"User-Agent": "TestClient"}
    # )
    # print(f"状态码: {get_result.code}")
    # print(f"业务消息: {get_result.busiMsg}")
    # if get_result.code == ResponseEnum.OK.getHttpCode:
    #     print(f"响应数据: {get_result.data}")
    #     print(f"请求ID: {get_result.requestId}")
    # else:
    #     print(f"错误信息: {get_result.exceptionStack}")
    #
    # # 测试http_get方法 - 超时案例
    # print("\n测试http_get - 超时案例:")
    # timeout_result = RequestUtil.get(
    #     url="https://httpbin.org/delay/5",  # 这个端点会延迟5秒响应
    #     timeout=1  # 设置1秒超时
    # )
    # print(f"状态码: {timeout_result.code}")
    # print(f"业务消息: {timeout_result.busiMsg}")
    # print(f"错误堆栈: {timeout_result.exceptionStack}")
    #
    # 测试http_post方法 - 成功案例
    # print("\n测试http_post - 成功案例:")
    # post_data = {"key": "value", "number": 42}
    # post_result = RequestUtil.post(
    #     url="https://httpbin.org/post",
    #     json_data=post_data,
    #     headers={"Content-Type": "application/json"}
    # )
    # print(f"状态码: {post_result.code}")
    # print(f"业务消息: {post_result.busiMsg}")
    # if post_result.code == ResponseEnum.OK.getHttpCode:
    #     print(f"响应数据: {post_result.data}")
    #     print(f"请求ID: {post_result.requestId}")
    # else:
    #     print(f"错误信息: {post_result.exceptionStack}")
    #
    # # 测试http_post方法 - 错误URL案例
    # print("\n测试http_post - 错误URL案例:")
    # error_result = RequestUtil.post(
    #     url="https://invalid-domain-xyz.example/api",
    #     json_data={"test": "data"}
    # )
    # print(f"状态码: {error_result.code}")
    # print(f"业务消息: {error_result.busiMsg}")
    # print(f"错误堆栈: {error_result.exceptionStack}")
    #
    # # 测试http_post方法 - 无效JSON响应
    # print("\n测试http_post - 无效JSON响应:")
    # invalid_json_result = RequestUtil.post(
    #     url="https://httpbin.org/html",  # 返回HTML内容而不是JSON
    #     headers={"Accept": "application/json"}  # 故意要求JSON
    # )
    # print(f"状态码: {invalid_json_result.code}")
    # print(f"业务消息: {invalid_json_result.busiMsg}")
    # print(f"错误堆栈: {invalid_json_result.exceptionStack}")

    bode: dict = {
        "current_node_id": "63a2d06a-f8d3-4cf3-a65c-20f4b448a019",
        "graph": {
            "edges": [
                {
                    "shape": "edge",
                    "attrs": {
                        "line": {
                            "stroke": "#537FDF",
                            "strokeWidth": 1,
                            "strokeDasharray": 5
                        }
                    },
                    "id": "525a7895-f2b7-4303-822b-80b7bdd13130",
                    "router": {
                        "name": "manhattan"
                    },
                    "connector": {
                        "name": "rounded"
                    },
                    "data": {
                        "source": "a5009321-1d7e-4ff5-831d-638d2c261bbc",
                        "target": "90fde588-881b-4404-93c1-0fc7b31711dc"
                    },
                    "source": "a5009321-1d7e-4ff5-831d-638d2c261bbc",
                    "target": "90fde588-881b-4404-93c1-0fc7b31711dc",
                    "zIndex": 6
                },
                {
                    "shape": "edge",
                    "attrs": {
                        "line": {
                            "stroke": "#537FDF",
                            "strokeWidth": 1,
                            "strokeDasharray": 5
                        }
                    },
                    "id": "ab879292-6122-4943-96fa-93e2e4af7a95",
                    "router": {
                        "name": "manhattan"
                    },
                    "connector": {
                        "name": "rounded"
                    },
                    "data": {
                        "source": "90fde588-881b-4404-93c1-0fc7b31711dc",
                        "target": "f743f047-b8dc-4cf1-a047-c1fae4131357"
                    },
                    "source": "90fde588-881b-4404-93c1-0fc7b31711dc",
                    "target": "f743f047-b8dc-4cf1-a047-c1fae4131357",
                    "zIndex": 7
                },
                {
                    "shape": "edge",
                    "attrs": {
                        "line": {
                            "stroke": "#537FDF",
                            "strokeWidth": 1,
                            "strokeDasharray": 5
                        }
                    },
                    "id": "1bebc19b-12ec-4eb0-88bf-724111325bde",
                    "router": {
                        "name": "manhattan"
                    },
                    "connector": {
                        "name": "rounded"
                    },
                    "data": {
                        "source": "63a2d06a-f8d3-4cf3-a65c-20f4b448a019",
                        "target": "f743f047-b8dc-4cf1-a047-c1fae4131357"
                    },
                    "source": "63a2d06a-f8d3-4cf3-a65c-20f4b448a019",
                    "target": "f743f047-b8dc-4cf1-a047-c1fae4131357",
                    "zIndex": 8
                },
                {
                    "shape": "edge",
                    "attrs": {
                        "line": {
                            "stroke": "#537FDF",
                            "strokeWidth": 1,
                            "strokeDasharray": 5
                        }
                    },
                    "id": "a048f5f1-8a0f-49b8-b582-951c7d2ab46a",
                    "router": {
                        "name": "manhattan"
                    },
                    "connector": {
                        "name": "rounded"
                    },
                    "data": {
                        "source": "f743f047-b8dc-4cf1-a047-c1fae4131357",
                        "target": "5162970b-8786-487b-94d0-66349dfedb92"
                    },
                    "source": "f743f047-b8dc-4cf1-a047-c1fae4131357",
                    "target": "5162970b-8786-487b-94d0-66349dfedb92",
                    "zIndex": 9
                }
            ],
            "nodes": [
                {
                    "position": {
                        "x": 100,
                        "y": 200
                    },
                    "size": {
                        "width": 240,
                        "height": 73
                    },
                    "view": "vue-shape-view",
                    "shape": "data-node",
                    "ports": {
                        "groups": {
                            "right": {
                                "position": "right",
                                "attrs": {
                                    "circle": {
                                        "magnet": True,
                                        "stroke": "#8f8f8f",
                                        "r": 5
                                    }
                                },
                                "label": {
                                    "position": "right"
                                }
                            },
                            "left": {
                                "position": "left",
                                "attrs": {
                                    "circle": {
                                        "magnet": True,
                                        "stroke": "#8f8f8f",
                                        "r": 5
                                    }
                                },
                                "label": {
                                    "position": "left"
                                }
                            }
                        },
                        "items": [
                            {
                                "id": "63a2d06a-f8d3-4cf3-a65c-20f4b448a019-out",
                                "group": "right"
                            }
                        ]
                    },
                    "id": "63a2d06a-f8d3-4cf3-a65c-20f4b448a019",
                    "data": {
                        "key": "dd_zhendi_status",
                        "columns": [
                            {
                                "columnName": "count_zdzb",
                                "columnType": "String",
                                "is_nullable": True,
                                "is_primary_key": False,
                                "is_unique": False,
                                "is_indexed": False,
                                "comment": None,
                                "length": 1024
                            },
                            {
                                "columnName": "name_ddfsj",
                                "columnType": "String",
                                "is_nullable": True,
                                "is_primary_key": False,
                                "is_unique": False,
                                "is_indexed": False,
                                "comment": None
                            },
                            {
                                "columnName": "count_ddfsj",
                                "columnType": "String",
                                "is_nullable": True,
                                "is_primary_key": False,
                                "is_unique": False,
                                "is_indexed": False,
                                "comment": None,
                                "length": 1020
                            },
                            {
                                "columnName": "name_zdzb",
                                "columnType": "String",
                                "is_nullable": True,
                                "is_primary_key": False,
                                "is_unique": False,
                                "is_indexed": False,
                                "comment": None
                            },
                            {
                                "columnName": "action_name",
                                "columnType": "String",
                                "is_nullable": True,
                                "is_primary_key": False,
                                "is_unique": False,
                                "is_indexed": False,
                                "comment": None
                            }
                        ],
                        "row_count": 27,
                        "create_time": "2025-06-10T01:52:34",
                        "update_time": "2025-06-10T01:52:35",
                        "table_size": "0.00 MB",
                        "comment": None,
                        "description": "",
                        "isCheckbox": True,
                        "name": None,
                        "table": "dd_zhendi_status",
                        "data_type": "dataset",
                        "node_type": "INPUT",
                        "showMenu": False
                    },
                    "zIndex": 1
                },
                {
                    "position": {
                        "x": 100,
                        "y": 300
                    },
                    "size": {
                        "width": 240,
                        "height": 73
                    },
                    "view": "vue-shape-view",
                    "shape": "data-node",
                    "ports": {
                        "groups": {
                            "right": {
                                "position": "right",
                                "attrs": {
                                    "circle": {
                                        "magnet": True,
                                        "stroke": "#8f8f8f",
                                        "r": 5
                                    }
                                },
                                "label": {
                                    "position": "right"
                                }
                            },
                            "left": {
                                "position": "left",
                                "attrs": {
                                    "circle": {
                                        "magnet": True,
                                        "stroke": "#8f8f8f",
                                        "r": 5
                                    }
                                },
                                "label": {
                                    "position": "left"
                                }
                            }
                        },
                        "items": [
                            {
                                "id": "a5009321-1d7e-4ff5-831d-638d2c261bbc-out",
                                "group": "right"
                            }
                        ]
                    },
                    "id": "a5009321-1d7e-4ff5-831d-638d2c261bbc",
                    "data": {
                        "key": "xy_refined_result",
                        "columns": [
                            {
                                "columnName": "task_id",
                                "columnType": "String",
                                "is_nullable": True,
                                "is_primary_key": False,
                                "is_unique": False,
                                "is_indexed": False,
                                "comment": None,
                                "length": 128
                            },
                            {
                                "columnName": "target_name",
                                "columnType": "String",
                                "is_nullable": True,
                                "is_primary_key": False,
                                "is_unique": False,
                                "is_indexed": False,
                                "comment": None,
                                "length": 1020
                            },
                            {
                                "columnName": "target_id",
                                "columnType": "String",
                                "is_nullable": True,
                                "is_primary_key": False,
                                "is_unique": False,
                                "is_indexed": False,
                                "comment": None,
                                "length": 1020
                            },
                            {
                                "columnName": "start_time",
                                "columnType": "Timestamp",
                                "is_nullable": True,
                                "is_primary_key": False,
                                "is_unique": False,
                                "is_indexed": False,
                                "comment": None
                            },
                            {
                                "columnName": "satellite",
                                "columnType": "String",
                                "is_nullable": True,
                                "is_primary_key": False,
                                "is_unique": False,
                                "is_indexed": False,
                                "comment": None,
                                "length": 1020
                            },
                            {
                                "columnName": "data_json",
                                "columnType": "String",
                            },
                            {
                                "columnName": "type",
                                "columnType": "Integer",
                            },
                            {
                                "columnName": "target_type",
                                "columnType": "Integer",
                            }
                        ],
                        "row_count": 61,
                        "create_time": "2025-06-07T19:51:11",
                        "update_time": "2025-06-07T22:27:28",
                        "table_size": "0.00 MB"
                    },
                    "zIndex": 2
                },
                {
                    "position": {
                        "x": 450,
                        "y": 300
                    },
                    "size": {
                        "width": 240,
                        "height": 73
                    },
                    "view": "vue-shape-view",
                    "shape": "data-node",
                    "ports": {
                        "groups": {
                            "right": {
                                "position": "right",
                                "attrs": {
                                    "circle": {
                                        "magnet": True,
                                        "stroke": "#8f8f8f",
                                        "r": 5
                                    }
                                },
                                "label": {
                                    "position": "right"
                                }
                            },
                            "left": {
                                "position": "left",
                                "attrs": {
                                    "circle": {
                                        "stroke": "#8f8f8f",
                                        "r": 5
                                    }
                                },
                                "label": {
                                    "position": "left"
                                }
                            }
                        },
                        "items": [
                            {
                                "id": "90fde588-881b-4404-93c1-0fc7b31711dc-input",
                                "group": "left"
                            },
                            {
                                "id": "90fde588-881b-4404-93c1-0fc7b31711dc-out",
                                "group": "right"
                            }
                        ]
                    },
                    "id": "90fde588-881b-4404-93c1-0fc7b31711dc",
                    "data": {
                        "data_type": "transform",
                        "node_type": "TRANSFORM",
                        "key": "转换",
                        "transformer_list": [
                            {
                                "alias": "",
                                "function_name": "JSONParsing",
                                "table_name": "xy_refined_result",
                                "argument_list": [
                                    {
                                        "param_name": "",
                                        "is_field": False,
                                        "value": "[\n    {\n        \"name1\": \"导D发射架\",\n        \"type1\": \"发射架\",\n        \"unit1\": \"6\",\n        \"count1\": 1,\n        \"changecount1\": 1,\n        \"name2\": \"制导装备\",\n        \"type2\": \"\",\n        \"unit2\": \"1\",\n        \"count2\": 1,\n        \"changecount2\": 0\n    },\n{\n        \"name1\": \"导D发射架\",\n        \"type1\": \"发射架\",\n        \"unit1\": \"6\",\n        \"count1\": 2,\n        \"changecount1\": 1,\n        \"name2\": \"制导装备\",\n        \"type2\": \"\",\n        \"unit2\": \"1\",\n        \"count2\": 1,\n        \"changecount2\": 0\n    },{\n        \"name1\": \"导D发射架\",\n        \"type1\": \"发射架\",\n        \"unit1\": \"6\",\n        \"count1\": 3,\n        \"changecount1\": 1,\n        \"name2\": \"制导装备\",\n        \"type2\": \"\",\n        \"unit2\": \"1\",\n        \"count2\": 1,\n        \"changecount2\": 0\n    },{\n        \"name1\": \"导D发射架\",\n        \"type1\": \"发射架\",\n        \"unit1\": \"6\",\n        \"count1\": 4,\n        \"changecount1\": 1,\n        \"name2\": \"制导装备\",\n        \"type2\": \"\",\n        \"unit2\": \"1\",\n        \"count2\": 1,\n        \"changecount2\": 0\n    }\n,{\n        \"name1\": \"导D发射架\",\n        \"type1\": \"发射架\",\n        \"unit1\": \"6\",\n        \"count1\": 1,\n        \"changecount1\": 1,\n        \"name2\": \"制导装备\",\n        \"type2\": \"\",\n        \"unit2\": \"1\",\n        \"count2\": 1,\n        \"changecount2\": 0\n    }\n]"
                                    },
                                    {
                                        "param_name": "",
                                        "is_field": False,
                                        "value": "[{\"name\":\"name1\",\"types\":\"String\"},{\"name\":\"type1\",\"types\":\"String\"},{\"name\":\"unit1\",\"types\":\"String\"},{\"name\":\"count1\",\"types\":\"String\"},{\"name\":\"changecount1\",\"types\":\"String\"},{\"name\":\"name2\",\"types\":\"String\"},{\"name\":\"type2\",\"types\":\"String\"},{\"name\":\"unit2\",\"types\":\"String\"},{\"name\":\"count2\",\"types\":\"String\"},{\"name\":\"changecount2\",\"types\":\"String\"}]"
                                    }
                                ]
                            }
                        ],
                        "allForData": [
                            {
                                "title": "JSONParsing",
                                "sharedData": {
                                    "rid": "ri.ontology.main.transform_operator.29e92254-3818-479b-a4af-da7d021e1b60",
                                    "create_uid": "123",
                                    "ctime": "2025-05-27T12:09:34",
                                    "utime": "2025-05-27T12:09:34",
                                    "name": "json解析",
                                    "en_name": "JSONParsing",
                                    "type": "数据准备",
                                    "description": "对 JSON 格式的数据进行解析",
                                    "input_params": {},
                                    "output_params": {},
                                    "user_params": {},
                                    "icon": {},
                                    "tableName": "xy_refined_result",
                                    "selectedTags": [
                                        {
                                            "label": "task_id",
                                            "value": "task_id",
                                            "typeName": "STRING"
                                        },
                                        {
                                            "label": "target_name",
                                            "value": "target_name",
                                            "typeName": "STRING"
                                        },
                                        {
                                            "label": "target_id",
                                            "value": "target_id",
                                            "typeName": "STRING"
                                        },
                                        {
                                            "label": "start_time",
                                            "value": "start_time",
                                            "typeName": "TIMESTAMP(3)"
                                        },
                                        {
                                            "label": "satellite",
                                            "value": "satellite",
                                            "typeName": "STRING"
                                        },
                                        {
                                            "label": "data_json",
                                            "value": "data_json",
                                            "typeName": "STRING"
                                        },
                                        {
                                            "label": "type",
                                            "value": "type",
                                            "typeName": "INT"
                                        },
                                        {
                                            "label": "target_type",
                                            "value": "target_type",
                                            "typeName": "INT"
                                        }
                                    ],
                                    "treeObj": [
                                        {
                                            "rid": "ri.ontology.main.transform_operator.b1d7478a-dd6f-4339-97b3-8f09b61004ba",
                                            "create_uid": "123",
                                            "ctime": "2025-05-27T12:09:17",
                                            "utime": "2025-05-27T12:09:17",
                                            "name": "数值乘",
                                            "en_name": "NumericMultiplication",
                                            "type": "数值",
                                            "description": "两个数相乘",
                                            "example": [
                                                {
                                                    "key": "参数",
                                                    "children": [
                                                        {
                                                            "heading": "左",
                                                            "title": "乘数"
                                                        },
                                                        {
                                                            "heading": "右",
                                                            "title": "被乘数"
                                                        }
                                                    ]
                                                }
                                            ],
                                            "input_params": {},
                                            "output_params": {},
                                            "user_params": {},
                                            "icon": {}
                                        },
                                        {
                                            "rid": "ri.ontology.main.transform_operator.c1f2d0b8-c756-4df4-9d9c-6c72d44c029e",
                                            "create_uid": "123",
                                            "ctime": "2025-05-27T12:09:13",
                                            "utime": "2025-05-27T12:09:13",
                                            "name": "数值加",
                                            "en_name": "NumericAddition",
                                            "type": "数值",
                                            "description": "两个数相加",
                                            "example": [
                                                {
                                                    "key": "参数",
                                                    "children": [
                                                        {
                                                            "heading": "左",
                                                            "title": "加数"
                                                        },
                                                        {
                                                            "heading": "右",
                                                            "title": "被加数"
                                                        }
                                                    ]
                                                }
                                            ],
                                            "input_params": {},
                                            "output_params": {},
                                            "user_params": {},
                                            "icon": {}
                                        },
                                        {
                                            "rid": "ri.ontology.main.transform_operator.52e45029-ca58-436a-883d-7e02ff4367a9",
                                            "create_uid": "123",
                                            "ctime": "2025-05-27T12:09:19",
                                            "utime": "2025-05-27T12:09:19",
                                            "name": "数值除",
                                            "en_name": "NumericDivision",
                                            "type": "数值",
                                            "description": "两个数相除",
                                            "example": [
                                                {
                                                    "key": "参数",
                                                    "children": [
                                                        {
                                                            "heading": "左",
                                                            "title": "除数"
                                                        },
                                                        {
                                                            "heading": "右",
                                                            "title": "被除数"
                                                        }
                                                    ]
                                                }
                                            ],
                                            "input_params": {},
                                            "output_params": {},
                                            "user_params": {},
                                            "icon": {}
                                        },
                                        {
                                            "rid": "ri.ontology.main.transform_operator.4e075471-0cae-4689-b1f5-509631741a36",
                                            "create_uid": "123",
                                            "ctime": "2025-05-27T12:09:15",
                                            "utime": "2025-05-27T12:09:15",
                                            "name": "数值减",
                                            "en_name": "NumericSubtraction",
                                            "type": "数值",
                                            "description": "两个数相减",
                                            "example": [
                                                {
                                                    "key": "参数",
                                                    "children": [
                                                        {
                                                            "heading": "左",
                                                            "title": "减数"
                                                        },
                                                        {
                                                            "heading": "右",
                                                            "title": "被减数"
                                                        }
                                                    ]
                                                }
                                            ],
                                            "input_params": {},
                                            "output_params": {},
                                            "user_params": {},
                                            "icon": {}
                                        },
                                        {
                                            "rid": "ri.ontology.main.transform_operator.6483c19e-2f48-4143-9f74-c04519f2c69e",
                                            "create_uid": "123",
                                            "ctime": "2025-05-27T12:09:21",
                                            "utime": "2025-05-27T12:09:21",
                                            "name": "连接字符串",
                                            "en_name": "ConcatenateStrings",
                                            "type": "字符串",
                                            "description": "将一个字符串列表与指定的连接符连接起来",
                                            "example": [
                                                {
                                                    "key": "参数",
                                                    "children": [
                                                        {
                                                            "heading": "连接符",
                                                            "title": "字符串中间的连接符"
                                                        },
                                                        {
                                                            "heading": "字符串列表",
                                                            "title": "需要连接的字符串列表"
                                                        }
                                                    ]
                                                }
                                            ],
                                            "input_params": {},
                                            "output_params": {},
                                            "user_params": {},
                                            "icon": {}
                                        },
                                        {
                                            "rid": "ri.ontology.main.transform_operator.40a600ad-ea33-4110-afca-d3f87c55d179",
                                            "create_uid": "123",
                                            "ctime": "2025-05-27T12:09:23",
                                            "utime": "2025-05-27T12:09:23",
                                            "name": "哈希sha256",
                                            "en_name": "HashSHA256",
                                            "type": "字符串",
                                            "description": "对字符串进行 SHA256 哈希运算",
                                            "example": None,
                                            "input_params": {},
                                            "output_params": {},
                                            "user_params": {},
                                            "icon": {}
                                        },
                                        {
                                            "rid": "ri.ontology.main.transform_operator.0ddd3f59-177e-4d00-95f6-fa56cf0fe4b0",
                                            "create_uid": "123",
                                            "ctime": "2025-05-27T12:09:10",
                                            "utime": "2025-05-27T12:09:10",
                                            "name": "选择列",
                                            "en_name": "SelectColumn",
                                            "type": "常用",
                                            "description": "从输入数据集选择指定列",
                                            "example": [
                                                {
                                                    "key": "参数",
                                                    "children": [
                                                        {
                                                            "heading": "要选择的列",
                                                            "title": "要选择的列的列表"
                                                        }
                                                    ]
                                                }
                                            ],
                                            "input_params": {},
                                            "output_params": {},
                                            "user_params": {},
                                            "icon": {}
                                        },
                                        {
                                            "rid": "ri.ontology.main.transform_operator.f1e7292f-8237-4acd-ba26-d1a3079b5b66",
                                            "create_uid": "123",
                                            "ctime": "2025-05-27T12:09:08",
                                            "utime": "2025-05-27T12:09:08",
                                            "name": "删除列",
                                            "en_name": "DeleteColumn",
                                            "type": "常用",
                                            "description": "删除指定列，转换输入数据集",
                                            "example": [
                                                {
                                                    "key": "参数",
                                                    "children": [
                                                        {
                                                            "heading": "要删除的列",
                                                            "title": "要删除的列的列表"
                                                        }
                                                    ]
                                                }
                                            ],
                                            "input_params": {},
                                            "output_params": {},
                                            "user_params": {},
                                            "icon": {}
                                        },
                                        {
                                            "rid": "ri.ontology.main.transform_operator.8122d450-ffac-4cb0-b81d-45a9bf6f1f72",
                                            "create_uid": "123",
                                            "ctime": "2025-05-27T12:09:06",
                                            "utime": "2025-05-27T12:09:06",
                                            "name": "cast函数转换",
                                            "en_name": "CastFunctionConversion",
                                            "type": "转换",
                                            "description": "将值、列或表达式转换成另一种类型，包含日期时间转换以及反之转换",
                                            "example": [
                                                {
                                                    "key": "参数",
                                                    "children": [
                                                        {
                                                            "heading": "表达式",
                                                            "title": "转换表达式"
                                                        },
                                                        {
                                                            "heading": "类型",
                                                            "title": "需要转换成的类型"
                                                        }
                                                    ]
                                                }
                                            ],
                                            "input_params": {},
                                            "output_params": {},
                                            "user_params": {},
                                            "icon": {}
                                        },
                                        {
                                            "rid": "ri.ontology.main.transform_operator.0a3abf4c-9de6-4f0d-a788-cf187073d28b",
                                            "create_uid": "123",
                                            "ctime": "2025-05-27T12:09:30",
                                            "utime": "2025-05-27T12:09:30",
                                            "name": "Ontology GeoPoint转GeoPoint",
                                            "en_name": "OntologyGeoPointToGeoPoint",
                                            "type": "地理空间",
                                            "description": "将一个Ontology GeoPoint转换为一个常规GeoPoint。Ontology GeoPoint是格式为\"{lat},{lon}\"的字符串，其中-90 <= lat <= 90 且 -180 <= lon <= 180。常规GeoPoint是格式为{\"longitude\": {long},\"latitude\": {lat}}的结构。",
                                            "example": [
                                                {
                                                    "key": "参数",
                                                    "children": [
                                                        {
                                                            "heading": "表达式",
                                                            "title": "要转换的 Ontology GeoPoint"
                                                        }
                                                    ]
                                                }
                                            ],
                                            "input_params": {},
                                            "output_params": {},
                                            "user_params": {},
                                            "icon": {}
                                        },
                                        {
                                            "rid": "ri.ontology.main.transform_operator.2b700568-102e-404c-b814-934887357670",
                                            "create_uid": "123",
                                            "ctime": "2025-05-27T12:09:28",
                                            "utime": "2025-05-27T12:09:28",
                                            "name": "获取H3索引",
                                            "en_name": "GetH3Index",
                                            "type": "地理空间",
                                            "description": "将GeoPoint转换为给定分辨率的H3索引。对于分辨率<0或>15返回null。",
                                            "example": [
                                                {
                                                    "key": "参数",
                                                    "children": [
                                                        {
                                                            "heading": "GeoPoint",
                                                            "title": "要转换为 H3 索引的 GeoPoint (lon,lat)"
                                                        },
                                                        {
                                                            "heading": "Resolution",
                                                            "title": "H3 网格分辨率，范围在 0 到 15 之间（包括 0 和 15）"
                                                        }
                                                    ]
                                                }
                                            ],
                                            "input_params": {},
                                            "output_params": {},
                                            "user_params": {},
                                            "icon": {}
                                        },
                                        {
                                            "rid": "ri.ontology.main.transform_operator.81088269-9e4c-4fbd-b674-55159a11323b",
                                            "create_uid": "123",
                                            "ctime": "2025-05-27T12:09:25",
                                            "utime": "2025-05-27T12:09:25",
                                            "name": "构建Geopoint列",
                                            "en_name": "BuildGeopointColumn",
                                            "type": "地理空间",
                                            "description": "从纬度和经度列构建 GeoPoint 列。验证纬度参数是否在-90和90之间（包括边界），以及经度参数是否在-180和180之间（包括边界）；如果不在范围内，则返回空值。",
                                            "example": [
                                                {
                                                    "key": "表达式类别",
                                                    "children": [
                                                        {
                                                            "heading": "类别",
                                                            "title": "地理空间"
                                                        }
                                                    ]
                                                },
                                                {
                                                    "key": "声明的参数",
                                                    "children": [
                                                        {
                                                            "heading": "纬度",
                                                            "title": "纬度列"
                                                        },
                                                        {
                                                            "heading": "经度",
                                                            "title": "经度列"
                                                        }
                                                    ]
                                                }
                                            ],
                                            "input_params": {},
                                            "output_params": {},
                                            "user_params": {},
                                            "icon": {}
                                        },
                                        {
                                            "rid": "ri.ontology.main.transform_operator.d6c46310-74c6-403c-93db-02569fa5b2e1",
                                            "create_uid": "123",
                                            "ctime": "2025-05-27T12:09:32",
                                            "utime": "2025-05-27T12:09:32",
                                            "name": "GeoPoint转Ontology GeoPoint",
                                            "en_name": "GeoPointToOntologyGeoPoint",
                                            "type": "地理空间",
                                            "description": "将 GeoPoint 转换为字符串，以便 Ontology 接受地理索引列（地理哈希类型列）。Ontology GeoPoint 是格式为 '{lat},{lon}' 的字符串，其中 -90 <= lat <= 90 且 -180 <= lon <= 180。",
                                            "example": [
                                                {
                                                    "key": "参数",
                                                    "children": [
                                                        {
                                                            "heading": "表达式",
                                                            "title": "要转换的 Ontology GeoPoint"
                                                        }
                                                    ]
                                                }
                                            ],
                                            "input_params": {},
                                            "output_params": {},
                                            "user_params": {},
                                            "icon": {}
                                        }
                                    ]
                                },
                                "allList": {
                                    "expression": "json解析",
                                    "textarea": "[\n    {\n        \"name1\": \"导D发射架\",\n        \"type1\": \"发射架\",\n        \"unit1\": \"6\",\n        \"count1\": 1,\n        \"changecount1\": 1,\n        \"name2\": \"制导装备\",\n        \"type2\": \"\",\n        \"unit2\": \"1\",\n        \"count2\": 1,\n        \"changecount2\": 0\n    },\n{\n        \"name1\": \"导D发射架\",\n        \"type1\": \"发射架\",\n        \"unit1\": \"6\",\n        \"count1\": 2,\n        \"changecount1\": 1,\n        \"name2\": \"制导装备\",\n        \"type2\": \"\",\n        \"unit2\": \"1\",\n        \"count2\": 1,\n        \"changecount2\": 0\n    },{\n        \"name1\": \"导D发射架\",\n        \"type1\": \"发射架\",\n        \"unit1\": \"6\",\n        \"count1\": 3,\n        \"changecount1\": 1,\n        \"name2\": \"制导装备\",\n        \"type2\": \"\",\n        \"unit2\": \"1\",\n        \"count2\": 1,\n        \"changecount2\": 0\n    },{\n        \"name1\": \"导D发射架\",\n        \"type1\": \"发射架\",\n        \"unit1\": \"6\",\n        \"count1\": 4,\n        \"changecount1\": 1,\n        \"name2\": \"制导装备\",\n        \"type2\": \"\",\n        \"unit2\": \"1\",\n        \"count2\": 1,\n        \"changecount2\": 0\n    }\n,{\n        \"name1\": \"导D发射架\",\n        \"type1\": \"发射架\",\n        \"unit1\": \"6\",\n        \"count1\": 1,\n        \"changecount1\": 1,\n        \"name2\": \"制导装备\",\n        \"type2\": \"\",\n        \"unit2\": \"1\",\n        \"count2\": 1,\n        \"changecount2\": 0\n    }\n]",
                                    "Json": "[\n    {\n        \"name1\": \"导D发射架\",\n        \"type1\": \"发射架\",\n        \"unit1\": \"6\",\n        \"count1\": 1,\n        \"changecount1\": 1,\n        \"name2\": \"制导装备\",\n        \"type2\": \"\",\n        \"unit2\": \"1\",\n        \"count2\": 1,\n        \"changecount2\": 0\n    },\n{\n        \"name1\": \"导D发射架\",\n        \"type1\": \"发射架\",\n        \"unit1\": \"6\",\n        \"count1\": 2,\n        \"changecount1\": 1,\n        \"name2\": \"制导装备\",\n        \"type2\": \"\",\n        \"unit2\": \"1\",\n        \"count2\": 1,\n        \"changecount2\": 0\n    },{\n        \"name1\": \"导D发射架\",\n        \"type1\": \"发射架\",\n        \"unit1\": \"6\",\n        \"count1\": 3,\n        \"changecount1\": 1,\n        \"name2\": \"制导装备\",\n        \"type2\": \"\",\n        \"unit2\": \"1\",\n        \"count2\": 1,\n        \"changecount2\": 0\n    },{\n        \"name1\": \"导D发射架\",\n        \"type1\": \"发射架\",\n        \"unit1\": \"6\",\n        \"count1\": 4,\n        \"changecount1\": 1,\n        \"name2\": \"制导装备\",\n        \"type2\": \"\",\n        \"unit2\": \"1\",\n        \"count2\": 1,\n        \"changecount2\": 0\n    }\n,{\n        \"name1\": \"导D发射架\",\n        \"type1\": \"发射架\",\n        \"unit1\": \"6\",\n        \"count1\": 1,\n        \"changecount1\": 1,\n        \"name2\": \"制导装备\",\n        \"type2\": \"\",\n        \"unit2\": \"1\",\n        \"count2\": 1,\n        \"changecount2\": 0\n    }\n]",
                                    "Schema": "struct",
                                    "dataSet": [
                                        {
                                            "name": "name1",
                                            "types": "String"
                                        },
                                        {
                                            "name": "type1",
                                            "types": "String"
                                        },
                                        {
                                            "name": "unit1",
                                            "types": "String"
                                        },
                                        {
                                            "name": "count1",
                                            "types": "String"
                                        },
                                        {
                                            "name": "changecount1",
                                            "types": "String"
                                        },
                                        {
                                            "name": "name2",
                                            "types": "String"
                                        },
                                        {
                                            "name": "type2",
                                            "types": "String"
                                        },
                                        {
                                            "name": "unit2",
                                            "types": "String"
                                        },
                                        {
                                            "name": "count2",
                                            "types": "String"
                                        },
                                        {
                                            "name": "changecount2",
                                            "types": "String"
                                        }
                                    ]
                                },
                                "newsCol": "",
                                "dataForName": "xy_refined_result"
                            },
                            {
                                "title": "Transform",
                                "sharedData": {},
                                "allList": [],
                                "newsCol": "",
                                "dataForName": "xy_refined_result"
                            }
                        ],
                        "columns": [
                            {
                                "columnName": "task_id",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "target_name",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "target_id",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "start_time",
                                "columnType": "TIMESTAMP(3)",
                                "objectType": "Object"
                            },
                            {
                                "columnName": "satellite",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "data_json",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "type",
                                "columnType": "INT",
                                "objectType": "Integer"
                            },
                            {
                                "columnName": "target_type",
                                "columnType": "INT",
                                "objectType": "Integer"
                            },
                            {
                                "columnName": "name1",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "type1",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "unit1",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "count1",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "changecount1",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "name2",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "type2",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "unit2",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "count2",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "changecount2",
                                "columnType": "STRING",
                                "objectType": "String"
                            }
                        ],
                        "rowCount": 18,
                        "left_node": "a5009321-1d7e-4ff5-831d-638d2c261bbc",
                        "showMenu": False
                    },
                    "zIndex": 3
                },
                {
                    "position": {
                        "x": 800,
                        "y": 300
                    },
                    "size": {
                        "width": 240,
                        "height": 73
                    },
                    "view": "vue-shape-view",
                    "shape": "data-node",
                    "ports": {
                        "groups": {
                            "right": {
                                "position": "right",
                                "attrs": {
                                    "circle": {
                                        "magnet": True,
                                        "stroke": "#8f8f8f",
                                        "r": 5
                                    }
                                },
                                "label": {
                                    "position": "right"
                                }
                            },
                            "left": {
                                "position": "left",
                                "attrs": {
                                    "circle": {
                                        "magnet": True,
                                        "stroke": "#8f8f8f",
                                        "r": 5
                                    }
                                },
                                "label": {
                                    "position": "left"
                                }
                            }
                        },
                        "items": [
                            {
                                "id": "f743f047-b8dc-4cf1-a047-c1fae4131357-input",
                                "group": "left"
                            },
                            {
                                "id": "f743f047-b8dc-4cf1-a047-c1fae4131357-out",
                                "group": "right"
                            }
                        ]
                    },
                    "id": "f743f047-b8dc-4cf1-a047-c1fae4131357",
                    "data": {
                        "key": "连接",
                        "node_type": "JOIN",
                        "joinType": "inner",
                        "match_condition": [
                            {
                                "source_table": "",
                                "source_id": "90fde588-881b-4404-93c1-0fc7b31711dc",
                                "source_column": "name1",
                                "target_table": "dd_zhendi_status",
                                "target_id": "",
                                "target_column": "name_ddfsj"
                            },
                            {
                                "source_table": "",
                                "source_id": "90fde588-881b-4404-93c1-0fc7b31711dc",
                                "source_column": "count1",
                                "target_table": "dd_zhendi_status",
                                "target_id": "",
                                "target_column": "count_ddfsj"
                            },
                            {
                                "source_table": "",
                                "source_id": "90fde588-881b-4404-93c1-0fc7b31711dc",
                                "source_column": "name2",
                                "target_table": "dd_zhendi_status",
                                "target_id": "",
                                "target_column": "name_zdzb"
                            },
                            {
                                "source_table": "",
                                "source_id": "90fde588-881b-4404-93c1-0fc7b31711dc",
                                "source_column": "count2",
                                "target_table": "dd_zhendi_status",
                                "target_id": "",
                                "target_column": "count_zdzb"
                            }
                        ],
                        "select_source_column": [],
                        "select_target_column": [],
                        "left_table": "转换",
                        "right_table": "dd_zhendi_status",
                        "leftNodeId": "90fde588-881b-4404-93c1-0fc7b31711dc",
                        "rightNodeId": "63a2d06a-f8d3-4cf3-a65c-20f4b448a019",
                        "prefix": "",
                        "hiddenAdvanced": False,
                        "data_type": "join",
                        "columns": [
                            {
                                "columnName": "task_id",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "target_name",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "target_id",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "start_time",
                                "columnType": "TIMESTAMP(3)",
                                "objectType": "Object"
                            },
                            {
                                "columnName": "satellite",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "data_json",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "type",
                                "columnType": "INT",
                                "objectType": "Integer"
                            },
                            {
                                "columnName": "target_type",
                                "columnType": "INT",
                                "objectType": "Integer"
                            },
                            {
                                "columnName": "name1",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "type1",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "unit1",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "count1",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "changecount1",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "name2",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "type2",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "unit2",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "count2",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "changecount2",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "count_zdzb",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "name_ddfsj",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "count_ddfsj",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "name_zdzb",
                                "columnType": "STRING",
                                "objectType": "String"
                            },
                            {
                                "columnName": "action_name",
                                "columnType": "STRING",
                                "objectType": "String"
                            }
                        ],
                        "rowCount": 23,
                        "showMenu": False
                    },
                    "zIndex": 4
                },
                {
                    "position": {
                        "x": 1150,
                        "y": 300
                    },
                    "size": {
                        "width": 240,
                        "height": 73
                    },
                    "view": "vue-shape-view",
                    "shape": "data-node",
                    "ports": {
                        "groups": {
                            "right": {
                                "position": "right",
                                "attrs": {
                                    "circle": {
                                        "magnet": True,
                                        "stroke": "#8f8f8f",
                                        "r": 5
                                    }
                                },
                                "label": {
                                    "position": "right"
                                }
                            },
                            "left": {
                                "position": "left",
                                "attrs": {
                                    "circle": {
                                        "magnet": True,
                                        "stroke": "#8f8f8f",
                                        "r": 5
                                    }
                                },
                                "label": {
                                    "position": "left"
                                }
                            }
                        },
                        "items": [
                            {
                                "id": "5162970b-8786-487b-94d0-66349dfedb92-input",
                                "group": "left"
                            }
                        ]
                    },
                    "id": "5162970b-8786-487b-94d0-66349dfedb92",
                    "data": {
                        "key": "Xy_0610_02",
                        "data_type": "output",
                        "pipeline_data_type": "dataset",
                        "table": "Xy_0610_02",
                        "output_name": "Xy_0610_02",
                        "columns": [
                            {
                                "columnName": "task_id",
                                "columnType": "STRING",
                                "objectType": "String",
                                "field_name": "task_id",
                                "field_type": "STRING"
                            },
                            {
                                "columnName": "target_name",
                                "columnType": "STRING",
                                "objectType": "String",
                                "field_name": "target_name",
                                "field_type": "STRING"
                            },
                            {
                                "columnName": "target_id",
                                "columnType": "STRING",
                                "objectType": "String",
                                "field_name": "target_id",
                                "field_type": "STRING"
                            },
                            {
                                "columnName": "start_time",
                                "columnType": "TIMESTAMP(3)",
                                "objectType": "Object",
                                "field_name": "start_time",
                                "field_type": "TIMESTAMP(3)"
                            },
                            {
                                "columnName": "satellite",
                                "columnType": "STRING",
                                "objectType": "String",
                                "field_name": "satellite",
                                "field_type": "STRING"
                            },
                            {
                                "columnName": "data_json",
                                "columnType": "STRING",
                                "objectType": "String",
                                "field_name": "data_json",
                                "field_type": "STRING"
                            },
                            {
                                "columnName": "type",
                                "columnType": "INT",
                                "objectType": "Integer",
                                "field_name": "type",
                                "field_type": "INT"
                            },
                            {
                                "columnName": "target_type",
                                "columnType": "INT",
                                "objectType": "Integer",
                                "field_name": "target_type",
                                "field_type": "INT"
                            },
                            {
                                "columnName": "name1",
                                "columnType": "STRING",
                                "objectType": "String",
                                "field_name": "name1",
                                "field_type": "STRING"
                            },
                            {
                                "columnName": "type1",
                                "columnType": "STRING",
                                "objectType": "String",
                                "field_name": "type1",
                                "field_type": "STRING"
                            },
                            {
                                "columnName": "unit1",
                                "columnType": "STRING",
                                "objectType": "String",
                                "field_name": "unit1",
                                "field_type": "STRING"
                            },
                            {
                                "columnName": "count1",
                                "columnType": "STRING",
                                "objectType": "String",
                                "field_name": "count1",
                                "field_type": "STRING"
                            },
                            {
                                "columnName": "changecount1",
                                "columnType": "STRING",
                                "objectType": "String",
                                "field_name": "changecount1",
                                "field_type": "STRING"
                            },
                            {
                                "columnName": "name2",
                                "columnType": "STRING",
                                "objectType": "String",
                                "field_name": "name2",
                                "field_type": "STRING"
                            },
                            {
                                "columnName": "type2",
                                "columnType": "STRING",
                                "objectType": "String",
                                "field_name": "type2",
                                "field_type": "STRING"
                            },
                            {
                                "columnName": "unit2",
                                "columnType": "STRING",
                                "objectType": "String",
                                "field_name": "unit2",
                                "field_type": "STRING"
                            },
                            {
                                "columnName": "count2",
                                "columnType": "STRING",
                                "objectType": "String",
                                "field_name": "count2",
                                "field_type": "STRING"
                            },
                            {
                                "columnName": "changecount2",
                                "columnType": "STRING",
                                "objectType": "String",
                                "field_name": "changecount2",
                                "field_type": "STRING"
                            },
                            {
                                "columnName": "count_zdzb",
                                "columnType": "STRING",
                                "objectType": "String",
                                "field_name": "count_zdzb",
                                "field_type": "STRING"
                            },
                            {
                                "columnName": "name_ddfsj",
                                "columnType": "STRING",
                                "objectType": "String",
                                "field_name": "name_ddfsj",
                                "field_type": "STRING"
                            },
                            {
                                "columnName": "count_ddfsj",
                                "columnType": "STRING",
                                "objectType": "String",
                                "field_name": "count_ddfsj",
                                "field_type": "STRING"
                            },
                            {
                                "columnName": "name_zdzb",
                                "columnType": "STRING",
                                "objectType": "String",
                                "field_name": "name_zdzb",
                                "field_type": "STRING"
                            },
                            {
                                "columnName": "action_name",
                                "columnType": "STRING",
                                "objectType": "String",
                                "field_name": "action_name",
                                "field_type": "STRING"
                            }
                        ],
                        "left_node": "f743f047-b8dc-4cf1-a047-c1fae4131357",
                        "node_type": "OUTPUT"
                    },
                    "zIndex": 5
                }
            ]
        }
    }
    # 测试http trace_id、user_id 透传 - 成功案例
    print("测试xtrace_id_result - 成功案例:")

    headers = {"User-Agent": "TestClient", "x-trace-id": "x-trace-id-11111111111111",
               'Content-Type': 'application/json',
               "x-user-id": "x-user-id-222222222222222", "x-request-id": "x-request-id-zzzzzzzzzzzzzzzzzzzzzzzzzzzz"}
    xtrace_id_result = RequestUtil.post(
        url="http://192.168.1.245:31045/api/pipelines/v1/pipelines/currentNode/data",
        json_data=bode,
        headers=headers
    )
    # 查看实际发送的请求头

    print(f"状态码: {xtrace_id_result.code}")
    print(f"业务消息: {xtrace_id_result.busiMsg}")
    print(f"错误堆栈: {xtrace_id_result.exceptionStack}")

    # 测试http trace_id、user_id 透传 - 成功案例
    print("测试xtrace_id_result - 失败案例:")
    bode["current_node_id"] = ""
    xtrace_id_result = RequestUtil.post(
        url="http://192.168.1.245:31045/api/pipelines/v1/pipelines/currentNode/data",
        json_data=bode,
        headers=headers
    )

    print(f"状态码: {xtrace_id_result.code}")
    print(f"业务消息: {xtrace_id_result.busiMsg}")
    print(f"错误堆栈: {xtrace_id_result.exceptionStack}")
