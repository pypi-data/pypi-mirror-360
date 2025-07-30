import logging
import datetime
from typing import Annotated, Dict, Any, Optional, List
from fastmcp.tools import Tool
from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from sqlalchemy.orm import selectinload

from auto_video_mcp.utils.api_client import HiFlyClient
from auto_video_mcp.utils.database import get_db
from auto_video_mcp.utils.models import Task, Video, Avatar, Voice

# 配置日志
logger = logging.getLogger(__name__)

# 创建全局客户端实例
client = HiFlyClient()

async def create_video_by_audio_tool(
    avatar: Annotated[str, Field(description="数字人ID，可以是公共数字人ID或自己克隆的数字人ID")],
    audio_url: Annotated[Optional[str], Field(description="音频URL，与file_id二选一必填")] = None,
    file_id: Annotated[Optional[str], Field(description="上传的音频文件ID，与audio_url二选一必填")] = None,
    title: Annotated[Optional[str], Field(description="视频标题，如不提供则使用\"未命名\"")] = None,
    user_id: Annotated[Optional[str], Field(description="用户ID，用于关联视频所有者，如不提供则使用默认用户")] = "default",
) -> Dict[str, Any]:
    # 参数验证
    if not avatar:
        raise ValueError("数字人ID不能为空")
    
    if not audio_url and not file_id:
        raise ValueError("audio_url和file_id必须提供一个")
    
    if audio_url and file_id:
        raise ValueError("audio_url和file_id只能提供一个")
    
    # 获取数据库会话
    async for db in get_db():
        try:
            # 使用全局客户端实例
            
            # 调用API创建视频
            response = await client.create_video_by_audio(
                avatar=avatar,
                audio_url=audio_url,
                file_id=file_id,
                title=title or "未命名"
            )
            
            # 获取任务ID
            task_id = response.get("task_id")
            request_id = response.get("request_id")
            
            if not task_id:
                raise ValueError("API返回的任务ID为空")
            
            # 创建任务记录
            task = Task(
                task_id=task_id,
                task_type=1,  # 1表示视频创作
                status=1,  # 1表示等待中
                title=title or "未命名",
                request_id=request_id,
                user_id=user_id or "default",
            )
            
            # 创建视频记录
            video = Video(
                title=title or "未命名",
                task_id=task_id,
                avatar_id=avatar,
                user_id=user_id or "default",
            )
            
            # 保存到数据库
            db.add(task)
            db.add(video)
            await db.commit()
            
            return {
                "task_id": task_id,
                "status": "waiting",
                "message": "视频创作任务已提交，请稍后查询任务状态"
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"创建视频失败: {str(e)}")
            raise ValueError(f"创建视频失败: {str(e)}")

async def create_video_by_tts_tool(
    avatar: Annotated[str, Field(description="数字人ID，可以是公共数字人ID或自己克隆的数字人ID")],
    voice: Annotated[str, Field(description="声音ID，可以是公共声音ID或自己克隆的声音ID")],
    text: Annotated[str, Field(description="文本内容")],
    title: Annotated[Optional[str], Field(description="视频标题，如不提供则使用\"未命名\"")] = None,
    st_show: Annotated[int, Field(description="是否显示字幕，1:显示，0:不显示，默认不显示")] = 0,
    st_primary_color: Annotated[Optional[str], Field(description="字幕主要颜色，如\"#FFFFFF\"")] = None,
    st_outline_color: Annotated[Optional[str], Field(description="字幕轮廓颜色，如\"#000000\"")] = None,
    st_font_name: Annotated[Optional[str], Field(description="字幕字体名称")] = None,
    st_font_size: Annotated[Optional[int], Field(description="字幕字体大小")] = None,
    st_pos_x: Annotated[Optional[int], Field(description="字幕X坐标")] = None,
    st_pos_y: Annotated[Optional[int], Field(description="字幕Y坐标")] = None,
    st_width: Annotated[Optional[int], Field(description="字幕宽度")] = None,
    st_height: Annotated[Optional[int], Field(description="字幕高度")] = None,
    user_id: Annotated[Optional[str], Field(description="用户ID，用于关联视频所有者，如不提供则使用默认用户")] = "default",
) -> Dict[str, Any]:
    # 参数验证
    if not avatar:
        raise ValueError("数字人ID不能为空")
    
    if not voice:
        raise ValueError("声音ID不能为空")
    
    if not text:
        raise ValueError("文本内容不能为空")
    
    # 获取数据库会话
    async for db in get_db():
        try:
            # 使用全局客户端实例
            
            # 准备字幕参数
            subtitle_params = {}
            if st_show == 1:
                if st_primary_color:
                    subtitle_params["st_primary_color"] = st_primary_color
                if st_outline_color:
                    subtitle_params["st_outline_color"] = st_outline_color
                if st_font_name:
                    subtitle_params["st_font_name"] = st_font_name
                if st_font_size:
                    subtitle_params["st_font_size"] = st_font_size
                if st_pos_x is not None:
                    subtitle_params["st_pos_x"] = st_pos_x
                if st_pos_y is not None:
                    subtitle_params["st_pos_y"] = st_pos_y
                if st_width:
                    subtitle_params["st_width"] = st_width
                if st_height:
                    subtitle_params["st_height"] = st_height
            
            # 调用API创建视频
            response = await client.create_video_by_tts(
                avatar=avatar,
                voice=voice,
                text=text,
                title=title or "未命名",
                st_show=st_show,
                **subtitle_params
            )
            
            # 获取任务ID
            task_id = response.get("task_id")
            request_id = response.get("request_id")
            
            if not task_id:
                raise ValueError("API返回的任务ID为空")
            
            # 创建任务记录
            task = Task(
                task_id=task_id,
                task_type=1,  # 1表示视频创作
                status=1,  # 1表示等待中
                title=title or "未命名",
                request_id=request_id,
                user_id=user_id or "default",
            )
            
            # 创建视频记录
            video = Video(
                title=title or "未命名",
                task_id=task_id,
                avatar_id=avatar,
                voice_id=voice,
                user_id=user_id or "default",
            )
            
            # 保存到数据库
            db.add(task)
            db.add(video)
            await db.commit()
            
            return {
                "task_id": task_id,
                "status": "waiting",
                "message": "视频创作任务已提交，请稍后查询任务状态"
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"创建视频失败: {str(e)}")
            raise ValueError(f"创建视频失败: {str(e)}")

