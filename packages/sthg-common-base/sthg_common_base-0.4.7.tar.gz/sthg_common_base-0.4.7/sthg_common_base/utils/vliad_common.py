from build.lib.sthg_common_base import LoggerUtil
from sthg_common_base.response.httpCodeEnum import ResponseEnum
from sthg_common_base.response.response import BaseResponse
from typing import Optional, Any, Union
from datetime import datetime


class ValidCommon:
    """
    字段验证工具类，提供各种字段验证方法
    所有方法返回BaseResponse对象:
    - 验证成功: ResponseEnum.OK
    - 验证失败: ResponseEnum.InvalidArgument
    - 异常错误: ResponseEnum.InternalError
    """

    @staticmethod
    def check_null(
            value: Any,
            field_name: str = "字段",
            base_response: BaseResponse = None
    ) -> BaseResponse:
        """
        检查字段是否为None或空字符串
        :param base_response: 如果已有失败的响应，则直接返回
        """
        # 如果已有失败的响应，直接返回
        if base_response and not base_response.is_success():
            return base_response

        try:
            if value is None:
                resp = BaseResponse(ResponseEnum.InvalidArgument, msg=f"{field_name}不能为空")
                if base_response:
                    base_response.build_reset_by_resp(resp)
                    return base_response
                return resp

            if isinstance(value, str) and value.strip() == "":
                resp = BaseResponse(ResponseEnum.InvalidArgument, msg=f"{field_name}不能为空字符串")
                if base_response:
                    base_response.build_reset_by_resp(resp)
                    return base_response
                return resp

            return BaseResponse(ResponseEnum.OK, data=value)
        except Exception as e:
            LoggerUtil.error_log(f"{field_name}:检查空值异常")
            resp = BaseResponse(
                ResponseEnum.InternalError,
                msg=f"{field_name}:检查空值异常"
            )
            if base_response:
                base_response.build_reset_by_resp(resp)
                return base_response
            return resp

    @staticmethod
    def check_numeric(
            value: Union[str, int, float],
            field_name: str = "字段",
            base_response: BaseResponse = None
    ) -> BaseResponse:
        """
        检查字段是否为数字或可转换为数字
        :param base_response: 如果已有失败的响应，则直接返回
        """
        # 如果已有失败的响应，直接返回
        if base_response and not base_response.is_success():
            return base_response

        try:
            # 如果已经是数字类型
            if isinstance(value, (int, float)):
                return BaseResponse(ResponseEnum.OK, data=value)

            # 尝试转换字符串为数字
            if isinstance(value, str):
                if value.isdigit():
                    return BaseResponse(ResponseEnum.OK, data=int(value))
                try:
                    float_val = float(value)
                    return BaseResponse(ResponseEnum.OK, data=float_val)
                except ValueError:
                    pass

            resp = BaseResponse(ResponseEnum.InvalidArgument, msg=f"{field_name}必须是数字")
            if base_response:
                base_response.build_reset_by_resp(resp)
                return base_response
            return resp
        except Exception as e:
            LoggerUtil.error_log(f"{field_name}:数字检查异常")
            resp = BaseResponse(
                ResponseEnum.InternalError,
                msg=f"{field_name}:数字检查异常"
            )
            if base_response:
                base_response.build_reset_by_resp(resp)
                return base_response
            return resp

    @staticmethod
    def validate_length(
            value: str,
            min_len: Optional[int] = None,
            max_len: Optional[int] = None,
            field_name: str = "字段",
            base_response: BaseResponse = None
    ) -> BaseResponse:
        """
        验证字符串长度范围
        :param base_response: 如果已有失败的响应，则直接返回
        """
        # 如果已有失败的响应，直接返回
        if base_response and not base_response.is_success():
            return base_response

        try:
            # 先检查是否为字符串
            if not isinstance(value, str):
                resp = BaseResponse(ResponseEnum.InvalidArgument, msg=f"{field_name}必须是字符串类型")
                if base_response:
                    base_response.build_reset_by_resp(resp)
                    return base_response
                return resp

            length = len(value)
            error_msg = None

            if min_len is not None and max_len is not None:
                if not (min_len <= length <= max_len):
                    error_msg = f"{field_name}长度需在{min_len}到{max_len}之间"
            elif min_len is not None:
                if length < min_len:
                    error_msg = f"{field_name}长度不能小于{min_len}"
            elif max_len is not None:
                if length > max_len:
                    error_msg = f"{field_name}长度不能超过{max_len}"

            if error_msg:
                resp = BaseResponse(ResponseEnum.InvalidArgument, msg=error_msg)
                if base_response:
                    base_response.build_reset_by_resp(resp)
                    return base_response
                return resp

            return BaseResponse(ResponseEnum.OK, data=value)
        except Exception as e:
            LoggerUtil.error_log(f"{field_name}:长度验证异常")
            resp = BaseResponse(
                ResponseEnum.InternalError,
                msg=f"{field_name}:长度验证异常"
            )
            if base_response:
                base_response.build_reset_by_resp(resp)
                return base_response
            return resp

    @staticmethod
    def validate_date_format(
            value: str,
            date_format: str = "%Y-%m-%d",
            field_name: str = "字段",
            base_response: BaseResponse = None
    ) -> BaseResponse:
        """
        验证日期格式是否符合指定格式
        :param base_response: 如果已有失败的响应，则直接返回
        """
        # 如果已有失败的响应，直接返回
        if base_response and not base_response.is_success():
            return base_response

        try:
            if not isinstance(value, str):
                resp = BaseResponse(ResponseEnum.InvalidArgument, msg=f"{field_name}必须是字符串类型")
                if base_response:
                    base_response.build_reset_by_resp(resp)
                    return base_response
                return resp

            try:
                # 尝试解析日期
                datetime.strptime(value, date_format)
                return BaseResponse(ResponseEnum.OK, data=value)
            except ValueError:
                resp = BaseResponse(
                    ResponseEnum.InvalidArgument,
                    msg=f"{field_name}格式应为{date_format}"
                )
                if base_response:
                    base_response.build_reset_by_resp(resp)
                    return base_response
                return resp
        except Exception as e:
            LoggerUtil.error_log(f"{field_name}:日期格式验证异常")
            resp = BaseResponse(
                ResponseEnum.InternalError,
                msg=f"{field_name}:日期格式验证异常"
            )
            if base_response:
                base_response.build_reset_by_resp(resp)
                return base_response
            return resp

