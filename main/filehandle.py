import os
from shutil import rmtree
from pathlib import Path
from zipfile import ZipFile
from typing import List

def get_shortcut_target(shortcut_path):
    try:
        # 使用winshell模块打开快捷方式
        shortcut = winshell.shortcut(shortcut_path)
        # 获取目标路径
        target_path = shortcut.path
        # 检查目标路径是否存在
        if os.path.exists(target_path):
            return target_path
        else:
            return None
    except Exception as e:
        print("Error accessing shortcut:", e)
        return None


def detctDefaultDir() -> List[str]:
    """
    检测默认游戏目录
    :return: 返回默认游戏目录,找不到返回空串
    """
    if os.path.exists(
        Path(os.path.expanduser(r"~\Documents\Euro Truck Simulator 2\profiles"))
    ):
        DOCUMENTS_DIR = (
            str(
                Path(os.path.expanduser(r"~\Documents\Euro Truck Simulator 2\profiles"))
            )
            + "\\"
        )
    else:
        DOCUMENTS_DIR = ""
    if os.path.exists(
        Path(os.path.expanduser(r"~\Documents\Euro Truck Simulator 2\readme.rtf.lnk"))
    ):
        GAME_DIR = get_shortcut_target(
            os.path.expanduser(r"~\Documents\Euro Truck Simulator 2\readme.rtf.lnk")
        ).rstrip("readme.rtf")
    else:
        GAME_DIR = ""
    return [DOCUMENTS_DIR, GAME_DIR]

dafaultDirectory=detctDefaultDir()