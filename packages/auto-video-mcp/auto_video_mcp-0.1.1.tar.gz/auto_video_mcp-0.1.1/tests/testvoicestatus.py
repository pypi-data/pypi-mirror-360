import asyncio
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_client import HiFlyClient
from tools.voice_tools import query_voice_task_tool

# 配置日志
logging.basicConfig(level=logging.INFO)

async def test_query_voice_task():
    """测试查询声音克隆任务状态"""
    response = await query_voice_task_tool(
        task_id="IQwWBZARey1TfTC9kCcdvw"  # 替换为实际的任务ID
    )
    print(f"声音克隆任务状态: {response}")

if __name__ == "__main__":
    asyncio.run(test_query_voice_task()) 