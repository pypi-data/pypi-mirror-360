## 简介

通过 [tobe：1分钟创建StreamableHTTP MCP 并5分钟验证]我们了解到开发 MCP 服务是非常容易的，如果我们想分享 [MCP Server]给其他开发者使用，打包上传到官方PyPI仓库是更好的选择，本文将介绍上传 Python 报并通过 uvx 来启动 MCP Server 的全流程。

## 创建标准Python项目

首先初始化一个标准的Python 项目。

```text
uv init
uv venv
source .venv/bin/activate
uv add fastmcp
```

这里最好创建一个子目录来放源文件，创建空的__init__.py，最后项目目录如下。

```text
├── README.md
├── pyproject.toml
├── server.py
├── tobe_time_mcp
│   ├── __init__.py
│   └── server.py
├── uv.lock
```

然后编写一个有入口函数的 MCP Server 类，文件为sever.py。

```text
from fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP()

@mcp.tool
def get_current_time():
    """Get current time"""
    return datetime.now()

def main():
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000, path="/mcp")

if __name__ == "__main__":
    main()
```

然后修改项目配置文件，确定包名和命令名。

```text
[project]
name = "tobe-time-mcp"
version = "0.1.0"
description = "The MCP server to get local time"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastmcp>=2.7.0",
]

[tool.uv.workspace]
members = ["venv"]

[project.scripts]
tobe-time-mcp = "tobe_time_mcp.server:main"
```

## Python项目打包

接下来就是对 Python 项目进行打包，首先安装打包和上传依赖的工具。

```text
uv pip install build twine
```

然后执行打包命令。

```text
python -m build
```

打包成功后会保存文件到dist 目录。

## Python项目上传

上传项目到 PyPI 需要现在官网注册账号，然后创建 API token，建议把 token 配置保存到本地。

```text
vim $HOME/.pypirc
```

然后执行命令上传即可。

```text
python -m twine upload ./dist/*
```

## 使用uvx启动服务

上传 PyPI 后，可以马上执行下面的 uvx 命令进行服务启动和验证。

```text
uvx tobe-time-mcp
```

![img](https://pic2.zhimg.com/v2-77bead3c7e349a41b1bdaf7706111299_1440w.jpg)

## 总结

Python 提供了标准包管理机制，uvx 提供了快速初始化和运行 Python 包的能力，两者结合让 MCP 服务的分享和启动更加便捷。

