# auto_video_mcp: 一站式自动生成视频MCP服务

**一站式自动生成视频 MCP 服务** 是一个基于 [FastMCP](https://github.com/mcp-suite/fastmcp) 框架构建的强大后端服务。它不仅无缝集成了**飞影数字人**的先进 API，还整合了多种网络内容获取工具，为大语言模型（LLM）提供了一套从内容获取、声音克隆到视频创作的全链路自动化功能。

该项目利用 SQLAlchemy 2.0 进行异步数据库操作，并通过一个后台任务管理器自动更新任务状态，确保了系统的高效和稳定。

## ✨ 功能特性

- **数字人克隆**：支持通过照片或视频创建个性化的数字人形象。
- **声音克隆**：支持通过音频文件或文本创建和管理自定义声音。
- **视频创作**：支持通过文本驱动（Text-to-Video）或音频驱动（Audio-to-Video）两种方式创作数字人视频。
- **音频创作**：支持通过文本生成高质量的语音内容（Text-to-Speech）。
- **内容聚合**：内置多个内容抓取工具，支持从网站、RSS源等自动获取最新资讯。
- **文件管理**：提供文件上传接口，方便管理媒体资源。
- **状态查询**：提供任务状态、数字人列表、声音列表等多种查询功能。
- **异步任务处理**：所有耗时操作（如视频生成）均为异步处理，并自动更新任务状态。

## 🛠️ 可用工具

服务器提供以下工具，可供 LLM 或其他客户端直接调用：

### 数字人与多媒体创作工具
- **Avatar Tools (`avatar_tools`)**:
  - `create_personal_avatar_by_photo`: 通过单张照片创建个人数字人。
  - `create_personal_avatar_by_video`: 通过视频文件创建个人数字人。
- **Voice Tools (`voice_tools`)**:
  - `create_voice_by_file`: 通过音频文件克隆声音。
  - `create_voice_by_text`: 通过文本创建声音（用于声音定制）。
- **Video Creation Tools (`video_tools`)**:
  - `create_video_by_audio`: 使用指定的数字人和音频文件创作视频。
  - `create_video_by_script`: 使用指定的数字人和文本脚本创作视频。
- **Audio Creation Tools (`audio_tools`)**:
  - `create_audio_by_text`: 将文本转换为语音。
- **File Upload Tools (`upload_tools`)**:
  - `upload_file`: 上传媒体文件（音频、视频）到服务器。

### 网络与内容工具 (`web_tools`)
- `get_baidu_trending`: 获取百度热搜榜。
- `get_36kr_news`: 获取 36氪 最新资讯。
- `get_autohome_news`: 获取汽车之家最新资讯。
- `get_custom_rss`: 从指定的 RSS 源获取内容。
- `crawl_website`: 爬取指定网页的结构化内容。
- `web_search`: 执行网络搜索。

### 查询工具 (`query_tools`)
- `query_task_status`: 查询指定任务的当前状态和结果。
- `query_personal_avatars`: 查询已创建的个人数字人列表。
- `query_personal_voices`: 查询已创建的个人声音列表。
- `query_public_avatars`: 查询公共数字人列表。
- `query_public_voices`: 查询公共声音列表。
- `query_video_templates`: 查询可用的视频模板。

## 🚀 快速开始

### 1. 环境要求
- Python 3.11+
- 飞影数字人 API Token
- FireCrawl API Key (如果使用 `crawl_website` 工具)

### 2. 安装步骤

1.  **克隆仓库**:
    ```bash
    git clone https://github.com/fancyboi999/auto_video_mcp.git
    cd auto_video_mcp
    ```

2.  **创建虚拟环境并安装依赖**:
    ```bash
    # 推荐使用 uv, an extremely fast Python package installer
    uv venv
    source .venv/bin/activate
    uv pip install -e .
    ```
    如果未使用 `uv`，也可以使用 `venv`:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -e .
    ```

3.  **配置环境变量**:
    复制示例配置文件并填入您的 API Token。
    ```bash
    cp env.example .env
    ```
    编辑 `.env` 文件，至少需要设置 `FLYWORKS_API_TOKEN`。详细配置见下方“环境变量配置”部分。

### 3. 数据库迁移
在首次运行前，请执行数据库迁移以创建所需的表结构：
```bash
alembic upgrade head
```

### 4. Docker 部署

本项目提供了 Docker 支持，可以轻松部署到容器环境或 Smithery 平台。

#### 使用 Docker Compose 本地部署

1. **构建并启动容器**:
   ```bash
   docker-compose up -d
   ```

2. **查看日志**:
   ```bash
   docker-compose logs -f
   ```

3. **停止服务**:
   ```bash
   docker-compose down
   ```

#### 部署到 Smithery 平台

项目已配置好 `Dockerfile` 和 `smithery.yaml` 文件，可以直接部署到 Smithery 平台：

1. **确保已经在 Smithery 平台创建了项目**

2. **配置环境变量**:
   在 Smithery 平台的项目设置中，添加必要的环境变量，特别是 `FLYWORKS_API_TOKEN`。

3. **部署项目**:
   按照 Smithery 平台的指引，将代码推送到关联的 Git 仓库，平台会自动构建和部署。

4. **访问服务**:
   部署完成后，可以通过 Smithery 提供的 URL 访问服务。

### 5. 运行服务器与配置

本项目支持多种方式来运行和配置 FastMCP 服务器，以适应不同的开发和部署需求。

#### 环境变量配置

Docker 部署时，可以通过环境变量传递配置。以下是主要的环境变量及其说明：

**核心配置:**
- `FLYWORKS_API_TOKEN`: 飞影API令牌 (必需)。
- `FLYWORKS_API_BASE_URL`: 飞影API的基础URL。
- `FIRECRAWL_API_KEY`: FireCrawl服务的API密钥，用于`crawl_website`工具。

**工具配置:**
- `DISABLED_TOOLS`: 禁用的工具列表，以逗号分隔 (例如: `get_baidu_trending,crawl_website`)。
- `TRENDS_HUB_CUSTOM_RSS_URL`: 自定义RSS源的URL，用于`get_custom_rss`工具。

**数据库配置:**
- `DATABASE_URL`: 数据库连接URL (默认为 `sqlite+aiosqlite:///./hifly.db`)。
- `DB_ECHO`: 是否在日志中打印SQLAlchemy执行的SQL语句 (默认为 `false`)。
- `DB_POOL_SIZE`: 数据库连接池大小 (默认为 `5`)。
- `DB_MAX_OVERFLOW`: 连接池中允许的额外连接数 (默认为 `10`)。
- `DB_POOL_TIMEOUT`: 获取连接的超时时间 (秒) (默认为 `30`)。
- `DB_POOL_RECYCLE`: 连接回收时间 (秒) (默认为 `1800`)。

**服务器配置:**
- `SERVER_HOST`: 服务器主机地址 (默认为 `127.0.0.1`)。
- `SERVER_PORT`: 服务器端口 (默认为 `8000`)。
- `SERVER_PATH`: API路径前缀 (默认为 `/mcp/`)。
- `SERVER_LOG_LEVEL`: 日志级别 (默认为 `info`)。

**后台任务配置:**
- `TASK_CHECK_INTERVAL`: 任务状态检查的时间间隔 (秒) (默认为 `60`)。
- `TASK_MAX_RETRY`: 任务失败后的最大重试次数 (默认为 `3`)。

#### 命令行工具

安装后，您可以使用 `auto_video_mcp` 命令行工具来启动服务器：

```bash
# 激活虚拟环境
source .venv/bin/activate

# HTTP 模式 (默认端口 8000)
python -m auto_video_mcp.server --transport http

# 自定义主机和端口
python -m auto_video_mcp.server --transport http --host 0.0.0.0 --port 8080 

# SSE 模式
python -m auto_video_mcp.server --transport sse

# STDIO 模式 (用于 MCP 集成)
python -m auto_video_mcp.server --transport stdio
```

或者使用安装的命令行工具：

```bash
# HTTP 模式 (默认端口 8000)
auto_video_mcp --transport http

# 自定义主机和端口
auto_video_mcp --transport http --host 0.0.0.0 --port 8080 

# SSE 模式
auto_video_mcp --transport sse

# STDIO 模式 (用于 MCP 集成)
auto_video_mcp --transport stdio
```

#### 配置方式

服务器的配置项（如主机、端口等）可以通过以下三种方式设置，优先级从高到低：

1.  **命令行参数**: 启动时直接传入参数，优先级最高。
2.  **配置文件**: 通过 `--config` 参数指定一个 JSON 配置文件。
3.  **环境变量**: 从 `.env` 文件中加载，通常用于存放敏感信息如 API Token。

#### 传输协议 (Transport)

FastMCP 支持多种传输协议，您可以通过不同的子命令选择：

-   **`http` (默认)**: 启动一个基于 Streamable HTTP 的 Web 服务器。这是推荐用于 Web 服务部署的方式。
    ```bash
    # 使用默认配置 (http://127.0.0.1:8000)
    python -m auto_video_mcp.server --transport http

    # 自定义主机和端口
    python -m auto_video_mcp.server --transport http --host 0.0.0.0 --port 8080
    ```

-   **`sse`**: 启动一个基于 Server-Sent Events (SSE) 的服务器。这是旧版协议，新项目推荐使用 `http`。
    ```bash
    python -m auto_video_mcp.server --transport sse
    ```

-   **`stdio`**: 启动一个基于标准输入/输出的服务器。这主要用于与 MCP 客户端集成。
    ```bash
    python -m auto_video_mcp.server --transport stdio
    ```

#### 命令行参数

您可以使用以下参数来配置服务器的运行：

-   `--transport <type>`: 传输协议类型，可选 `http`, `sse`, `stdio`。
-   `--host <address>`: 服务器监听的主机地址 (默认为 `127.0.0.1`)。
-   `--port <number>`: 服务器监听的端口 (默认为 `8000`)。
-   `--path <url_path>`: HTTP 模式下的 URL 路径 (默认为 `/mcp/`)。
-   `--log-level <level>`: 设置日志级别 (`debug`, `info`, `warning`, `error`, `critical`)。
-   `--config <file>`: 指定配置文件路径。

#### 客户端连接配置

##### Cursor IDE 集成

Cursor IDE 支持通过 MCP 协议与飞影数字人服务器集成。有两种主要的连接方式：

**方式一：通过 `stdio` (标准输入/输出)**

这是最直接的集成方式，Cursor 会在需要时自动启动和停止 MCP 服务器进程。

1.  编辑 Cursor 的 MCP 配置文件 (`~/.cursor/mcp.json`):

    ```json
    {
      "mcpServers": {
        "auto_video_mcp": {
          "command": "uvx",
          "args": ["auto_video_mcp", "--transport", "stdio"],
          "env": {
            "FLYWORKS_API_TOKEN": "你的API令牌"
          }
        }
      }
    }
    ```

2.  确保 `auto_video_mcp` 已经安装在您的 Python 环境中。

3.  在 Cursor 中选择 "auto_video_mcp" 作为 MCP 服务器。

**方式二：通过 `http` 连接**

如果您已经手动启动了 MCP 服务器（例如，在本地或 Docker 中运行），您可以通过 HTTP 连接到它。

1.  首先，确保服务器正在运行。例如：
    ```bash
    python -m auto_video_mcp.server --transport http --host 127.0.0.1 --port 8000
    ```

2.  编辑 Cursor 的 MCP 配置文件 (`~/.cursor/mcp.json`)，添加以下配置：

    ```json
    {
      "mcpServers": {
        "auto_video_mcp_http": {
          "transport": "http",
          "url": "http://127.0.0.1:8000/mcp/"
        }
      }
    }
    ```
    > **注意**:
    > - `url` 中的路径 (`/mcp/`) 需要与服务器配置的 `SERVER_PATH` 环境变量保持一致。
    > - 如果服务器运行在不同的主机或端口，请相应地修改 `url`。

3.  在 Cursor 中选择 "auto_video_mcp_http" 作为 MCP 服务器。

##### 远程连接 (HTTP)

如果您需要将服务部署为网络服务，可以使用 HTTP 连接。

1.  **启动服务器**:
    ```bash
    python -m auto_video_mcp.server --transport http --host 0.0.0.0 --port 8000
    ```

2.  **配置客户端**:
    在客户端的配置文件中，添加一个指向您服务器 URL 的条目。

    ```json
    {
      "mcpServers": {
        "auto_video_mcp-remote": {
          "transport": "http",
          "url": "http://your-server-ip:8000/mcp/"
        }
      }
    }
    ```
    > **注意**: 请将 `your-server-ip` 替换为运行服务器的机器的实际 IP 地址或域名。

完成配置并重启客户端后，即可连接到飞影数字人 MCP 服务器。

## ⚙️ 项目结构

```
auto_video_mcp/
├── auto_video_mcp/     # Python 包目录
│   ├── __init__.py  # 包初始化文件
│   └── server.py    # 服务器实现
│   ├── utils/       # 工具类目录
│   │   ├── config.py       # 配置管理模块
│   │   ├── database.py     # 数据库会话管理
│   │   ├── models.py       # SQLAlchemy 数据库模型定义
│   │   ├── api_client.py   # 飞影 API 客户端封装
│   │   └── task_manager.py # 后台任务状态更新管理器
│   └── tools/       # MCP 工具目录
│       ├── avatar_tools.py  # 数字人相关工具
│       ├── voice_tools.py   # 声音相关工具
│       ├── video_tools.py   # 视频相关工具
│       ├── audio_tools.py   # 音频相关工具
│       ├── upload_tools.py  # 上传相关工具
│       └── query_tools.py   # 查询相关工具
├── migrations/      # Alembic 数据库迁移脚本
├── pyproject.toml   # 项目元数据和构建配置
├── requirements.txt # 项目依赖
└── README.md        # 项目文档
```

## 📄 许可证

本项目采用 [MIT License](LICENSE) 授权。

---

如有任何问题，欢迎提交 Issue 或联系项目维护者。
