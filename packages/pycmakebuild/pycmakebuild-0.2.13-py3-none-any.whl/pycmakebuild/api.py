from cmake import CMAKE_BIN_DIR
from enum import Enum
from pathlib import Path
import shutil
import subprocess
import sys
import os



class BuildType(Enum):
    Debug = "Debug"
    Release = "Release"


def __clean_screen():
    if sys.platform == "win32":
        __execute_cmd("cls")
    else:
        __execute_cmd("clear")


def __gen_prefix_list(prefixs: list) -> str:
    if len(prefixs) == 0:
        return ""

    return f'''-DCMAKE_PREFIX_PATH="{';'.join(prefixs)}"'''


def __execute_cmd(cmd: str, cwd: str = None):
    print(f"执行命令: {cmd}, 工作目录: {cwd}")

    pro = subprocess.run(
        cmd,
        shell=True,
        encoding=("gb2312" if sys.platform == "win32" else "utf-8"),
        text=True,
        check=True,
        cwd=cwd,
    )
    if pro.returncode != 0:
        __clean_screen()
        print(f"命令执行失败: {cmd}")
        if pro.stderr:
            print(f"错误信息: {pro.stderr.strip()}")
        if sys.platform == "win32":
            raise Exception(f"命令执行异常: {pro.stderr.strip()}")


def update_git_source(src_dir: str):
    abs_source_path = Path(src_dir).absolute().as_posix()
    print(f"更新源码工程:{abs_source_path}")
    __execute_cmd("git clean -fdx", cwd=abs_source_path)
    __execute_cmd("git checkout .", cwd=abs_source_path)
    __execute_cmd(
        "git submodule foreach --recursive git clean -fdx", cwd=abs_source_path
    )
    __execute_cmd(
        "git submodule foreach --recursive git checkout .", cwd=abs_source_path
    )
    __execute_cmd("git pull", cwd=abs_source_path)
    __execute_cmd("git submodule update --init --recursive", cwd=abs_source_path)
    print("更新源码工程成功!")


# 供外部调用
__all__ = ["build_and_install", "update_git_source", "BuildType"]



