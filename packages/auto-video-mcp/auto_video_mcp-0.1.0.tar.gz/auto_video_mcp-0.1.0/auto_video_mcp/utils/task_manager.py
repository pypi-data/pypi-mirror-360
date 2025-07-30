"""
任务状态更新管理器，定期检查任务状态并更新数据库
"""

import asyncio
import logging
import datetime
from typing import Dict, Any, List, Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, and_

from auto_video_mcp.utils.api_client import HiFlyClient
from auto_video_mcp.utils.database import get_db, AsyncSessionLocal
from auto_video_mcp.utils.models import Task, Avatar, Voice, Video, Audio
# 导入封装好的工具函数
from auto_video_mcp.tools.avatar_tools import query_avatar_task_tool
from auto_video_mcp.tools.voice_tools import query_voice_task_tool
from auto_video_mcp.tools.video_tools import query_video_task_tool
from auto_video_mcp.tools.audio_tools import query_audio_task_tool

# 配置日志
logger = logging.getLogger(__name__)

# 任务类型映射
TASK_TYPE_MAP = {
    1: "视频作品",
    2: "数字人克隆",
    3: "声音克隆",
    4: "音频创作"
}

# 任务状态映射
TASK_STATUS_MAP = {
    1: "等待中",
    2: "处理中",
    3: "完成",
    4: "失败"
}

class TaskManager:
    """任务状态更新管理器"""
    
    def __init__(self, check_interval: int = 60, max_retry: int = 3):
        """
        初始化任务管理器
        
        Args:
            check_interval: 检查间隔时间（秒）
            max_retry: 任务处理最大重试次数
        """
        self.check_interval = check_interval
        self.max_retry = max_retry
        self.running = False
        self.task = None
        self.processing_tasks: Set[str] = set()  # 正在处理的任务ID集合，避免重复处理
        self.client = None  # API客户端实例
        
        logger.info(f"TaskManager initialized with check_interval={check_interval}s, max_retry={max_retry}")
    
    async def start(self):
        """启动任务状态更新循环"""
        if self.running:
            logger.warning("TaskManager is already running")
            return
        
        # 创建API客户端
        self.client = HiFlyClient()
        logger.info("Created API client for TaskManager")
        
        self.running = True
        self.task = asyncio.create_task(self._update_loop())
        logger.info("TaskManager started")
    
    async def stop(self):
        """停止任务状态更新循环"""
        if not self.running:
            logger.warning("TaskManager is not running")
            return
        
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None
        
        # 关闭API客户端
        if self.client:
            await self.client.close()
            self.client = None
            logger.info("Closed API client for TaskManager")
            
        logger.info("TaskManager stopped")
    
    async def _update_loop(self):
        """任务状态更新循环"""
        while self.running:
            try:
                await self._check_and_update_tasks()
            except Exception as e:
                logger.error(f"Error in task update loop: {str(e)}")
            
            # 等待下一次检查
            await asyncio.sleep(self.check_interval)
    
    async def _check_and_update_tasks(self):
        """检查并更新所有未完成任务的状态"""
        logger.debug("Starting task status check...")
        
        # 获取数据库会话
        async with AsyncSessionLocal() as db:
            try:
                # 查询所有未完成的任务
                result = await db.execute(
                    select(Task).where(
                        and_(
                            Task.status.in_([1, 2]),  # 1:等待中, 2:处理中
                            Task.task_id.notin_(self.processing_tasks)  # 排除正在处理的任务
                        )
                    )
                )
                tasks = result.scalars().all()
                
                if not tasks:
                    logger.debug("No pending tasks found")
                    return
                
                logger.info(f"Found {len(tasks)} pending tasks")
                
                # 处理每个未完成的任务
                for task in tasks:
                    # 标记任务为正在处理
                    self.processing_tasks.add(task.task_id)
                    
                    try:
                        # 根据任务类型调用不同的工具函数查询任务状态
                        await self._update_task_status(task)
                    except Exception as e:
                        logger.error(f"Error updating task {task.task_id}: {str(e)}")
                    finally:
                        # 无论成功失败，都从处理集合中移除
                        self.processing_tasks.remove(task.task_id)
                
            except Exception as e:
                logger.error(f"Error checking tasks: {str(e)}")
    
    async def _update_task_status(self, task: Task):
        """
        更新单个任务的状态，使用封装好的工具函数
        
        Args:
            task: 任务对象
        """
        logger.debug(f"Updating task {task.task_id} (type: {TASK_TYPE_MAP.get(task.task_type, 'Unknown')})")
        
        try:
            # 根据任务类型调用不同的工具函数
            if task.task_type == 1:  # 视频作品
                await query_video_task_tool(task.task_id)
            elif task.task_type == 2:  # 数字人克隆
                await query_avatar_task_tool(task.task_id)
            elif task.task_type == 3:  # 声音克隆
                await query_voice_task_tool(task.task_id)
            elif task.task_type == 4:  # 音频创作
                await query_audio_task_tool(task.task_id)
            else:
                logger.warning(f"Unknown task type: {task.task_type}")
                return
            
            logger.info(f"Successfully updated task {task.task_id}")
            
        except Exception as e:
            logger.error(f"Error updating task {task.task_id}: {str(e)}")

# 创建全局任务管理器实例
task_manager = TaskManager()

async def start_task_manager():
    """启动任务管理器"""
    await task_manager.start()

async def stop_task_manager():
    """停止任务管理器"""
    await task_manager.stop()

# 手动触发任务状态检查
async def check_tasks_now():
    """手动触发任务状态检查"""
    try:
        await task_manager._check_and_update_tasks()
        return {"status": "success", "message": "任务状态检查已触发"}
    except Exception as e:
        logger.error(f"Error triggering task check: {str(e)}")
        return {"status": "error", "message": f"任务状态检查失败: {str(e)}"} 