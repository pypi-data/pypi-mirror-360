import sys
import shutil
from pathlib import Path


def print_version():
    try:
        from importlib.metadata import version
    except ImportError:
        from pkg_resources import get_distribution as version
    try:
        ver = version("pycmakebuild")
    except Exception:
        ver = "(dev)"
    print(f"Version: {ver}")


def init():
    # 执行环境初始化

    import os
    from .envs import init_env_file, init_build_json

    init_env_file()
    cwd = os.getcwd()
    init_build_json(cwd)
    print("已执行环境初始化")


def build(build_type: str = "Release", json_path: str = "build.json", env_path: str = ".env"):
    import os, json

    try:
        # 加载指定的环境变量文件
        from dotenv import load_dotenv
        if not load_dotenv(env_path):
            raise Exception(f"未能加载环境变量文件 {env_path}")

        from .api import build_and_install, BuildType, load_env_globals

        load_env_globals()

        if not os.path.isabs(json_path):
            json_path = os.path.join(os.getcwd(), json_path)
        if not os.path.exists(json_path):
            raise Exception(
                f"""未找到{json_path}
请先执行pycmakebuild --init初始化或指定正确的json文件。"""
            )
        print(f"使用配置文件: {json_path}, 构建类型: {build_type}")
        with open(json_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        sources = config.get("sources", [])
        for item in sources:
            path = item.get("path")
            name = item.get("name")
            build_types = [build_type]
            cmakelists_subpath = item.get("cmakelists_subpath", "")
            for bt in build_types:
                print(f"\n==== 构建 {name} [{bt}] ====")
                build_and_install(
                    project_path=path,
                    name=name,
                    build_type=BuildType[bt],
                    cmakelists_subpath=cmakelists_subpath,
                )
    except Exception as e:
        print(f"{e}")


def clean_all_projects(json_path: str = "build.json", env_path: str = ".env"):
    import os, json
    from .api import update_git_source

    if not os.path.isabs(json_path):
        json_path = os.path.join(os.getcwd(), json_path)
    if not os.path.exists(json_path):
        raise Exception(
            f"未找到{json_path}, 请先执行pycmakebuild --init初始化或指定正确的json文件。"
        )
    with open(json_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    sources = config.get("sources", [])
    if len(sources) == 0:
        raise Exception("build.json未配置任何工程，无法清理。")
    for item in sources:
        src = Path(item.get("path")).absolute().as_posix()
        name = item.get("name")

        print(f"更新项目: {name}, 安装目录: {src}")
        update_git_source(src)

    # 删除BUILD_DIR
    # if BUILD_DIR and os.path.exists(BUILD_DIR):
    #     print(f"清理构建目录: {BUILD_DIR}")
    #     shutil.rmtree(BUILD_DIR)
    print("批量清理完成！")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="pycmakebuild - 批量构建CMake工程的Python工具",
        prog="pycmakebuild",
    )
    parser.add_argument(
        "--env",
        type=str,
        default=".env",
        help="指定环境变量文件，默认为.env"
    )
    parser.add_argument(
        "--build",
        type=str,
        nargs="?",
        const="Release",
        default=None,
        choices=["Debug", "Release"],
        help="根据 build.json 批量构建，支持 --build=Debug 或 --build=Release，默认Release",
    )
    parser.add_argument(
        "--json",
        type=str,
        default="build.json",
        help="指定配置json文件，默认为build.json",
    )
    parser.add_argument(
        "--init", action="store_true", help="初始化环境(.env)和 build.json 模板"
    )
    parser.add_argument(
        "--clean", action="store_true", help="清理所有项目的源代码（git）"
    )
    parser.add_argument("--version", "-v", action="store_true", help="显示版本号")
    # argparse自带--help/-h
    args = parser.parse_args()

    if args.version:
        print_version()
        return
    if args.init:
        init()
        return
    if args.clean:
        clean_all_projects(json_path=args.json, env_path=args.env)
        return
    if args.build:
        build(build_type=args.build, json_path=args.json, env_path=args.env)
    else:
        build(build_type="Release", json_path=args.json, env_path=args.env)


if __name__ == "__main__":
    main()
