#!/usr/bin/env python3
"""主命令行界面模块。"""

import os
import subprocess
import sys
from pathlib import Path

import click
import tomlkit
from inquirer import confirm, list_input
from packaging.version import InvalidVersion, Version
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from tomlkit import items

from ._version import get_package_version
from .version_manager import VersionManager

console = Console()


def validate_version(version_string: str) -> bool:
    """验证版本号是否符合 PEP 440 规范

    Args:
        version_string: 要验证的版本号字符串

    Returns:
        bool: 如果版本号符合 PEP 440 规范返回 True，否则返回 False
    """
    try:
        Version(version_string)
        click.echo(f"✅ Version {version_string} is PEP 440 compliant")
        return True
    except InvalidVersion:
        click.echo(f"❌ Version '{version_string}' is not PEP 440 compliant")
        return False


def exec_command(command: str, silent: bool = False) -> str:
    """执行命令并返回结果。"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        if not silent:
            console.print(result.stdout.strip())
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if not silent:
            console.print(f"[red]❌ 命令执行失败: {command}[/red]")
            console.print(e.stderr)
            sys.exit(1)
        raise e


def get_current_version() -> tuple[str, str]:
    """获取当前版本号和配置文件类型。"""
    # 优先查找 pyproject.toml
    if Path("pyproject.toml").exists():
        with open("pyproject.toml") as f:
            doc = tomlkit.load(f)

        # 检查 [project] 部分
        project = doc.get("project")
        if isinstance(project, dict | items.Table) and "version" in project:
            return str(project["version"]), "pyproject.toml"

        # 检查 [tool.poetry] 部分
        tool = doc.get("tool")
        if isinstance(tool, dict | items.Table):
            poetry = tool.get("poetry")
            if isinstance(poetry, dict | items.Table) and "version" in poetry:
                return str(poetry["version"]), "pyproject.toml"

    # 检查 setup.py
    if Path("setup.py").exists():
        console.print("[yellow]⚠️  找到 setup.py, 但建议使用 pyproject.toml[/yellow]")
        # 简单的版本提取（实际可能更复杂）
        with open("setup.py") as f:
            content = f.read()
            import re

            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1), "setup.py"

    console.print("[red]❌ 未找到 Python 项目配置文件 (pyproject.toml 或 setup.py)[/red]")
    console.print("[dim]提示：这是一个 Python 版本管理工具，请在 Python 项目中使用[/dim]")
    sys.exit(1)


def update_version_file(new_version: str, file_type: str) -> None:
    """更新版本文件。"""
    if file_type == "pyproject.toml":
        with open("pyproject.toml") as f:
            doc = tomlkit.load(f)

        # 更新相应部分的版本
        project = doc.get("project")
        if isinstance(project, dict | items.Table) and "version" in project:
            project["version"] = new_version
        else:
            tool = doc.get("tool")
            if isinstance(tool, dict | items.Table):
                poetry = tool.get("poetry")
                if isinstance(poetry, dict | items.Table) and "version" in poetry:
                    poetry["version"] = new_version

        # 使用 tomlkit.dumps 保留原始格式
        with open("pyproject.toml", "w") as f:
            f.write(tomlkit.dumps(doc))

    elif file_type == "setup.py":
        # 简单的替换（实际可能需要更复杂的处理）
        with open("setup.py") as f:
            content = f.read()
        import re

        content = re.sub(r'version\s*=\s*["\'][^"\']+["\']', f'version="{new_version}"', content)
        with open("setup.py", "w") as f:
            f.write(content)


def get_current_branch() -> str:
    """获取当前 Git 分支。"""
    return exec_command("git branch --show-current", silent=True)


def check_git_status() -> bool:
    """检查工作区是否干净。"""
    status = exec_command("git status --porcelain", silent=True)
    if status:
        console.print("[yellow]⚠️  工作区有未提交的更改:[/yellow]")
        console.print(status)
        return False
    return True


def run_version_bump(dry_run=False):
    """执行版本升级的核心逻辑。"""
    try:
        console.print(Panel.fit("🔢 版本号管理工具", style="bold blue"))
        console.print()

        # 检查当前状态
        current_version, config_file = get_current_version()
        current_branch = get_current_branch()

        console.print(f"[cyan]📦 当前版本: {current_version}[/cyan]")
        console.print(f"[cyan]📄 配置文件: {config_file}[/cyan]")
        console.print(f"[cyan]🌿 当前分支: {current_branch}[/cyan]")

        # 如果是干跑模式，显示明显的提示
        if dry_run:
            console.print()
            console.print("[bold yellow]🎭 干跑模式已启用 - 所有操作仅为预览，不会实际执行[/bold yellow]")

        console.print()

        # 检查分支
        if current_branch not in ["main", "master"]:
            console.print("[yellow]⚠️  警告: 不在主分支上[/yellow]")
            if not confirm("确定要在非主分支上发布吗？", default=False):
                console.print("[red]✖ 发布已取消[/red]")
                sys.exit(0)

        # 检查工作区
        if not check_git_status():
            console.print("[red]✖ 发布已取消：工作区有未提交的更改[/red]")
            sys.exit(0)

        # 创建版本管理器
        version_manager = VersionManager()

        # 解析当前版本
        version_parts = version_manager.parse_version(current_version)
        if not version_parts:
            console.print(f"[red]❌ 无效的版本号格式: {current_version}[/red]")
            sys.exit(1)

        # 构建发布类型选项
        choices = ["正式版本 (Production)"]

        # Dev 版本只能在当前是 dev 版本或者没有预发布版本时选择
        if not version_parts.prerelease_type or version_parts.prerelease_type == "dev":
            choices.append("Dev 版本")

        if not version_parts.prerelease_type or version_parts.prerelease_type in ["dev", "a"]:
            choices.append("Alpha 版本")

        if not version_parts.prerelease_type or version_parts.prerelease_type in ["dev", "a", "b"]:
            choices.append("Beta 版本")

        if not version_parts.prerelease_type or version_parts.prerelease_type in ["dev", "a", "b", "rc"]:
            choices.append("RC 版本")

        # Post 版本只能从正式版本或者已有的 post 版本创建
        if not version_parts.prerelease_type or version_parts.prerelease_type == "post":
            choices.append("Post 版本")

        # 选择发布类型
        release_choice = list_input(message="选择发布类型", choices=choices, default=choices[0])

        if not release_choice:
            console.print("[red]✖ 发布已取消[/red]")
            sys.exit(0)

        # 解析选择
        is_prerelease = "正式版本" not in release_choice
        prerelease_type = None
        if is_prerelease:
            if "Dev" in release_choice:
                prerelease_type = "dev"
            elif "Alpha" in release_choice:
                prerelease_type = "a"
            elif "Beta" in release_choice:
                prerelease_type = "b"
            elif "RC" in release_choice:
                prerelease_type = "rc"
            elif "Post" in release_choice:
                prerelease_type = "post"

        # 选择版本号类型
        version_bump = "patch"

        if version_parts.prerelease_type:
            # 当前是预发布版本
            if is_prerelease and prerelease_type == version_parts.prerelease_type:
                console.print(f"[yellow]当前是 {version_parts.prerelease_type} 版本，将自动递增版本号[/yellow]")
            elif is_prerelease:
                type_names = {"dev": "Dev", "a": "Alpha", "b": "Beta", "rc": "RC", "post": "Post"}
                console.print(
                    f"[yellow]当前是 {type_names.get(version_parts.prerelease_type or '', version_parts.prerelease_type)} 版本，"
                    f"将切换到 {type_names.get(prerelease_type or '', prerelease_type)} 版本[/yellow]"
                )
            else:
                console.print(f"[yellow]当前是 {version_parts.prerelease_type} 版本，将发布为正式版本[/yellow]")
        else:
            # 需要选择版本递增类型
            major, minor, patch = version_parts.major, version_parts.minor, version_parts.patch

            suffix = f"{prerelease_type}0" if is_prerelease else ""

            version_choices = [
                f"Patch (修订号): {current_version} → {major}.{minor}.{patch + 1}{suffix}",
                f"Minor (次版本号): {current_version} → {major}.{minor + 1}.0{suffix}",
                f"Major (主版本号): {current_version} → {major + 1}.0.0{suffix}",
            ]

            selected = list_input(message="选择版本号递增类型", choices=version_choices, default=version_choices[0])

            if not selected:
                console.print("[red]✖ 发布已取消[/red]")
                sys.exit(0)

            if "Patch" in selected:
                version_bump = "patch"
            elif "Minor" in selected:
                version_bump = "minor"
            elif "Major" in selected:
                version_bump = "major"

        # 计算新版本号
        new_version = version_manager.get_next_version(current_version, version_bump, is_prerelease, prerelease_type)
        tag_name = f"v{new_version}"

        # 显示执行计划
        console.print()
        console.print(Panel.fit("📋 执行计划", style="bold blue"))

        table = Table(show_header=False, box=None)
        table.add_row("当前版本:", f"{current_version} → {new_version}")
        table.add_row("标签名称:", tag_name)

        release_type_name = "正式版本"
        if is_prerelease:
            type_names = {"a": "Alpha (内部测试)", "b": "Beta (公开测试)", "rc": "RC (候选发布)"}
            release_type_name = type_names.get(prerelease_type or "", "预发布版本")
        table.add_row("发布类型:", release_type_name)

        console.print(table)
        console.print()

        console.print("[bold blue]📝 执行步骤:[/bold blue]")
        steps = [
            f"更新版本号到 {new_version}",
            f'提交版本更新 (commit message: "chore: release {new_version}")',
            f"创建 Git 标签 {tag_name}",
            "推送提交和标签到远程仓库 (git push --follow-tags)",
            "如果配置了 CI/CD，将自动执行后续流程",
        ]

        for i, step in enumerate(steps, 1):
            console.print(f"  {i}. {step}")

        console.print(f'\n[dim]提交信息预览: "chore: release {new_version}"[/dim]')

        # 确认执行
        if not dry_run:
            if not confirm("确认执行以上步骤？", default=True):
                console.print("[red]✖ 发布已取消[/red]")
                sys.exit(0)

        # 执行版本更新流程
        console.print()
        console.print("[bold green]🏃 开始执行版本更新...[/bold green]")
        console.print()
        # 1. 更新版本号
        console.print(f"[cyan]📦 {'干跑: ' if dry_run else ''}更新版本号到 {new_version}...[/cyan]")
        if not dry_run:
            update_version_file(new_version, config_file)
        else:
            console.print(f"[dim]  将更新 {config_file} 中的版本号[/dim]")

        # 如果是 pyproject.toml 且存在 uv.lock，运行 uv sync 更新 lock 文件
        if config_file == "pyproject.toml" and Path("uv.lock").exists():
            if not dry_run:
                console.print("[dim]正在更新 uv.lock...[/dim]")
                exec_command("uv sync --quiet", silent=True)
            else:
                console.print("[dim]  uv sync --quiet[/dim]")

        # 2. 提交更改
        console.print(f"\n[cyan]💾 {'干跑: ' if dry_run else ''}提交版本更新...[/cyan]")
        if not dry_run:
            if config_file == "pyproject.toml":
                exec_command("git add pyproject.toml")
                # 如果存在 uv.lock，也添加它（因为版本号变化会更新 lock 文件）
                if Path("uv.lock").exists():
                    exec_command("git add uv.lock")
            elif config_file == "setup.py":
                exec_command("git add setup.py")

            exec_command(f'git commit -m "chore: release {new_version}"')
        else:
            if config_file == "pyproject.toml":
                console.print("[dim]  git add pyproject.toml[/dim]")
                if Path("uv.lock").exists():
                    console.print("[dim]  git add uv.lock[/dim]")
            elif config_file == "setup.py":
                console.print("[dim]  git add setup.py[/dim]")
            console.print(f'[dim]  git commit -m "chore: release {new_version}"[/dim]')

        # 3. 创建标签
        console.print(f"\n[cyan]🏷️  {'干跑: ' if dry_run else ''}创建标签 {tag_name}...[/cyan]")
        if not dry_run:
            exec_command(f'git tag -a {tag_name} -m "Release {new_version}"')
        else:
            console.print(f'[dim]  git tag -a {tag_name} -m "Release {new_version}"[/dim]')

        # 4. 推送提交和标签
        if not os.environ.get("BUMP_VERSION_SKIP_PUSH"):
            console.print(f"\n[cyan]📤 {'干跑: ' if dry_run else ''}推送提交和标签到远程仓库...[/cyan]")
            if not dry_run:
                exec_command("git push --follow-tags")
            else:
                console.print("[dim]  git push --follow-tags[/dim]")

        console.print()
        if dry_run:
            console.print("[bold yellow]🎭 干跑模式完成！[/bold yellow]")
            console.print(f"如果执行真实操作，版本 {new_version} 将被创建并推送到远程仓库")
            console.print("\n[dim]提示: 移除 --dry-run 参数以执行真实的版本更新[/dim]")
        else:
            console.print("[bold green]✅ 版本更新成功！[/bold green]")
            console.print(f"版本 {new_version} 已创建并推送到远程仓库")

        if config_file == "pyproject.toml":
            console.print("\n[bold blue]📦 发布到 PyPI:[/bold blue]")
            console.print("  1. 构建包: uv build")
            console.print("  2. 发布: uv publish")

    except Exception as e:
        console.print("\n[red]❌ 版本更新过程中出现错误[/red]")
        console.print(str(e))
        sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  用户取消操作[/yellow]")
        sys.exit(0)


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version=get_package_version(), prog_name="bump")
@click.option("--dry-run", is_flag=True, help="显示将要执行的操作但不实际执行（无副作用）")
def main(ctx, dry_run):
    """Python 项目版本号管理工具 - 自动更新版本号并创建 Git 标签

    \b
    使用方法:
      bump                          运行交互式版本管理（默认）
      bump --dry-run                干跑模式，显示将要执行的操作但不实际执行
      bump validate                 验证版本号
      bump-py                       别名命令

    \b
    功能特性:
      • 支持 PEP 440 版本规范
      • 支持正式版本和预发布版本（alpha/beta/rc/dev/post）
      • 自动更新 pyproject.toml 或 setup.py
      • 自动创建 Git 提交和标签
      • 版本号格式验证
      • 安全检查（分支和工作区状态）
      • 干跑模式（--dry-run）

    \b
    示例:
      bump                               # 交互式版本管理
      bump --dry-run                     # 干跑模式，预览操作
      bump validate 1.0.0                # 验证版本号
      bump-py validate 1.0.0a0           # 验证 Alpha 版本

    \b
    版本格式:
      1.0.0       正式版本
      1.0.0a0     Alpha 版本
      1.0.0b0     Beta 版本
      1.0.0rc0    Release Candidate
      1.0.0.dev0  开发版本
      1.0.0.post0 后发布版本

    \b
    环境变量:
      BUMP_VERSION_SKIP_PUSH  设置后跳过 git push

    更多信息请访问: https://github.com/yarnovo/bumpster-py
    """
    # 如果没有子命令，执行默认的版本升级
    if ctx.invoked_subcommand is None:
        run_version_bump(dry_run=dry_run)


@main.command()
@click.argument("version")
def validate(version):
    """验证版本号是否符合 PEP 440 规范

    \b
    示例:
      bump validate 1.0.0                ✅ 有效版本
      bump validate v1.0.0               ✅ 有效版本（自动处理 v 前缀）
      bump validate 1.0                  ✅ 有效版本
      bump validate 1.0.0a0              ✅ 有效的 Alpha 版本
      bump validate invalid              ❌ 无效版本

    \b
    退出码:
      0  版本号有效
      1  版本号无效

    \b
    在 CI/CD 中使用:
      if bump validate "$VERSION"; then
        echo "Version is valid"
      else
        echo "Version is invalid"
        exit 1
      fi
    """
    if validate_version(version):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