# 解析.env文件并返回变量字典
def parse_env_file(env_path: str = ".env") -> dict:
    abs_env_path = env_path
    if not os.path.isabs(env_path):
        abs_env_path = os.path.join(os.getcwd(), env_path)
    env_vars = {}
    if not os.path.exists(abs_env_path):
        raise Exception(
            f"未找到.env文件({abs_env_path})或加载环境变量失败.\n"
            "使用pycmakebuild --init进行初始化\n"
            "使用pycmakebuild --help查看帮助信息。"
        )
    with open(abs_env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env_vars[k.strip()] = v.strip()
    print(f"加载环境变量文件{abs_env_path}")
    return env_vars


# 通过传入的env_vars字典初始化临时变量
def load_env_globals(env_vars: dict):
    global IS_WINDOWS, INSTALL_PATH, GENERATOR, ARCH, CMAKE_ARCH, BUILD_DIR, CORES
    IS_WINDOWS = sys.platform.startswith("win")
    print(f"操作系统({sys.platform}):IS_WINDOWS={IS_WINDOWS}")

    INSTALL_PATH = env_vars.get("INSTALL_PATH")
    if INSTALL_PATH is None or len(INSTALL_PATH) == 0:
        raise Exception("未设置安装路径环境变量INSTALL_PATH")
    else:
        print(f"安装路径:INSTALL_PATH={INSTALL_PATH}")

    GENERATOR = env_vars.get("GENERATOR")
    if GENERATOR is None or len(GENERATOR) == 0:
        raise Exception("未设置生成器环境变量GENERATOR(参考CMake的-G选项)")
    else:
        print(f"生成器:GENERATOR={GENERATOR}")

    ARCH = env_vars.get("ARCH")
    if ARCH is None or len(ARCH) == 0:
        raise Exception("未设置架构环境变量ARCH")
    else:
        CMAKE_ARCH = __guess_cmake_arch()
        print(f"架构:ARCH={ARCH}{'' if len(CMAKE_ARCH)==0 else f'({CMAKE_ARCH})'}")

    BUILD_DIR = env_vars.get("BUILD_DIR")
    if BUILD_DIR is None or len(BUILD_DIR) == 0:
        raise Exception("未设置构建目录环境变量:BUILD_DIR")
    else:
        print(f"构建目录:BUILD_DIR={BUILD_DIR}")

    CORES = env_vars.get("CORES")
    try:
        CORES = int(CORES)
        if CORES <= 0:
            CORES = 32
    except Exception:
        CORES = 32
    print(f"编译核心数: CORES={CORES}")


# 根据平台、GENERATOR和ARCH自动推断CMAKE_ARCH
def __guess_cmake_arch():
    # 根据平台、CMake生成器和架构自动推断CMake的-A参数，仅在Windows+Visual Studio下生效。
    if not IS_WINDOWS:
        return ""
    gen = GENERATOR.lower() if GENERATOR else ""
    arch = ARCH.lower() if ARCH else ""
    # 只对 Visual Studio 生成器返回 -A xxx，其它生成器（如Ninja/MinGW）不返回平台参数，避免CMake报错。
    if "visual studio" in gen:
        if arch in ["x86", "win32"]:
            return "-A Win32"
        elif arch in ["x64", "amd64"]:
            return "-A x64"
        elif arch in ["arm64"]:
            return "-A ARM64"
    # 其他生成器不返回任何平台参数
    return ""





def build_and_install(
    project_path: str,
    name: str,
    other_build_params: list = [],
    cmakelists_subpath: str = "",
    build_type: BuildType = BuildType.Debug,
) -> bool:
    """
    编译并安装指定的CMake工程。

    参数：
        project_path (str): 工程根目录路径
        name (str): 库名称（用于安装路径和打印信息）。
        update_source (bool): 是否先更新源码。
        other_build_params (list): 额外传递给cmake的参数列表。
        cmakelists_subpath (str): CMakeLists.txt子目录（可选）。
        build_type (BuildType): 构建类型（Debug/Release）。

    返回：
        bool: 构建和安装是否成功。
    """

    source_path = Path(project_path)
    if len(cmakelists_subpath) > 0:
        source_path = source_path.joinpath(cmakelists_subpath)

    if not source_path.exists():
        raise Exception(f"源码目录{source_path.absolute().as_posix()}不存在")
    abs_source_path = source_path.absolute().as_posix()

    if len(name) == 0:
        raise Exception("库名称为空")

    install_path = Path(INSTALL_PATH)

    install_path = install_path.joinpath(ARCH)
    install_path = install_path.joinpath(build_type.value)
    install_path = install_path.joinpath(name)

    abs_install_path = install_path.absolute().as_posix()

    # if update_source:
    #     clean_git_source(abs_source_path, abs_install_path)
    # else:
    #     if os.path.exists(abs_install_path):
    #         print(f"安装目录:{abs_install_path} 已存在, 跳过安装!\n")
    #         return True

    print(f"编译器信息:{name} / {GENERATOR} / {build_type.value} / {ARCH} ...")

    print(f"工程路径： {abs_source_path}, 安装路径： {abs_install_path}")

    build_dir = f"{BUILD_DIR}/{name}/build_{ARCH}_{build_type.value}"

    print(f"开始配置工程{name}并保存配置文件到{build_dir}...")

    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    if not os.path.exists(abs_install_path):
        os.makedirs(abs_install_path)

    args = [
        f"-S {abs_source_path}",
        f"-B {build_dir}",
        f'-G "{GENERATOR}"',
        # f"-DCMAKE_BUILD_TYPE={build_type.value}",
        CMAKE_ARCH,
        f"-DCMAKE_INSTALL_PREFIX={abs_install_path}",
        "  ".join(other_build_params),
    ]
    __execute_cmd(f"{CMAKE_BIN_DIR}/cmake {' '.join(args)}", cwd=abs_source_path)

    print(f"配置工程{name}成功!开始编译工程{name}...")

    args = [
        f"--build {build_dir}",
        f"--config {build_type.value}",
        f"-j{CORES}",
    ]
    __execute_cmd(f"{CMAKE_BIN_DIR}/cmake {' '.join(args)}", cwd=abs_source_path)

    print(f"编译工程{name}成功! 开始安装工程{name}...")

    args = [f"--install {build_dir}", f"--config {build_type.value}"]
    __execute_cmd(f"{CMAKE_BIN_DIR}/cmake {' '.join(args)}", cwd=abs_source_path)

    print(f"安装工程{name}成功!\n")
    return True
