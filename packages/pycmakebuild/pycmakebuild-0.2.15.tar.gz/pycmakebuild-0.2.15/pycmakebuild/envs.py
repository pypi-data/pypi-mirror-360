# -*- coding: utf-8 -*-
import sys, os
from pathlib import Path


def init_env_file():
    """初始化环境变量文件 .env"""
    if not os.path.exists(".env"):
        envs = []
        pwd_dir = Path(os.getcwd())
        envs.append(f"# 安装路径")
        envs.append(f"INSTALL_PATH={pwd_dir.joinpath('libs').absolute()}")
        envs.append(f"# 架构类型 可选值: x86, x64, arm64, amd64, win32, i386, i686")
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
        generator_comment = "# 可用CMake生成器类型(自动检测):"
        try:
            import subprocess

            result = subprocess.run(
                ["cmake", "-G"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )
            lines = result.stderr.splitlines() if result.stderr else result.stdout.splitlines()
            gen_lines = []
            found = False
            last_line = None
            for line in lines:
                if "Generators" in line:
                    found = True
                    continue
                if found:
                    if not line.strip():
                        break
                    # 过滤掉(deprecated)相关行
                    if "(deprecated)" in line:
                        continue
                    # 合并多行描述
                    if last_line is not None and (line.startswith("    ") or line.startswith("\t")):
                        # 上一行是生成器名，这一行是描述，合并
                        gen_lines[-1] += " " + line.strip()
                        last_line = gen_lines[-1]
                    else:
                        gen_lines.append(line.strip())
                        last_line = gen_lines[-1]
            if gen_lines:
                generator_comment += "\n" + "\n".join([f"#   {l}" for l in gen_lines])
        except Exception as e:
            generator_comment += f" (获取失败: {e})"
        envs.append(generator_comment)
        if sys.platform.startswith("win"):
            import shutil

            # 优先检测 vswhere
            vswhere = shutil.which("vswhere")
            envs.append(f"# CMake生成器类型")
            if vswhere:
                envs.append(f"GENERATOR=Visual Studio 16 2019")
            elif shutil.which("ninja"):
                envs.append(f"GENERATOR=Ninja")
            else:
                envs.append(f"GENERATOR=Visual Studio 16 2019")
        else:
            if os.path.exists("/usr/bin/ninja") or shutil.which("ninja"):
                envs.append(f"GENERATOR=Ninja")
            else:
                envs.append(f"GENERATOR=Unix Makefiles")
        envs.append(f"# 默认编译核心数")
        envs.append(f"CORES=32")

        with open(".env", "w", encoding="utf-8") as f:
            f.write("\n".join(envs))


def init_build_json(target_dir=None, name=None):
    import json

    build_json_path = os.path.join(target_dir or os.getcwd(), "build.json")
    if not os.path.exists(build_json_path):
        build_json = {
            "sources": [
                {
                    "path": "Log4Qt",
                    "name": "log4qt",
                    "cmakelists_subpath": ".",
                    "other_build_params": [],
                }
            ],
        }
        with open(build_json_path, "w", encoding="utf-8") as f:
            json.dump(build_json, f, indent=2, ensure_ascii=False)
        print(f"已创建 {build_json_path}")
    else:
        print(f"已存在 {build_json_path}")
