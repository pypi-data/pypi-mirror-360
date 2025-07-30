import asyncio
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_client import HiFlyClient
from tools.audio_tools import create_audio_by_tts_tool, query_audio_task_tool

# 测试音频生成任务状态

client = HiFlyClient()
async def test_audio_task():
    response = await create_audio_by_tts_tool(
        text="你好，我是飞影数字人，很高兴认识你。",
        voice="ZlOFcVt9CmXCFHwV8wvKUA",
        title="测试音频",
        # rate="1.0",
        # volume="1.0",
        # pitch="1.0"
    )
    print(f"音频生成任务状态: {response}")

async def test_query_audio_task():
    response = await query_audio_task_tool(
        task_id="jeaDl3YtFLR3uO2nuiAz1A"
    )
    print(f"音频生成任务状态: {response}")

if __name__ == "__main__":
    asyncio.run(test_audio_task())