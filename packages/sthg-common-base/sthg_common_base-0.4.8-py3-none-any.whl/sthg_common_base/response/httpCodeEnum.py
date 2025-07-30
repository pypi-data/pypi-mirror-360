import re

class HttpStatus():
    """HTTP 状态码枚举"""
    CONTINUE = 100
    SWITCHING_PROTOCOLS = 101
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    Range = 206

    # 重定向状态码
    MOVED_PERMANENTLY = 301
    FOUND = 302
    NOT_MODIFIED = 304

    # 客户端错误状态码
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    PAYLOAD_TOO_LARGE = 413
    TOO_MANY_REQUESTS = 429
    UNAVAILABLE_FOR_LEGAL_REASONS = 451

    # 服务器错误状态码
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    CONNECTION_TIMEOUT = 504
    READ_TIMEOUT = 504

def validate_busi_code(busi_code):
    """
    校验 busiCode 是否符合以下格式之一：
    - DDL_Query_Error
    - DDLQueryError
    - File_Is_NotExist
    要求：
    - 首字母必须大写
    - 单词之间可以用下划线连接，也可以直接驼峰连接
    - 下划线两边必须是大写字母开头的单词
    """
    # 正则：允许多组 (可选下划线 + 大写字母开头+小写字母/数字)
    pattern = re.compile(r"^([A-Z][a-z0-9]*)(_?[A-Z][a-z0-9]*)*$")

    if not pattern.fullmatch(busi_code):
        raise ValueError(
            f"busiCode '{busi_code}' 格式非法，必须符合 Bucket_Not_Exist, BucketNotExist, File_Is_NotExist, DDL_Query_Error 这样的格式。"
        )

class ResCode:
    """
    TempClass represents a structured response entry with:
    - business code (busiCode)
    - business message (busiMsg)
    - HTTP status code (httpCode)
    """
    def __init__(self, busiCode, busiMsg, httpCode):
        # Validate busiCode format using regex
        if not re.match(r'^[A-Z_]+$', busiCode):
            validate_busi_code(busiCode)
        self._busiCode = busiCode
        self._busiMsg = busiMsg
        self._httpCode = httpCode

    @property
    def getBusiCode(self):
        """返回业务编码."""
        return self._busiCode

    @property
    def getBusiMsg(self):
        """返回业务描述."""
        return self._busiMsg

    @property
    def getHttpCode(self):
        """返回HTTP状态码."""
        return self._httpCode


