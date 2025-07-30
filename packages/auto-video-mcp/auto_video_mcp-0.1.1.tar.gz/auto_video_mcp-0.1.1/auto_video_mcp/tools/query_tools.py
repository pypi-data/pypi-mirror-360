"""
查询工具，包括私人虚拟人ID查询功能
"""

import logging
from typing import Dict, Any, List, Optional
from fastmcp.tools import Tool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from auto_video_mcp.utils.database import get_db
from auto_video_mcp.utils.models import Avatar
from auto_video_mcp.utils.api_client import HiFlyClient

# 配置日志
logger = logging.getLogger(__name__)

# 创建全局客户端实例
client = HiFlyClient()

async def query_private_avatars_tool(
    user_id: str= "default",
    page: int = 1,
    size: int = 10,
) -> Dict[str, Any]:
    """
    查询用户的私人虚拟人列表。
    
    Args:
        user_id: 用户ID
        page: 页码，默认为1
        size: 每页数量，默认为10
        
    Returns:
        包含私人虚拟人列表和分页信息的结果
    """
    # 参数验证
    if not user_id:
        raise ValueError("用户ID不能为空")
    
    if page < 1:
        raise ValueError("页码必须大于等于1")
    
    if size < 1 or size > 100:
        raise ValueError("每页数量必须在1到100之间")
    
    # 计算偏移量
    offset = (page - 1) * size
    
    # 获取数据库会话
    async for db in get_db():
        try:
            # 查询总数
            count_result = await db.execute(
                select(func.count()).select_from(Avatar).where(
                    Avatar.user_id == user_id,
                    Avatar.kind == 1  # 1表示自己克隆的
                )
            )
            total_count = count_result.scalar_one()
            
            # 查询分页数据
            query_result = await db.execute(
                select(Avatar).where(
                    Avatar.user_id == user_id,
                    Avatar.kind == 1  # 1表示自己克隆的
                ).order_by(Avatar.created_at.desc()).offset(offset).limit(size)
            )
            avatars = query_result.scalars().all()
            
            # 构建结果
            avatar_list = []
            for avatar in avatars:
                avatar_data = {
                    "avatar_id": avatar.avatar_id,
                    "title": avatar.title,
                    "kind": avatar.kind,
                    "task_id": avatar.task_id,
                    "created_at": avatar.created_at.isoformat() if avatar.created_at else None,
                    "updated_at": avatar.updated_at.isoformat() if avatar.updated_at else None
                }
                avatar_list.append(avatar_data)
            
            return {
                "avatars": avatar_list,
                "page": page,
                "size": size,
                "total": total_count,
                "pages": (total_count + size - 1) // size  # 总页数
            }
            
        except Exception as e:
            logger.error(f"查询私人虚拟人列表失败: {str(e)}")
            raise ValueError(f"查询私人虚拟人列表失败: {str(e)}")

async def query_account_credit_tool() -> Dict[str, Any]:
    """
    查询账户积分
    """
    return await client.get_account_credit()


# 创建FastMCP工具
query_private_avatars = Tool.from_function(
    query_private_avatars_tool,
    name="query_private_avatars",
    description="查询用户的私人虚拟人列表，支持分页",
    tags={"avatar", "query", "private"}
)

query_account_credit = Tool.from_function(
    query_account_credit_tool,
    name="query_account_credit",
    description="查询账户积分",
    tags={"account", "credit", "query"}
)

# 导出工具列表，用于注册到FastMCP服务器
query_tools = [
    query_private_avatars,
    query_account_credit
] 