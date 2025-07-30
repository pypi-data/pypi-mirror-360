import asyncio
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_client import HiFlyClient
from tools.video_tools import create_video_by_audio_tool, create_video_by_tts_tool, query_video_task_tool

# 配置日志
logging.basicConfig(level=logging.INFO)

client = HiFlyClient()

async def test_create_video_by_audio():
    response = await create_video_by_audio_tool(
        avatar="0ezhDusZR1FI9Qi042MTrg",  # 替换为你的数字人ID
        audio_url="https://hfcdn.lingverse.co/39903f565d0a8aa3745e9b5d99c6dfa1/6865577F/hf/local/1000020056/audios/38c97451-15e5-4e7c-a17b-2d8134df219b.wav",
        title="音频驱动视频测试"
    )
    print(f"音频驱动视频创建任务: {response}")

async def test_create_video_by_tts():
    response = await create_video_by_tts_tool(
        avatar="0ezhDusZR1FI9Qi042MTrg",  # 替换为你的数字人ID
        voice="iLafe9ZZZrjgiCulLLTXNw",   # 替换为你的声音ID
        text="这是一个测试视频，用于测试文本驱动视频创建功能。",
        title="文本驱动视频测试",
        st_show=1  # 显示字幕
    )
    print(f"文本驱动视频创建任务: {response}")

async def test_query_video_task():
    response = await query_video_task_tool(
        task_id="9fV1PigNwIBQ_qRplYl7Lw"  # 替换为实际的任务ID
    )
    print(f"视频创建任务状态: {response}")

if __name__ == "__main__":
    # 取消注释你想要测试的函数
    # asyncio.run(test_create_video_by_audio())
    # asyncio.run(test_create_video_by_tts())
    asyncio.run(test_query_video_task()) 