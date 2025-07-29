# MMDev - 制造云开发者平台

MMDev 是一个用于制造云开发的开发者平台，提供元数据服务和工具集成，帮助开发者快速获取代码元数据和异常编码。

## 功能特性

- **代码元数据服务**: 根据项目和代码路径获取业务模块、业务对象、代码类型等信息。
- **异常编码服务**: 根据项目、业务模块、业务对象和异常内容生成异常编码。
- **开发工具集成**: 提供代码生成规则和优化规则的工具支持。

## 环境要求

- Python 版本: 3.13 或更高
- 依赖库: `fastmcp`, `httpx`

## 安装步骤
1. 安装 Python 3.13 或更高版本。
2. 安装Python包管理器 uv
    ```bash
    pip install uv
    ```
    验证安装‌
    ```bash
    uv --version
    ```

3. 克隆项目到本地:
   ```bash
   git clone https://github.com/ggoop/mmdev.git
   cd mmdev
   ```
4. 安装依赖:
    ```bash
    # With uv (recommended)
    uv sync
    ```
5. 启动服务:
    ```bash
    uv run main.py
    ```
## mcp 配置
```json
    {
        "mcpServers": {
            "aaddoopp/mmdev": {
                "command": "uvx",
                "args": [
                    "yonyou-mm-dev-mcp@latest"
                ],
                "env": {
                    "server": "https://xxxx"
                }
            }
        }
    }
```