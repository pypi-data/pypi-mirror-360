import sys
import shutil
from pathlib import Path


def print_help():
    print(
        """
pycmakebuild - 批量构建CMake工程的Python工具

用法:
  pycmakebuild --init        初始化环境(.env)和 build.json 模板
  pycmakebuild --build       根据 build.json 批量构建
  pycmakebuild --clean       清理所有项目的源代码（git）
  pycmakebuild --version/-v  显示版本号
  pycmakebuild --help/-h     显示帮助信息
  pycmakebuild               自动检测 build.json 并批量构建(同pycmakebuild --build)

build.json 支持字段:
  path              CMake 项目源码路径
  name              目标名称
  build_types       构建类型数组（如 Debug/Release）
  cmakelists_subpath CMakeLists.txt 所在子目录（可选）
  other_build_params  传递给 cmake 的额外参数列表（可选）
        """
    )


def print_version():
    try:
        from importlib.metadata import version
    except ImportError:
        from pkg_resources import get_distribution as version
    try:
        ver = version("pycmakebuild")
    except Exception:
        ver = "(dev)"
    print(f"pycmakebuild version: {ver}")


def init():
    # 执行环境初始化

    import os
    from .envs import init_env_file, init_build_json

    init_env_file()
    cwd = os.getcwd()
    init_build_json(cwd)
    print("已执行pycmakebuild环境初始化")


def build():
    import os, json

    try:
        from .api import build_and_install, BuildType

        build_json_path = os.path.join(os.getcwd(), "build.json")
        if not os.path.exists(build_json_path):
            print("未找到build.json, 请先执行pycmakebuild --init初始化。")
            return
        with open(build_json_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        sources = config.get("sources", [])
        for item in sources:
            path = item.get("path")
            name = item.get("name")
            build_types = item.get("build_types", ["Debug"])
            cmakelists_subpath = item.get("cmakelists_subpath", "")
            for build_type in build_types:
                print(f"\n==== 构建 {name} [{build_type}] ====")
                build_and_install(
                    project_path=path,
                    name=name,
                    build_type=BuildType[build_type],
                    cmakelists_subpath=cmakelists_subpath,
                )
    except Exception as e:
        print(f"{e}")


def clean_all_projects():
    import os, json
    from .api import update_git_source, BUILD_DIR, INSTALL_PATH, ARCH, BuildType

    build_json_path = os.path.join(os.getcwd(), "build.json")
    if not os.path.exists(build_json_path):
        print("未找到build.json, 请先执行pycmakebuild --init初始化。")
        return
    with open(build_json_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    sources = config.get("sources", [])
    if len(sources) == 0:
        print("build.json未配置任何工程，无法清理。")
        return
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
    # 参照--help等命令风格，直接判断sys.argv
    if len(sys.argv) > 1 and sys.argv[1] == "--clean":
        clean_all_projects()
        return
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print_help()
        return
    if len(sys.argv) > 1 and sys.argv[1] in ("--version", "-v"):
        print_version()
        return
    if len(sys.argv) > 1 and sys.argv[1] == "--init":
        init()
        return
    # --build 命令：强制执行 build.json 批量编译
    elif len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] == "--build"):
        build()
        return
    # ...existing code...


if __name__ == "__main__":
    main()
