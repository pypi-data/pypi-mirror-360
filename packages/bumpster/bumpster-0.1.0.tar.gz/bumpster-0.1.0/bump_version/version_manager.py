"""版本管理核心功能模块。"""

from dataclasses import dataclass
from typing import Literal

from packaging.version import InvalidVersion, Version

ReleaseType = Literal["major", "minor", "patch"]
PrereleaseType = Literal["a", "b", "rc", "dev", "post"]  # Python 风格的预发布类型


@dataclass
class VersionParts:
    """版本号组成部分。"""

    major: int
    minor: int
    patch: int
    prerelease_type: PrereleaseType | None = None
    prerelease_num: int | None = None
    dev: int | None = None  # 开发版本号
    post: int | None = None  # 后发布版本号
    local: str | None = None  # Python 支持本地版本标识符


class VersionManager:
    """版本管理器。"""

    def parse_version(self, version: str) -> VersionParts | None:
        """解析版本号，支持 PEP 440 格式。"""
        # 移除可能的 'v' 前缀
        version = version.lstrip("v")

        try:
            pv = Version(version)
        except InvalidVersion:
            return None

        # 提取主版本号
        if len(pv.release) >= 3:
            major, minor, patch = pv.release[:3]
        else:
            # 处理版本号不完整的情况（如 1.0 -> 1.0.0）
            release = [*list(pv.release), 0, 0, 0]
            major, minor, patch = release[:3]

        # 统一处理预发布类型和版本号
        prerelease_type = None
        prerelease_num = None
        dev_num = None
        post_num = None

        # 优先级：dev < pre < 正式版 < post
        if pv.dev is not None:
            # dev 版本
            prerelease_type = "dev"
            prerelease_num = pv.dev
            dev_num = pv.dev
        elif pv.pre:
            # alpha, beta, rc 版本
            prerelease_type = pv.pre[0]  # 'a', 'b', 'rc'
            prerelease_num = pv.pre[1]
        elif pv.post is not None:
            # post 版本
            prerelease_type = "post"
            prerelease_num = pv.post
            post_num = pv.post

        return VersionParts(
            major=major,
            minor=minor,
            patch=patch,
            prerelease_type=prerelease_type,  # type: ignore
            prerelease_num=prerelease_num,
            dev=dev_num,
            post=post_num,
            local=pv.local,
        )

    def get_next_version(
        self,
        current_version: str,
        release_type: ReleaseType,
        is_prerelease: bool,
        prerelease_type: PrereleaseType | None,
    ) -> str:
        """计算下一个版本号。"""
        version_parts = self.parse_version(current_version)
        if not version_parts:
            raise ValueError(f"无效的版本号格式: {current_version}")

        major = version_parts.major
        minor = version_parts.minor
        patch = version_parts.patch

        # 如果当前是预发布版本
        if version_parts.prerelease_type:
            if is_prerelease and prerelease_type:
                if prerelease_type == version_parts.prerelease_type:
                    # 相同类型：递增版本号
                    new_num = (version_parts.prerelease_num or 0) + 1
                    if prerelease_type in ["dev", "post"]:
                        return f"{major}.{minor}.{patch}.{prerelease_type}{new_num}"
                    else:
                        return f"{major}.{minor}.{patch}{prerelease_type}{new_num}"
                else:
                    # 不同类型：检查升级路径
                    # PEP 440 顺序: dev < a < b < rc < 正式版 < post
                    prerelease_order = ["dev", "a", "b", "rc"]

                    # 处理 post 版本的特殊情况
                    if version_parts.prerelease_type == "post":
                        # 从 post 版本只能继续 post 或者升级到新的主/次/修订版本
                        if prerelease_type == "post":
                            new_num = (version_parts.prerelease_num or 0) + 1
                            return f"{major}.{minor}.{patch}.post{new_num}"
                        else:
                            # 不允许从 post 回到其他预发布版本
                            raise ValueError(f"不能从 post 版本回到 {prerelease_type} 版本")
                    elif prerelease_type == "post":
                        # 不能从预发布版本直接到 post 版本
                        raise ValueError("不能从预发布版本直接升级到 post 版本，请先发布正式版本")

                    current_idx = (
                        prerelease_order.index(version_parts.prerelease_type)
                        if version_parts.prerelease_type in prerelease_order
                        else -1
                    )
                    new_idx = prerelease_order.index(prerelease_type) if prerelease_type in prerelease_order else -1

                    if new_idx > current_idx:
                        # 升级预发布类型
                        if prerelease_type in ["dev", "post"]:
                            return f"{major}.{minor}.{patch}.{prerelease_type}0"
                        else:
                            return f"{major}.{minor}.{patch}{prerelease_type}0"
                    else:
                        # 降级警告，但仍然允许
                        if prerelease_type in ["dev", "post"]:
                            return f"{major}.{minor}.{patch}.{prerelease_type}0"
                        else:
                            return f"{major}.{minor}.{patch}{prerelease_type}0"
            else:
                # 预发布 -> 正式版：去掉预发布后缀
                return f"{major}.{minor}.{patch}"
        else:
            # 当前是正式版本
            if is_prerelease and prerelease_type == "post":
                # 正式版本可以直接升级到 post 版本
                return f"{major}.{minor}.{patch}.post0"

            if release_type == "major":
                major += 1
                minor = 0
                patch = 0
            elif release_type == "minor":
                minor += 1
                patch = 0
            elif release_type == "patch":
                patch += 1

            new_version = f"{major}.{minor}.{patch}"

            if is_prerelease and prerelease_type and prerelease_type != "post":
                if prerelease_type == "dev":
                    new_version += f".{prerelease_type}0"
                else:
                    new_version += f"{prerelease_type}0"

            return new_version
