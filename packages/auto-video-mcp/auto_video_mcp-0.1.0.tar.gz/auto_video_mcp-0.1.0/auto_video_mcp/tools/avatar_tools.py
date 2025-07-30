"""
数字人克隆相关的FastMCP工具，包括视频数字人创建、图片数字人创建和查询功能
"""

import os
import logging
import asyncio
from typing import Annotated, Dict, Any, Optional, List, Union
from fastmcp.tools import Tool
from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
import datetime
from sqlalchemy.orm import selectinload

from auto_video_mcp.utils.api_client import HiFlyClient
from auto_video_mcp.utils.database import get_db
from auto_video_mcp.utils.models import Task, Avatar

# 配置日志
logger = logging.getLogger(__name__)

# 创建全局客户端实例
client = HiFlyClient()

async def create_avatar_by_video_tool(
    title: Annotated[str, Field(description="数字人名称，不超过20个字")],
    video_url: Annotated[Optional[str], Field(description="视频URL地址，与file_path二选一必填，支持mp4、mov格式且使用h264编码，500MB以内，分辨率范围360p～4K，时长范围5秒～30分钟")] = None,
    file_path: Annotated[Optional[str], Field(description="本地视频文件路径，与video_url二选一必填，系统会自动上传该文件")] = None,
    user_id: Annotated[Optional[str], Field(description="用户ID，用于关联数字人所有者，如不提供则使用默认用户")] = "default",
) -> Dict[str, Any]:
    if not video_url and not file_path:
        raise ValueError("video_url和file_path必须提供一个")
    
    if video_url and file_path:
        raise ValueError("video_url和file_path只能提供一个")
    
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
            
            # 调用API创建数字人
            if file_id:
                response = await client.create_avatar_by_video(title=title, file_id=file_id)
            else:
                response = await client.create_avatar_by_video(title=title, video_url=video_url)
            
            # 获取任务ID
            task_id = response.get("task_id")
            request_id = response.get("request_id")
            
            if not task_id:
                raise ValueError("API返回的任务ID为空")
            
            # 创建任务记录
            task = Task(
                task_id=task_id,
                task_type=2,  # 2表示数字人克隆
                status=1,  # 1表示等待中
                title=title,
                request_id=request_id,
                user_id=user_id or "default",
            )
            avatar = Avatar(
                title=title,
                kind=1,  # 1表示自己克隆的
                task_id=task_id,
                user_id=user_id or "default",
            )
            # 保存到数据库
            db.add(task)
            db.add(avatar)
            await db.commit()
            
            return {
                "task_id": task_id,
                "status": "waiting",
                "message": "数字人克隆任务已提交，请稍后查询任务状态"
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"创建数字人失败: {str(e)}")
            raise ValueError(f"创建数字人失败: {str(e)}")

async def create_avatar_by_image_tool(
    title: Annotated[str, Field(description="数字人名称，不超过20个字")],
    image_url: Annotated[Optional[str], Field(description="图片URL地址，与file_path二选一必填")] = None,
    file_path: Annotated[Optional[str], Field(description="本地图片文件路径，与image_url二选一必填，系统会自动上传该文件")] = None,
    model: Annotated[int, Field(description="模型类型，1:视频2.0，2:视频2.1，默认2")] = 2,
    user_id: Annotated[Optional[str], Field(description="用户ID，用于关联数字人所有者，如不提供则使用默认用户")] = "default",
) -> Dict[str, Any]:
    if not image_url and not file_path:
        raise ValueError("image_url和file_path必须提供一个")
    
    if image_url and file_path:
        raise ValueError("image_url和file_path只能提供一个")
    
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
            
            # 调用API创建数字人
            if file_id:
                response = await client.create_avatar_by_image(title=title, file_id=file_id, model=model)
            else:
                response = await client.create_avatar_by_image(title=title, image_url=image_url, model=model)
            
            # 获取任务ID
            task_id = response.get("task_id")
            request_id = response.get("request_id")
            
            if not task_id:
                raise ValueError("API返回的任务ID为空")
            
            # 创建任务记录
            task = Task(
                task_id=task_id,
                task_type=2,  # 2表示数字人克隆
                status=1,  # 1表示等待中
                title=title,
                request_id=request_id,
                user_id=user_id or "default",
            )
            # avatar
            avatar = Avatar(
                title=title,
                kind=1,  # 1表示自己克隆的
                task_id=task_id,
                user_id=user_id or "default",
            )
            # 保存到数据库
            db.add(task)
            db.add(avatar)
            await db.commit()
            
            return {
                "task_id": task_id,
                "status": "waiting",
                "message": "数字人克隆任务已提交，请稍后查询任务状态"
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"创建数字人失败: {str(e)}")
            raise ValueError(f"创建数字人失败: {str(e)}")

