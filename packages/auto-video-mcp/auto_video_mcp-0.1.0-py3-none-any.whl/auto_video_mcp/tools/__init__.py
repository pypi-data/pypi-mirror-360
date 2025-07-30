"""
MCP服务工具列表
"""

from .avatar_tools import avatar_tools
from .voice_tools import voice_tools
from .audio_tools import audio_tools
from .video_tools import video_tools
from .query_tools import query_tools
from .websearch import websearch_tool
from .crawlweb import crawl_website_tool
from .kr36 import kr36_tool_config
from .autohome import autohome_tool_config
from .baidu import baidu_tool_config
from .custom_rss import custom_rss_tool


import os

# 获取禁用工具名称列表
disabled_tools = os.getenv("DISABLED_TOOLS", "")
disabled_list = [x.strip() for x in disabled_tools.split(",") if x.strip()]

# 将所有工具按模块分类组织
tool_groups = {
    "avatar_tools": avatar_tools,
    "voice_tools": voice_tools,
    "audio_tools": audio_tools,
    "video_tools": video_tools,
    "query_tools": query_tools,
    "websearch_tool": [websearch_tool],
    "crawl_website_tool": [crawl_website_tool],
    "kr36_tool_config": [kr36_tool_config],
    "autohome_tool_config": [autohome_tool_config],
    "baidu_tool_config": [baidu_tool_config],
    "custom_rss_tool": [custom_rss_tool],
}

# 过滤掉禁用工具
for group in tool_groups.values():
    group[:] = [tool for tool in group if getattr(tool, "name", None) not in disabled_list]

# 整合所有需要注册的工具
all_tools = []
for group_list in tool_groups.values():
    all_tools.extend(group_list)