class ResponseEnum:
    """响应枚举类，包含错误代码、描述和 HTTP 状态码"""
    AccessDenied = ResCode("AccessDenied", "访问被拒绝", HttpStatus.FORBIDDEN)
    InternalError = ResCode("InternalError", "我们遇到了内部错误。请稍后再试。", HttpStatus.INTERNAL_SERVER_ERROR)
    InvalidArgument = ResCode("InvalidArgument", "无效参数", HttpStatus.BAD_REQUEST)
    InvalidRequest = ResCode("InvalidRequest", "SOAP 请求必须通过 HTTPS 连接发送。", HttpStatus.BAD_REQUEST)
    InvalidURI = ResCode("InvalidUri", "无法解析指定的 URI。", HttpStatus.BAD_REQUEST)
    RequestTimeout = ResCode("RequestTimeout", "您的套接字连接在超时期间内未读取或写入数据。", HttpStatus.GATEWAY_TIMEOUT)
    ReadTimeout = ResCode("ReadTimeout", "数据读取超时", HttpStatus.READ_TIMEOUT)
    ConnectionTimeout = ResCode("ConnectionTimeout", "请求连接超时", HttpStatus.CONNECTION_TIMEOUT)
    ConnectionError = ResCode("ConnectionError", "请求错误!", HttpStatus.BAD_GATEWAY)
    NotFoundApi = ResCode("NotFoundApi", "未找到 API", HttpStatus.NOT_FOUND)
    NotFoundData = ResCode("NotFoundData", "未找到数据", HttpStatus.NOT_FOUND)
    URLExpired = ResCode("UrlExpired", "URL 已过期，请获取一个新的。", HttpStatus.FORBIDDEN)
    InvalidKey = ResCode("InvalidKey", "无效密钥", HttpStatus.BAD_REQUEST)
    Unauthorized = ResCode("Unauthorized", "请求需要用户身份验证", HttpStatus.UNAUTHORIZED)
    NotifyFail = ResCode("NotifyFail", "通知失败", HttpStatus.BAD_REQUEST)
    CallbackFail = ResCode("CallbackFail", "回调服务器失败", HttpStatus.BAD_REQUEST)
    OK = ResCode("OK", "成功", HttpStatus.OK)
    Repeat_Request = ResCode("Repeat_Request", "重复请求", HttpStatus.OK)
    Sign_Is_Not_Pass = ResCode("Sign_Is_Not_Pass", "签名未通过", HttpStatus.BAD_REQUEST)
    Error_Token = ResCode("Error_Token", "非法授权", HttpStatus.UNAUTHORIZED)
    Payload_Too_Large = ResCode("Payload_Too_Large", "负载过大！", HttpStatus.FORBIDDEN)
    Too_Many_Request = ResCode("Too_Many_Request", "您已被限制，请稍后再试！", HttpStatus.TOO_MANY_REQUESTS)
    Meta_Data_Error = ResCode("Meta_Data_Error", "元数据错误！", HttpStatus.BAD_REQUEST)
    Param_Error = ResCode("Param_Error", "参数错误", HttpStatus.BAD_REQUEST)
    Time_Error = ResCode("Time_Error", "您的时间参数不正确或已过期！", HttpStatus.BAD_REQUEST)
    Rule_Not_Found = ResCode("Rule_Not_Found", "规则未找到！", HttpStatus.NOT_FOUND)
    Service_Timeout = ResCode("Service_Timeout", "服务调用超时！", HttpStatus.GATEWAY_TIMEOUT)
    Sign_Time_Is_Timeout = ResCode("Sign_Time_Is_Timeout", "签名时间戳已超过 %s 分钟！", HttpStatus.GATEWAY_TIMEOUT)
    Sentinel_Block_Error = ResCode("Sentinel_Block_Error", "请求被 Sentinel 阻止！", HttpStatus.BAD_REQUEST)
    Decryption_Error = ResCode(
        "Decryption_Error", "解密失败，请检查参数或密钥，或数据长度过长", HttpStatus.UNAVAILABLE_FOR_LEGAL_REASONS)
    Ecryption_Error = ResCode(
        "Ecryption_Error", "加密失败，请检查参数或密钥，或数据长度过长", HttpStatus.UNAVAILABLE_FOR_LEGAL_REASONS)
    Invalid_Xml_Data = ResCode("Invalid_Xml_Data", "XML 数据无效。", HttpStatus.BAD_REQUEST)
    Request_Header_Too_Large = ResCode("Request_Header_Too_Large", "请求头字段过大", HttpStatus.PAYLOAD_TOO_LARGE)
    Request_Entity_Too_Large = ResCode("Request_Entity_Too_Large", "请求实体过大", HttpStatus.PAYLOAD_TOO_LARGE)
    Security_Forbidden = ResCode("Security_Forbidden", "安全禁止", HttpStatus.FORBIDDEN)
    Redis_Error = ResCode("Redis_Error", "Redis 错误", HttpStatus.INTERNAL_SERVER_ERROR)
    Mysql_Error = ResCode("Mysql_Error", "MySQL 错误", HttpStatus.INTERNAL_SERVER_ERROR)
    Request_Header_Invalid = ResCode("Request_Header_Invalid", "请求头错误", HttpStatus.BAD_REQUEST)
    Source_Switching_Failed = ResCode("Source_Switching_Failed", "数据源切换保存", HttpStatus.INTERNAL_SERVER_ERROR)
    Third_Service_Error = ResCode("Third_Service_Error", "第三方服务错误", HttpStatus.INTERNAL_SERVER_ERROR)
    Data_Write_Failed = ResCode("Data_Write_Failed", "数据写入磁盘失败。", HttpStatus.BAD_REQUEST)
    File_Drop_Field = ResCode("File_Drop_Field", "文件丢弃字段", HttpStatus.BAD_REQUEST)
    File_Create_Field = ResCode("File_Create_Field", "文件创建字段", HttpStatus.BAD_REQUEST)
    PGsql_Error = ResCode("PGsql_Error", "PostgreSQL 错误", HttpStatus.BAD_REQUEST)
    PGsql_Insert_Error = ResCode("PGsql_Insert_Error", "PostgreSQL 插入错误", HttpStatus.BAD_REQUEST)
    PGsql_Update_Error = ResCode("PGsql_Update_Error", "PostgreSQL 更新错误", HttpStatus.BAD_REQUEST)
    PGsql_Query_Error = ResCode("PGsql_Query_Error", "PostgreSQL 查询错误", HttpStatus.BAD_REQUEST)
    Data_Not_Complete = ResCode("Data_Not_Complete", "数据不完整！", HttpStatus.BAD_REQUEST)
    Too_Much_Data = ResCode("Too_Much_Data", "数据过多，停止导出", HttpStatus.BAD_REQUEST)
    Table_No_UniqueIndex = ResCode("Table_No_UniqueIndex", "", HttpStatus.BAD_REQUEST)
    Table_Parse_Failed = ResCode("Table_Parse_Failed", "表解析失败", HttpStatus.BAD_REQUEST)
    Still_Failed_After_Retry = ResCode("Still_Failed_After_Retry", "重试后仍然失败", HttpStatus.BAD_REQUEST)
    Zero_Export_Data = ResCode("Zero_Export_Data", "零导出数据", HttpStatus.OK)
    Zero_Import_Data = ResCode("Zero_Import_Data", "零导入数据", HttpStatus.OK)
    Database_Is_Empty = ResCode("Database_Is_Empty", "数据库中的表为空", HttpStatus.OK)
    Folder_Is_Empty = ResCode("Folder_Is_Empty", "文件夹为空", HttpStatus.OK)
    File_Is_NotExist = ResCode("File_Is_NotExist", "文件不存在", HttpStatus.OK)
    Bucket_Not_Exist = ResCode("Bucket_Not_Exist", "存储桶不存在", HttpStatus.BAD_REQUEST)
    Final_Faild = ResCode("Final_Faild", "任务失败", HttpStatus.BAD_REQUEST)
    DDL_Query_Error = ResCode("DDL_Query_Error", "查询 DDL 错误", HttpStatus.BAD_REQUEST)
    JSON_Transform_Error = ResCode("JSON_Transform_Error", "JSON 转换错误", HttpStatus.BAD_REQUEST)
    Directory_Create_Error = ResCode("Directory_Create_Error", "目录创建错误", HttpStatus.BAD_REQUEST)
    File_Write_Error = ResCode("File_Write_Error", "文件写入错误", HttpStatus.BAD_REQUEST)
    Directory_Not_Exist = ResCode("Directory_Not_Exist", "目录不存在", HttpStatus.BAD_REQUEST)
    File_Read_Error = ResCode("File_Read_Error", "文件读取错误", HttpStatus.BAD_REQUEST)
    Sequence_Query_Error = ResCode("Sequence_Query_Error", "序列查询错误", HttpStatus.BAD_REQUEST)
    Sequence_Create_Error = ResCode("Sequence_Create_Error", "序列创建错误", HttpStatus.BAD_REQUEST)
    Export_File_Error = ResCode("Export_File_Error", "导出文件错误", HttpStatus.BAD_REQUEST)
    Import_Xml_Error = ResCode("Import_Xml_Error", "导入 XML 错误", HttpStatus.BAD_REQUEST)
    Field_Parsing_Error = ResCode("Field_Parsing_Error", "字段解析错误", HttpStatus.BAD_REQUEST)
    Dir_TARGZ_Error = ResCode("Dir_TARGZ_Error", "目录 TAR.GZ 错误", HttpStatus.BAD_REQUEST)
    Minio_Upload_Failed = ResCode("Minio_Upload_Failed", "Minio 上传失败", HttpStatus.BAD_REQUEST)
    Rollback_DDL_Failed = ResCode("Rollback_DDL_Failed", "回滚 DDL 失败", HttpStatus.BAD_REQUEST)
    Rollback_DML_Failed = ResCode("Rollback_DML_Failed", "回滚 DML 失败", HttpStatus.BAD_REQUEST)
    Some_File_Upload_Failed = ResCode("Some_File_Upload_Failed", "部分文件上传失败", HttpStatus.OK)
    Invalid_Tar_Data = ResCode("Invalid_Tar_Data", "tar 名称无效。", HttpStatus.BAD_REQUEST)
    Too_Retry_Request = ResCode("Too_Retry_Request", "您已被限制，请稍后再试！", HttpStatus.BAD_REQUEST)
    DB_Timeout = ResCode("Db_Timeout", "DB服务调用超时！", HttpStatus.GATEWAY_TIMEOUT)
    Redis_Error_Timeout = ResCode("Redis_Error_Timeout", "Redis服务调用超时！", HttpStatus.GATEWAY_TIMEOUT)
    Too_Many_Redirects = ResCode("Too_Many_Redirects", "请求跳转次数太多!", HttpStatus.BAD_REQUEST)
    Invalid_Header = ResCode("Invalid_Header", "请求头异常!", HttpStatus.BAD_REQUEST)
    Invalid_Proxy_URL = ResCode("Invalid_Proxy_URL", "错误的代理地址!", HttpStatus.BAD_REQUEST)
    Job_Execute_Field = ResCode("Job_Execute_Field", "job执行失败!", HttpStatus.BAD_REQUEST)
    Client_Connect_Timeout = ResCode("Client_Connect_Timeout", "数据库连接超时!", HttpStatus.GATEWAY_TIMEOUT)
    Db_Error = ResCode("Db_Error", "数据库错误!", HttpStatus.BAD_REQUEST)

    @classmethod
    def update_response_enum(cls, enum_class):
        """
        动态添加枚举类中的所有 ResCode 实例到 ResponseEnum 中。
        :param enum_class: 包含 ResCode 实例的类
        :raises ValueError: 如果响应项名称已存在
        """
        for name in dir(enum_class):
            if name.startswith('__'):
                continue  # 跳过内置属性
            attr = getattr(enum_class, name)
            if isinstance(attr, ResCode):
                if not hasattr(cls, name):
                    if hasattr(cls, name):
                        raise ValueError(f"ResponseEnum 中已存在 '{name}'，无法重复添加。")
                    setattr(cls, name, attr)

    @classmethod
    @classmethod
    def from_code(cls, code):
        """
        根据 busiCode 获取对应的 ResCode 实例。
        """
        for name in dir(cls):
            if name.startswith('__'):
                continue  # 跳过内置属性
            attr = getattr(cls, name)
            if isinstance(attr, ResCode) and attr.getBusiCode == code:
                return attr
        return None

class UserErrorEnmu():
    GitError = ResCode("GitError", "git产生错误！！", HttpStatus.GATEWAY_TIMEOUT)


if __name__ == '__main__':

    ResponseEnum.update_response_enum(UserErrorEnmu)
    print(ResponseEnum.OK.getBusiCode)
    print(ResponseEnum.GitError.getBusiCode)
    print(ResponseEnum.OK.getBusiMsg)
    print(ResponseEnum.OK.getHttpCode)
    # 通过错误代码获取枚举项
    code = "AccessDenied"
    enum_member = ResponseEnum.from_code(code)
    if enum_member:
        print(enum_member.getBusiMsg)  # 输出: 您已被限制，请稍后再试！