async def query_avatar_task_tool(
    task_id: Annotated[str, Field(description="任务ID")],
) -> Dict[str, Any]:

    async for db in get_db():
        try:
            # 从数据库查询任务，预加载avatars关系
            result = await db.execute(
                select(Task).where(Task.task_id == task_id).options(selectinload(Task.avatars))
            )
            task = result.scalars().first()
            
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            # 使用全局客户端实例
            
            # 调用API查询最新状态
            response = await client.get_avatar_task(task_id)
            
            # 获取状态
            status = response.get("status")
            avatar_id = response.get("avatar")
            message = response.get("message", "")
            code = response.get("code", 0)
            
            # 更新数据库中的任务状态
            await db.execute(
                update(Task)
                .where(Task.task_id == task_id)
                .values(
                    status=status,
                    message=message,
                    code=code,
                    updated_at=datetime.datetime.utcnow()
                )
            )
            
            # 获取或更新数字人记录
            if avatar_id:
                result = await db.execute(select(Avatar).where(Avatar.task_id == task_id))
                avatar = result.scalars().first()
                
                # 如果任务完成，更新数字人记录
                if status == 3 and avatar:  # 3表示完成
                    avatar.avatar_id = avatar_id
                    db.add(avatar)
            
            # 提交更改
            await db.commit()
            
            # 返回结果
            status_map = {1: "waiting", 2: "processing", 3: "completed", 4: "failed"}
            result = {
                "task_id": task_id,
                "status": status_map.get(status, "unknown")
            }
            
            if status == 3 and avatar_id:
                result["avatar_id"] = avatar_id
                result["title"] = task.title
            elif status == 4:
                result["message"] = message
                result["code"] = code
            
            return result
            
        except Exception as e:
            await db.rollback()
            logger.error(f"查询数字人克隆任务状态失败: {str(e)}")
            raise ValueError(f"查询数字人克隆任务状态失败: {str(e)}")

async def list_public_avatars_tool(
    page: Annotated[int, Field(description="页码，默认1")],
    size: Annotated[int, Field(description="每页数量，默认20")],
    kind: Annotated[int, Field(description="数字人分类，2:公共数字人，默认2")],
) -> Dict[str, Any]:
    try:
        # 使用全局客户端实例
        logger.info(f"正在查询公共数字人列表，参数：page={page}, size={size}, kind={kind}")
        
        try:
            # 调用API查询公共数字人
            response = await client.get_avatar_list(page=page, size=size, kind=kind)
            logger.info(f"API响应：{response}")
            
            # 获取数字人列表
            avatars = response.get("data", [])
            
            # 返回结果
            return {
                "avatars": avatars,
                "page": page,
                "size": size,
                "kind": kind,
                "total": len(avatars)
            }
        except Exception as api_error:
            logger.error(f"API调用失败: {str(api_error)}")
            raise ValueError(f"查询公共数字人列表失败: {str(api_error)}")
            
    except Exception as e:
        logger.error(f"查询公共数字人列表失败: {str(e)}")
        raise ValueError(f"查询公共数字人列表失败: {str(e)}")

# 创建FastMCP工具
create_avatar_by_video = Tool.from_function(
    create_avatar_by_video_tool,
    name="create_avatar_by_video",
    description="通过视频创建数字人，支持上传本地视频文件或提供视频URL",
    tags={"avatar", "video", "creation"}
)

create_avatar_by_image = Tool.from_function(
    create_avatar_by_image_tool,
    name="create_avatar_by_image",
    description="通过图片创建数字人，支持上传本地图片文件或提供图片URL",
    tags={"avatar", "image", "creation"}
)

query_avatar_task = Tool.from_function(
    query_avatar_task_tool,
    name="query_avatar_task",
    description="查询数字人克隆任务状态，获取任务进度和结果",
    tags={"avatar", "task", "query"}
)

list_public_avatars = Tool.from_function(
    list_public_avatars_tool,
    name="list_public_avatars",
    description="查询公共数字人列表，浏览可用的公共数字人资源",
    tags={"avatar", "public", "list"}
)

# 导出工具列表，用于注册到FastMCP服务器
avatar_tools = [
    create_avatar_by_video,
    create_avatar_by_image,
    query_avatar_task,
    list_public_avatars
]

# 应用退出时关闭客户端会在主模块中处理 