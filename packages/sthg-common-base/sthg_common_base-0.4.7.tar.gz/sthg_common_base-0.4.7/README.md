# sthg_common_base


##  开发模式 安装本地包 测试
pip install -e .

##  另外一个项目引入本地安装的包
pip install -e D:\workspace2025\workspace-sthg-2025\06\sthg_common_base

## Getting started
## 打包前先修改  setup.py 里的 version的值
 python3.11 setup.py sdist bdist_wheel
## 上传 使用token 在.pypirc 文件
 twine upload dist/*

## 序列化跳过
EnhancedJSONSerializer中的 _excluded_classes 可以设置
## 序列化自定义
EnhancedJSONSerializer中的 _custom_serializers 可以设置

