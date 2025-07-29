import os
import sys
from pathlib import Path


def load_path():
    """
    向上查找 [config.py or pyproject.toml] 所在目录，并将其添加到 sys.path 中。
    """
    current_dir = Path(sys.modules.get("__main__").__file__).resolve().parent
    root_dir = None
    for parent in [current_dir, *current_dir.parents]:
        if (parent / "config.py").exists() or (parent / "pyproject.toml").exists():
            root_dir = parent
            break
    if root_dir is not None:
        root_path = str(root_dir)
        if sys.path[0] != root_path:
            sys.path.insert(0, root_path)
            print(f"[load_path] 添加路径到 sys.path: {root_path}")
    else:
        print("[load_path] 未找到 config.py 或 pyproject.toml，未修改 sys.path。")
