import asyncio
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_client import HiFlyClient
from tools.avatar_tools import create_avatar_by_image_tool, create_avatar_by_video_tool, query_avatar_task_tool

# 测试音频生成任务状态

client = HiFlyClient()
async def test_create_avatar_by_video():
    response = await create_avatar_by_video_tool(
        title="测试数字人123",
        video_url="https://wechat-luobo.oss-cn-shanghai.aliyuncs.com/converted_media/fa6bd8c5-850f-4728-b681-3bb41e41f76c.mp4",
    )
    print(f"音频生成任务状态: {response}")

async def test_create_avatar_by_image():
    response = await create_avatar_by_image_tool(
        title="测试\数字人图片上传",
        image_url="https://wechat-luobo.oss-cn-shanghai.aliyuncs.com/static/uploads/preview_c970a538565911f0a7a200163e7f9c5a.mp4.jpg",
    )
    print(f"音频生成任务状态: {response}")

async def test_query_audio_task():
    response = await query_avatar_task_tool(
        task_id="mGZ9eqUcFfqmnf3i"
    )
    print(f"音频生成任务状态: {response}")

if __name__ == "__main__":
    asyncio.run(test_query_audio_task())