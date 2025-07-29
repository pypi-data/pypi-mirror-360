# pycmakebuild

Python CMake 批量构建与自动化工具，支持通过 build.json 配置文件和命令行批量编译多个 CMake 项目，适用于跨平台 C++/第三方库工程的自动化批量编译。

## 功能特性
- 支持 build.json 配置批量管理和编译多个 CMake 项目
- 支持 Debug/Release 等多种构建类型，支持自定义 CMakeLists.txt 子目录
- 支持命令行一键初始化环境、生成模板、批量构建
- 自动推断 CMake 构建参数，兼容 Windows/Linux/Mac
- 支持通过 `python -m pycmakebuild` 或 `pycmakebuild` 命令行调用

## 快速开始

### 1. 安装
```bash
pip install pycmakebuild
```


### 2. 初始化环境和模板
```bash
python -m pycmakebuild --init
```
将在当前目录生成 .env 和 build.json 模板。

### 3. 编辑 build.json
示例：
```json
{
  "sources": [
    {
      "path": "../Log4Qt",
      "name": "log4qt",
      "build_types": ["Debug", "Release"],
      "cmakelists_subpath": ".",
      "update_source": false,
      "other_build_params": ["-DCUSTOM_OPTION=ON"]
    }
  ]
}
```
- `path`: CMake 项目源码路径
- `name`: 目标名称（安装目录名）
- `build_types`: 构建类型数组（如 Debug/Release）
- `cmakelists_subpath`: CMakeLists.txt 所在子目录（可选，默认"."）
- `update_source`: 是否自动更新源码 git clean/pull（可选，默认 false）
- `other_build_params`: 传递给 cmake 的额外参数列表（如 ["-DCUSTOM_OPTION=ON"]，可选）
- "update_source" 字段已废弃，如需清理请用 --clean 命令

### 4. 批量构建
```bash
python -m pycmakebuild --build
```
或直接
```bash
python -m pycmakebuild
```
会自动检测当前目录下 build.json 并批量构建所有配置项目，支持自定义 cmake 参数。

### 5. 批量清理源码和安装目录
```bash
python -m pycmakebuild --clean
```
自动清理更新源码

## 命令行参数
- `--init`  初始化环境和 build.json 模板
- `--build` 强制根据 build.json 批量构建
- `--clean` 批根据 build.json 更新源码

## 依赖
- python-dotenv：环境变量管理
- cmake：Python CMake 封装

## 典型应用场景
- 本地一键环境初始化默认构建环境与批量编译CMake三方库

## License
MIT
