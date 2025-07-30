import os
import inspect
import sys
import configparser
from pathlib import Path
from typing import Optional

def _get_root_project_name() -> Optional[str]:
    """安全回溯获取项目根目录名称（静默模式）"""

    def _find_root(start: Path) -> Optional[Path]:
        """静默查找项目根目录"""
        if not start.exists():
            return None

        for parent in start.parents:
            # 检测常见项目标识文件
            if any((parent / marker).exists() for marker in [
                '.git',
                'pyproject.toml',
                'setup.py',
                'requirements.txt'
            ]):
                return parent
            if parent == parent.parent:  # 到达系统根目录
                break
        return None

    # 获取入口路径（多级降级）
    entry_path = None
    try:
        # 方法1：调用栈分析
        frame = inspect.currentframe()
        while frame and frame.f_back:
            frame = frame.f_back
        if module := inspect.getmodule(frame):
            if hasattr(module, '__file__') and module.__file__:
                entry_path = Path(module.__file__).resolve()
    except Exception:
        pass

    # 方法2：命令行参数
    if not entry_path and sys.argv[0]:
        try:
            entry_path = Path(sys.argv[0]).resolve()
        except Exception:
            pass

    # 方法3：当前工作目录
    if not entry_path:
        entry_path = Path.cwd()

    # 执行查找
    if root := _find_root(entry_path):
        return root.name
    return None

def _get_config_project_name() -> Optional[str]:
    """静默模式读取配置（支持 YAML）"""
    config_files = [
        Path("pyproject.toml"),
        Path("setup.cfg"),
        Path("settings.ini"),
        Path("config/settings.ini"),
        Path("config/settings.yaml"),
        Path("settings.yaml"),
        Path("config/settings.yml"),
        Path("settings.yml")
    ]

    for cfg_path in config_files:
        if not cfg_path.exists():
            continue

        try:
            # YAML 格式处理
            if cfg_path.suffix in ('.yaml', '.yml'):
                try:
                    import yaml  # 需要 PyYAML 库
                    with open(cfg_path, 'r') as f:
                        data = yaml.safe_load(f)
                        # 多层级尝试获取名称
                        return (
                            data.get('project', {}).get('name')  # project.name
                            or data.get('name')  # 顶层 name
                            or data.get('metadata', {}).get('name')  # metadata.name
                        )
                except ImportError:  # 未安装 PyYAML
                    continue
                except Exception:  # 解析失败
                    continue

            # TOML 格式处理
            if cfg_path.name == 'pyproject.toml':
                try:
                    import toml
                    data = toml.load(cfg_path)
                    return data.get('project', {}).get('name') or \
                           data.get('tool', {}).get('poetry', {}).get('name')
                except ImportError:
                    pass
                except Exception:
                    continue

            # INI 格式处理
            config = configparser.ConfigParser()
            config.read(cfg_path)
            if config.has_section('project'):
                return config.get('project', 'name', fallback=None)
            if config.has_section('metadata'):
                return config.get('metadata', 'name', fallback=None)

        except Exception:
            continue

    return None

def get_project_name(default: str = "unknown_project") -> str:
    """
    安全获取项目名称（三级降级策略）
    Args:
        default: 所有方法失败时的默认返回值
    Returns:
        项目名称或默认值（永远不会抛出异常）
    """
    # 第一级：配置读取

    try:
        if name := os.getenv("PROJECT_NAME",None):
            return name
        if name := _get_config_project_name():
            return name
        # 第二级：路径回溯
        if name := _get_root_project_name():
            return name
        # 第三级：当前目录名称
        if name := Path.cwd().name:
            return name
    except Exception:
        return default

    return default
# 示例用法
if __name__ == '__main__':
    print(f"Detected project name: {get_project_name()}")