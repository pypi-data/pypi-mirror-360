# -*- coding: utf-8 -*-
import sys, os
from pathlib import Path
from dotenv import load_dotenv


def init_env_file():
    """初始化环境变量文件 .env"""
    if not os.path.exists(".env"):
        envs = []
        pwd_dir = Path(os.getcwd())
        envs.append(f"# 安装路径，所有库的安装输出目录")
        envs.append(f"INSTALL_PATH={pwd_dir.joinpath('libs').absolute()}")
        envs.append(f"# 架构类型")
        # 自动推断架构
        if sys.platform.startswith("win"):
            import platform

            arch = platform.machine().lower()
            if arch in ["amd64", "x86_64"]:
                envs.append(f"ARCH=x64")
            elif arch in ["x86", "i386", "i686"]:
                envs.append(f"ARCH=x86")
            elif "arm" in arch:
                envs.append(f"ARCH=arm64")
            else:
                envs.append(f"ARCH={arch}")
        else:
            envs.append(f"ARCH=x64")
        envs.append(f"# 构建中间文件夹路径")
        envs.append(f"BUILD_DIR={pwd_dir.joinpath('builds').absolute()}")
        # 自动推断生成器
        if sys.platform.startswith("win"):
            import shutil

            # 优先检测 vswhere
            vswhere = shutil.which("vswhere")
            if vswhere:
                envs.append(f"# CMake生成器类型 (已检测到 Visual Studio)")
                envs.append(f"GENERATOR=Visual Studio 16 2019")
            elif shutil.which("ninja"):
                envs.append(f"# CMake生成器类型 (已检测到 Ninja)")
                envs.append(f"GENERATOR=Ninja")
            else:
                envs.append(f"# CMake生成器类型 (默认)")
                envs.append(f"GENERATOR=Visual Studio 16 2019")
        else:
            if os.path.exists("/usr/bin/ninja") or shutil.which("ninja"):
                envs.append(f"# CMake生成器类型 (已检测到 Ninja)")
                envs.append(f"GENERATOR=Ninja")
            else:
                envs.append(f"# CMake生成器类型 (默认)")
                envs.append(f"GENERATOR=Unix Makefiles")

        with open(".env", "w", encoding="utf-8") as f:
            f.write("\n".join(envs))


def init_build_json(target_dir=None, name=None):
    import json

    build_json_path = os.path.join(target_dir or os.getcwd(), "build.json")
    if not os.path.exists(build_json_path):
        build_json = {
            "sources": [
                {
                    "path": "源码路径",
                    "name": "目标目录名称",
                    "build_types": ["Debug", "Release"],
                    "cmakelists_subpath": "CMakeLists.txt所在子目录（可选）",
                    "update_source": True,
                    "other_build_params": ["-DCUSTOM_OPTION=ON"],
                }
            ]
        }
        with open(build_json_path, "w", encoding="utf-8") as f:
            json.dump(build_json, f, indent=2, ensure_ascii=False)
        print(f"已创建 {build_json_path}")
    else:
        print(f"已存在 {build_json_path}")
