class Constants:
    # 静态字段
    Favicon = "/favicon.ico"
    Str_Place = "-"
    DATA = "data"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    #成功
    Code_1 = 1
    #失败
    Code_0 = 0

    CodeMap = {
        Code_1 : SUCCESS,
        Code_0: ERROR
    }
    HttpRangesMap = {
        SUCCESS: (100,399),
        ERROR: (400, 10000)
        # 可以添加更多的范围
    }