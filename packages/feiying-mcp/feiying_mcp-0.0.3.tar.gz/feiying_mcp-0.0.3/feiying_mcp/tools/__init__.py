"""
飞影数字人API工具包
"""

from .avatar_tools import avatar_tools
from .voice_tools import voice_tools
from .upload_tools import upload_tools
from .audio_tools import audio_tools
from .video_tools import video_tools
from .query_tools import query_tools

# 导出所有工具，用于注册到FastMCP服务器
all_tools = [
    *avatar_tools,
    *voice_tools,
    *upload_tools,
    *audio_tools,
    *video_tools,
    *query_tools,
] 