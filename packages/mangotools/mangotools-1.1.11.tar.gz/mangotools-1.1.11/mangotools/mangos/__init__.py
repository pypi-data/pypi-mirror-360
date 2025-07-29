# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-02-26 11:46
# @Author : 毛鹏
import os
import platform
from pathlib import Path

import sys

python_version = sys.version_info
if f"{python_version.major}.{python_version.minor}" != "3.10":
    raise Exception("必须使用>Python3.10.4")
system = platform.system().lower()
if system == "windows":
    runtime_path = os.path.join(os.path.dirname(__file__), "pyarmor_runtime_windows")
elif system == "linux":
    runtime_path = os.path.join(os.path.dirname(__file__), "pyarmor_runtime_linux")
elif system == "Darwin" or system == "darwin":
    runtime_path = os.path.join(os.path.dirname(__file__), "pyarmor_runtime_linux")
else:
    raise RuntimeError(f"Unsupported platform: {system}")

if runtime_path not in sys.path:
    sys.path.append(runtime_path)
runtime_sub_path = os.path.join(runtime_path, "pyarmor_runtime_000000")
if runtime_sub_path not in sys.path:
    sys.path.append(runtime_sub_path)


def _load_pyarmor():
    """加载PyArmor运行时，完全适配您的打包结构"""
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        base_path = Path(base_path)
        if getattr(sys, 'frozen', False):
            runtime_dir = base_path / "mangos" / (
                "pyarmor_runtime_windows" if sys.platform == "win32" else "pyarmor_runtime_linux"
            )
        else:
            runtime_dir = base_path / (
                "pyarmor_runtime_windows" if sys.platform == "win32" else "pyarmor_runtime_linux"
            )

        if not runtime_dir.exists():
            raise RuntimeError(
                f"PyArmor运行时目录不存在\n"
                f"最终搜索路径: {runtime_dir}\n"
                f"当前工作目录: {os.getcwd()}\n"
                f"系统路径: {sys.path}\n"
                f"_MEIPASS: {getattr(sys, '_MEIPASS', '未设置')}"
            )
        runtime_dir_str = str(runtime_dir)
        if runtime_dir_str not in sys.path:
            sys.path.insert(0, runtime_dir_str)
        runtime_sub_dir = runtime_dir / "pyarmor_runtime_000000"
        if not runtime_sub_dir.exists():
            raise RuntimeError(f"缺少PyArmor子运行时目录: {runtime_sub_dir}")

        if str(runtime_sub_dir) not in sys.path:
            sys.path.insert(0, str(runtime_sub_dir))

    except Exception as e:
        raise RuntimeError(f"初始化PyArmor运行时失败: {str(e)}")


_load_pyarmor()
try:
    from mango import Mango

    Mango.v(1)
except ImportError as e:
    raise RuntimeError(f"导入mango模块失败，请检查PyArmor运行时配置。错误详情: {str(e)}")

__all__ = ['Mango']
