from setuptools import setup, find_packages

setup(
    name='sthg_common_base',
    version='0.4.7',
    packages=find_packages(include=['sthg_common_base*']),
    description='Python FastApi logs',
    # long_description=open('sthg_base_common/README.md').read(),
    long_description_content_type='text/markdown',
    author='DongQing',
    author_email='maoyouyu@163.com',
    url='https://github.com/yourusername/your_package_name',
    install_requires=[
        # 依赖项列表
        "fastapi >=0.68.0",  # 核心框架依赖‌:ml-citation{ref="3,4" data="citationList"}
        "uvicorn >=0.15.0",  # ASGI 服务器基础版本‌:ml-citation{ref="3,4" data="citationList"}
        "pydantic >=1.9.0",  # 数据验证库（FastAPI 依赖）‌:ml-citation{ref="3,4" data="citationList"}
        "starlette >=0.19.1",  # Web 工具集（FastAPI 依赖）‌:ml-citation{ref="3,4" data="citationList"}
        "sympy >=1.12",
        "requests>=2.32.3"
    ],
    classifiers=[
        # 包分类列表，例如：
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
)