async def query_video_task_tool(
    task_id: Annotated[str, Field(description="任务ID")],
) -> Dict[str, Any]:

    # 获取数据库会话
    async for db in get_db():
        try:
            # 从数据库查询任务，预加载videos关系
            query_result = await db.execute(
                select(Task).where(Task.task_id == task_id).options(selectinload(Task.videos))
            )
            task = query_result.scalars().first()
            
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            # 如果任务已经完成或失败，直接返回数据库中的状态
            if task.status in [3, 4]:  # 3:完成 4:失败
                if task.status == 3 and task.videos:
                    video = task.videos[0]
                    return {
                        "task_id": task_id,
                        "status": "completed",
                        "title": video.title,
                        "video_url": video.video_url,
                        "duration": video.duration,
                        "avatar_id": video.avatar_id,
                        "voice_id": video.voice_id
                    }
                elif task.status == 4:
                    return {
                        "task_id": task_id,
                        "status": "failed",
                        "message": task.message,
                        "code": task.code
                    }
            
            # 如果任务还在进行中，调用API查询最新状态
            response = await client.get_video_task(task_id)
            
            # 获取状态
            status = response.get("status")
            video_url = response.get("video_Url")
            duration = response.get("duration", 0)
            
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
            
            # 如果任务完成，更新视频记录
            if status == 3 and video_url:  # 3表示完成
                # 查询视频记录
                result = await db.execute(select(Video).where(Video.task_id == task_id))
                video = result.scalars().first()
                
                if video:
                    # 更新视频记录
                    video.video_url = video_url
                    video.duration = duration
                    db.add(video)
            
            # 提交更改
            await db.commit()
            
            # 返回结果
            status_map = {1: "waiting", 2: "processing", 3: "completed", 4: "failed"}
            result = {
                "task_id": task_id,
                "status": status_map.get(status, "unknown")
            }
            
            if status == 3 and video_url:
                result["video_url"] = video_url
                result["duration"] = duration
            elif status == 4:
                result["message"] = response.get("message", "")
                result["code"] = response.get("code", 0)
            
            return result
            
        except Exception as e:
            await db.rollback()
            logger.error(f"查询视频任务状态失败: {str(e)}")
            raise ValueError(f"查询视频任务状态失败: {str(e)}")

# 创建FastMCP工具
create_video_by_audio = Tool.from_function(
    create_video_by_audio_tool,
    name="create_video_by_audio",
    description="通过音频创建视频（音频驱动视频创作），支持指定数字人ID和音频文件",
    tags={"video", "creation", "audio"}
)

create_video_by_tts = Tool.from_function(
    create_video_by_tts_tool,
    name="create_video_by_tts",
    description="通过文本创建视频（文本驱动视频创作），支持指定数字人ID、声音ID和文本内容",
    tags={"video", "creation", "tts"}
)

query_video_task = Tool.from_function(
    query_video_task_tool,
    name="query_video_task",
    description="查询视频创作任务状态，获取任务进度和结果",
    tags={"video", "task", "query"}
)

# 导出工具列表，用于注册到FastMCP服务器
video_tools = [
    create_video_by_audio,
    create_video_by_tts,
    query_video_task
] 