"""
声音克隆相关的FastMCP工具，包括声音创建、修改和查询功能
"""

from pydantic import Field
import os
import logging
import asyncio
from typing import Annotated, Dict, Any, Optional, List, Union
from fastmcp.tools import Tool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
import datetime
from sqlalchemy.orm import selectinload

from auto_video_mcp.utils.api_client import HiFlyClient
from auto_video_mcp.utils.database import get_db
from auto_video_mcp.utils.models import Task, Voice

# 配置日志
logger = logging.getLogger(__name__)

# 创建全局客户端实例
client = HiFlyClient()

async def create_voice_tool(
    title: Annotated[str, Field(description="声音名称，不超过20个字")],
    voice_type: Annotated[int, Field(description="声音类型，8:声音克隆基础版v2，目前只支持8")] = 8,
    audio_url: Annotated[Optional[str], Field(description="声音文件URL，支持mp3、m4a、wav格式，20M以内，时长范围5秒～3分钟。与file_path二选一必填")] = None,
    file_path: Annotated[Optional[str], Field(description="本地音频文件路径，与audio_url二选一必填，系统会自动上传该文件")] = None,
    user_id: Annotated[Optional[str], Field(description="用户ID，用于关联声音所有者，如不提供则使用默认用户")] = "default",
) -> Dict[str, Any]:
    # 参数验证
    if not audio_url and not file_path:
        raise ValueError("audio_url和file_path必须提供一个")
    
    if audio_url and file_path:
        raise ValueError("audio_url和file_path只能提供一个")
    
    # 获取数据库会话
    async for db in get_db():
        try:
            # 使用全局客户端实例
            file_id = None
            
            # 如果提供了本地文件路径，先上传文件
            if file_path:
                if not os.path.exists(file_path):
                    raise ValueError(f"文件不存在: {file_path}")
                
                logger.info(f"开始上传文件: {file_path}")
                success, file_id = await client.upload_file(file_path)
                if not success or not file_id:
                    raise ValueError("文件上传失败")
                logger.info(f"文件上传成功，文件ID: {file_id}")
            
            # 调用API创建声音
            if file_id:
                response = await client.create_voice(title=title, voice_type=voice_type, file_id=file_id)
            else:
                response = await client.create_voice(title=title, voice_type=voice_type, audio_url=audio_url)
            
            # 获取任务ID
            task_id = response.get("task_id")
            request_id = response.get("request_id")
            
            if not task_id:
                raise ValueError("API返回的任务ID为空")
            
            # 创建任务记录
            task = Task(
                task_id=task_id,
                task_type=3,  # 3表示声音克隆
                status=1,  # 1表示等待中
                title=title,
                request_id=request_id,
                user_id=user_id or "default",
            )
            
            # 创建声音记录
            voice = Voice(
                title=title,
                voice_type=voice_type,
                task_id=task_id,
                rate="1.0",
                volume="1.0",
                pitch="1.0",
                user_id=user_id or "default",
            )
            
            # 保存到数据库
            db.add(task)
            db.add(voice)
            await db.commit()
            
            return {
                "task_id": task_id,
                "status": "waiting",
                "message": "声音克隆任务已提交，请稍后查询任务状态"
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"创建声音失败: {str(e)}")
            raise ValueError(f"创建声音失败: {str(e)}")