# 使用示例
if __name__ == "__main__":
    # 测试空值检查
    print("空值检查测试:")
    print(ValidCommon.check_null(None).to_dict())  # 应失败
    print(ValidCommon.check_null("").to_dict())  # 应失败
    print(ValidCommon.check_null("valid").to_dict())  # 应成功

    # 测试数字检查
    print("\n数字检查测试:")
    print(ValidCommon.check_numeric("123").to_dict())  # 应成功 (整数)
    print(ValidCommon.check_numeric("123.45").to_dict())  # 应成功 (浮点数)
    print(ValidCommon.check_numeric("abc").to_dict())  # 应失败

    # 测试长度验证
    print("\n长度验证测试:")
    print(ValidCommon.validate_length("test", min_len=3, max_len=5).to_dict())  # 应成功
    print(ValidCommon.validate_length("te", min_len=3).to_dict())  # 应失败
    print(ValidCommon.validate_length("too_long", max_len=5).to_dict())  # 应失败

    # 测试日期格式
    print("\n日期格式测试:")
    print(ValidCommon.validate_date_format("2023-08-15").to_dict())  # 应成功
    print(ValidCommon.validate_date_format("15/08/2023", date_format="%d/%m/%Y").to_dict())  # 应成功
    print(ValidCommon.validate_date_format("2023/08/15").to_dict())  # 应失败 (格式不匹配)