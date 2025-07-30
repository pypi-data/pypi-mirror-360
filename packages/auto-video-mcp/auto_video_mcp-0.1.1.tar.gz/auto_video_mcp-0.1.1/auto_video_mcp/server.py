"""
FastMCP服务器主程序，集成所有工具和功能
"""

import os
import sys
import logging
import asyncio
import argparse
from typing import Optional, AsyncIterator, Any
from contextlib import asynccontextmanager
from fastmcp import FastMCP

# 导入配置模块
from auto_video_mcp.utils.config import config, load_config

# 导入数据库初始化函数
from auto_video_mcp.utils.database import init_db

# 导入任务管理器
from auto_video_mcp.utils.task_manager import task_manager, start_task_manager, stop_task_manager

# 导入日志模块
from auto_video_mcp.utils.logger import logger

# 导入所有工具
from auto_video_mcp.tools import all_tools

# 定义服务器生命周期管理
@asynccontextmanager
async def lifespan(app: FastMCP) -> AsyncIterator[dict[str, Any]]:
    """服务器生命周期管理"""
    # 启动事件
    logger.info("Server starting up...")
    
    try:
        # 初始化数据库
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully")
        
        # 启动任务管理器
        logger.info("Starting task manager...")
        await start_task_manager()
        logger.info("Task manager started successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        # 严重错误，退出程序
        sys.exit(1)
    
    # 生命周期中间阶段
    yield {}
    
    # 关闭事件
    logger.info("Server shutting down...")
    
    try:
        # 停止任务管理器
        logger.info("Stopping task manager...")
        await stop_task_manager()
        logger.info("Task manager stopped successfully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

# 创建FastMCP服务器实例
mcp = FastMCP(name="一站式自动生成视频MCP服务", lifespan=lifespan)

# 注册所有工具
for tool in all_tools:
    mcp.add_tool(tool)
    logger.info(f"Registered tool: {tool.name}")


async def run_sse():
    """Run Excel MCP server in SSE mode."""
    # Assign value to EXCEL_FILES_PATH in SSE mode
    global EXCEL_FILES_PATH
    EXCEL_FILES_PATH = os.environ.get("EXCEL_FILES_PATH", "./excel_files")
    # Create directory if it doesn't exist
    os.makedirs(EXCEL_FILES_PATH, exist_ok=True)
    
    try:
        logger.info(f"Starting Excel MCP server with SSE transport (files directory: {EXCEL_FILES_PATH})")
        await mcp.run_sse_async()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        await mcp.shutdown()
    except Exception as e:
        logger.error(f"Server failed: {e}")
        raise
    finally:
        logger.info("Server shutdown complete")


def run_http(host: str, port: int, log_level: str):
    """Run Excel MCP server in HTTP mode."""
    try:
        logger.info(f"Starting Excel MCP server with HTTP transport (http://{host}:{port}")
        mcp.run(
            transport="http",
            host=host,
            port=port,
            log_level=log_level
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="飞影数字人API服务")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--host", type=str, help="服务器主机地址")
    parser.add_argument("--port", type=int, help="服务器端口")
    parser.add_argument("--log-level", type=str, choices=["debug", "info", "warning", "error", "critical"], help="日志级别")
    parser.add_argument("--transport", type=str, choices=["stdio", "http", "sse"], default="stdio", help="传输协议")
    return parser.parse_args()

def run_stdio():
    """Run feiying MCP server in stdio mode."""
    try:
        logger.info("Starting feiying MCP server with stdio transport")
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running server: {str(e)}")
        sys.exit(1)

def main():
    """主函数"""
    # 解析命令行参数
    
    args = parse_args()
    
    # 加载配置
    if args.config:
        load_config(args.config)
    
    # 获取服务器配置
    host = args.host or config.get("server_host")
    port = args.port or config.get("server_port")
    log_level = args.log_level or config.get("server_log_level")
    transport = args.transport
    
    # 设置日志级别
    if log_level:
        logging.getLogger().setLevel(getattr(logging, log_level.upper()))
    
    # 打印配置信息
    logger.info(f"Starting server with transport: {transport}")
    if transport == "http" or transport == "sse":
        logger.info(f"Server will be available at: http://{host}:{port}")
    
    # 运行服务器
    try:
        if transport == "http":
            run_http(host=host, port=port, log_level=log_level)
        elif transport == "sse":
            run_sse()
        elif transport == "stdio":
            run_stdio()
        else:
            raise ValueError("不支持的端口形式")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 