async def edit_voice_tool(
    voice_id: Annotated[str, Field(description="声音ID")],
    rate: Annotated[str, Field(description="语速，值为0.5和2.0之间，默认1.0")] = "1.0",
    volume: Annotated[str, Field(description="音量，值为0.1和2.0之间，默认1.0")] = "1.0",
    pitch: Annotated[str, Field(description="语调，值为0.1和2.0之间，默认1.0")] = "1.0",
    user_id: Annotated[Optional[str], Field(description="用户ID，用于验证声音所有权，如不提供则不验证")] = None,
) -> Dict[str, Any]:
    # 参数验证
    if not voice_id:
        raise ValueError("声音ID不能为空")
    
    # 验证语速、音量和语调
    try:
        rate_float = float(rate)
        if not (0.5 <= rate_float <= 2.0):
            raise ValueError("语速必须在0.5和2.0之间")
    except ValueError:
        raise ValueError("语速必须是有效的数字")
    
    try:
        volume_float = float(volume)
        if not (0.1 <= volume_float <= 2.0):
            raise ValueError("音量必须在0.1和2.0之间")
    except ValueError:
        raise ValueError("音量必须是有效的数字")
    
    try:
        pitch_float = float(pitch)
        if not (0.1 <= pitch_float <= 2.0):
            raise ValueError("语调必须在0.1和2.0之间")
    except ValueError:
        raise ValueError("语调必须是有效的数字")
    
    # 获取数据库会话
    async for db in get_db():
        try:
            # 查询声音是否存在
            result = await db.execute(select(Voice).where(Voice.voice_id == voice_id))
            voice = result.scalars().first()
            
            # 如果声音存在且指定了用户ID，验证所有权
            if voice and user_id and voice.user_id != user_id:
                raise ValueError("您没有权限修改此声音")
            
            # 使用全局客户端实例
            
            # 调用API修改声音参数
            response = await client.edit_voice(
                voice=voice_id,
                rate=rate,
                volume=volume,
                pitch=pitch
            )
            
            # 如果声音存在于数据库，更新参数
            if voice:
                voice.rate = rate
                voice.volume = volume
                voice.pitch = pitch
                voice.updated_at = datetime.datetime.utcnow()
                await db.commit()
            
            return {
                "voice_id": voice_id,
                "rate": rate,
                "volume": volume,
                "pitch": pitch,
                "message": "声音参数修改成功"
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"修改声音参数失败: {str(e)}")
            raise ValueError(f"修改声音参数失败: {str(e)}")

async def list_voices_tool(
    page: Annotated[int, Field(description="页码，默认1")] = 1,
    size: Annotated[int, Field(description="每页数量，默认20")] = 20,
    kind: Annotated[int, Field(description="声音分类，1:自己克隆的，2:公共声音，默认1")] = 1,
    user_id: Annotated[Optional[str], Field(description="用户ID，用于查询特定用户的声音，如不提供则使用默认用户")] = "default",
) -> Dict[str, Any]:
    """
    查询声音列表。
    
    Args:
        page: 页码，默认1
        size: 每页数量，默认20
        kind: 声音分类，1:自己克隆的，2:公共声音，默认1
        user_id: 用户ID，用于查询特定用户的声音，如不提供则使用默认用户
        
    Returns:
        包含声音列表的结果
    """
    try:
        # 使用全局客户端实例
        
        # 调用API查询声音列表
        response = await client.get_voice_list(page=page, size=size, kind=kind)
        
        # 获取声音列表
        voices = response.get("data", [])
        
        # 如果是查询自己克隆的声音，同步到数据库
        if kind == 1 and user_id:
            async for db in get_db():
                try:
                    for voice_data in voices:
                        voice_id = voice_data.get("voice")
                        if not voice_id:
                            continue
                            
                        # 检查声音是否已存在
                        result = await db.execute(select(Voice).where(Voice.voice_id == voice_id))
                        existing_voice = result.scalars().first()
                        
                        if not existing_voice:
                            # 创建声音记录
                            voice = Voice(
                                voice_id=voice_id,
                                title=voice_data.get("title", "未命名"),
                                voice_type=voice_data.get("type", 8),
                                rate=voice_data.get("rate", "1.0"),
                                volume=voice_data.get("volume", "1.0"),
                                pitch=voice_data.get("pitch", "1.0"),
                                demo_url=voice_data.get("demo_url"),
                                user_id=user_id or "default"
                            )
                            db.add(voice)
                        else:
                            # 更新声音记录
                            existing_voice.title = voice_data.get("title", existing_voice.title)
                            existing_voice.voice_type = voice_data.get("type", existing_voice.voice_type)
                            existing_voice.rate = voice_data.get("rate", existing_voice.rate)
                            existing_voice.volume = voice_data.get("volume", existing_voice.volume)
                            existing_voice.pitch = voice_data.get("pitch", existing_voice.pitch)
                            existing_voice.demo_url = voice_data.get("demo_url", existing_voice.demo_url)
                            existing_voice.updated_at = datetime.datetime.utcnow()
                    
                    await db.commit()
                except Exception as e:
                    await db.rollback()
                    logger.error(f"同步声音数据到数据库失败: {str(e)}")
        
        # 返回结果
        return {
            "voices": voices,
            "page": page,
            "size": size,
            "kind": kind
        }
        
    except Exception as e:
        logger.error(f"查询声音列表失败: {str(e)}")
        raise ValueError(f"查询声音列表失败: {str(e)}")

