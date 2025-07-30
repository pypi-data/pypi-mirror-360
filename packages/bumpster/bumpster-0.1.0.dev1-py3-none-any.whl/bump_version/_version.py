"""版本信息管理模块。"""

from pathlib import Path

import tomlkit
from tomlkit import items


def get_package_version() -> str:
    """获取当前包的版本号。"""
    try:
        # 尝试从包的根目录读取 pyproject.toml
        project_root = Path(__file__).parent.parent
        pyproject_path = project_root / "pyproject.toml"

        if pyproject_path.exists():
            with open(pyproject_path) as f:
                doc = tomlkit.load(f)

            project = doc.get("project")
            if isinstance(project, dict | items.Table):
                version = project.get("version")
                if version:
                    return str(version)

            return "unknown"

        # 如果找不到，返回默认值
        return "unknown"
    except Exception:
        return "unknown"