async def query_voice_task_tool(
    task_id: Annotated[str, Field(description="任务ID")],
) -> Dict[str, Any]:
    # 获取数据库会话
    async for db in get_db():
        try:
            # 从数据库查询任务，预加载voices关系
            result = await db.execute(
                select(Task).where(Task.task_id == task_id).options(selectinload(Task.voices))
            )
            task = result.scalars().first()
            
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            # 如果任务已经完成或失败，直接返回数据库中的状态
            if task.status in [3, 4]:  # 3:完成 4:失败
                if task.status == 3 and task.voices:
                    voice = task.voices[0]
                    return {
                        "task_id": task_id,
                        "status": "completed",
                        "voice_id": voice.voice_id,
                        "title": voice.title,
                        "demo_url": voice.demo_url,
                        "rate": voice.rate,
                        "volume": voice.volume,
                        "pitch": voice.pitch
                    }
                elif task.status == 4:
                    return {
                        "task_id": task_id,
                        "status": "failed",
                        "message": task.message,
                        "code": task.code
                    }
            
            # 如果任务还在进行中，调用API查询最新状态
            response = await client.get_voice_task(task_id)
            
            # 获取状态
            status = response.get("status")
            voice_id = response.get("voice")
            demo_url = response.get("demo_url")
            
            # 更新数据库中的任务状态
            await db.execute(
                update(Task)
                .where(Task.task_id == task_id)
                .values(
                    status=status,
                    message=response.get("message", ""),
                    code=response.get("code", 0),
                    updated_at=datetime.datetime.utcnow()
                )
            )
            
            # 如果任务完成，更新声音记录
            if status == 3 and voice_id:  # 3表示完成
                # 查询声音记录
                result = await db.execute(select(Voice).where(Voice.task_id == task_id))
                voice = result.scalars().first()
                
                if voice:
                    # 更新声音记录
                    voice.voice_id = voice_id
                    voice.demo_url = demo_url
                    db.add(voice)
                else:
                    # 创建声音记录（理论上不应该走到这里，因为创建任务时已创建声音记录）
                    voice = Voice(
                        voice_id=voice_id,
                        title=task.title,
                        voice_type=8,  # 默认为声音克隆基础版v2
                        task_id=task_id,
                        demo_url=demo_url,
                        user_id=task.user_id
                    )
                    db.add(voice)
            
            # 提交更改
            await db.commit()
            
            # 返回结果
            status_map = {1: "waiting", 2: "processing", 3: "completed", 4: "failed"}
            result = {
                "task_id": task_id,
                "status": status_map.get(status, "unknown")
            }
            
            if status == 3 and voice_id:
                result["voice_id"] = voice_id
                result["title"] = task.title
                result["demo_url"] = demo_url
            elif status == 4:
                result["message"] = response.get("message", "")
                result["code"] = response.get("code", 0)
            
            return result
            
        except Exception as e:
            await db.rollback()
            logger.error(f"查询声音克隆任务状态失败: {str(e)}")
            raise ValueError(f"查询声音克隆任务状态失败: {str(e)}")

# 创建FastMCP工具
create_voice = Tool.from_function(
    create_voice_tool,
    name="create_voice",
    description="创建克隆声音，支持上传本地音频文件或提供音频URL",
    tags={"voice", "creation", "clone"}
)

edit_voice = Tool.from_function(
    edit_voice_tool,
    name="edit_voice",
    description="修改声音参数，包括语速、音量和语调",
    tags={"voice", "edit", "parameters"}
)

list_voices = Tool.from_function(
    list_voices_tool,
    name="list_voices",
    description="查询声音列表，包括自己克隆的声音和公共声音",
    tags={"voice", "list", "query"}
)

query_voice_task = Tool.from_function(
    query_voice_task_tool,
    name="query_voice_task",
    description="查询声音克隆任务状态，获取任务进度和结果",
    tags={"voice", "task", "query"}
)

# 导出工具列表，用于注册到FastMCP服务器
voice_tools = [
    create_voice,
    edit_voice,
    list_voices,
    query_voice_task
]

# 应用退出时关闭客户端
import atexit
import asyncio

def close_client():
    loop = asyncio.get_event_loop()
    if not loop.is_closed():
        loop.run_until_complete(client.close())

atexit.register(close_client) 