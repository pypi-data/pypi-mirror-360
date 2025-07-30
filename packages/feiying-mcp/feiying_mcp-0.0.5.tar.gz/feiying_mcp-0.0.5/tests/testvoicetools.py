import asyncio
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_client import HiFlyClient
from tools.voice_tools import create_voice_tool, query_voice_task_tool, edit_voice_tool, list_voices_tool

# 配置日志
logging.basicConfig(level=logging.INFO)

client = HiFlyClient()

async def test_create_voice():
    """测试创建声音功能"""
    response = await create_voice_tool(
        title="测试声音克隆",
        voice_type=8,
        audio_url="https://wechat-luobo.oss-cn-shanghai.aliyuncs.com/static/uploads/e26794fe7e1c11efb9a600163e48bee7.wav",
    )
    print(f"声音克隆任务状态: {response}")
    return response.get("task_id")

async def test_query_voice_task(task_id):
    """测试查询声音克隆任务状态"""
    response = await query_voice_task_tool(
        task_id=task_id
    )
    print(f"声音克隆任务状态: {response}")
    return response

async def test_edit_voice(voice_id):
    """测试修改声音参数"""
    response = await edit_voice_tool(
        voice_id=voice_id,
        rate="1.2",
        volume="1.1",
        pitch="0.9"
    )
    print(f"修改声音参数结果: {response}")

async def test_list_voices():
    """测试查询声音列表"""
    response = await list_voices_tool(
        page=1,
        size=10,
        kind=2  # 1表示自己克隆的声音
    )
    print(f"声音列表: {response}")

async def main():
    # 创建声音
    task_id = await test_create_voice()
    
    # 查询任务状态
    response = await test_query_voice_task(task_id)
    
    # 如果任务完成，测试修改声音参数
    if response.get("status") == "completed":
        voice_id = response.get("voice_id")
        if voice_id:
            await test_edit_voice(voice_id)
    
    # 查询声音列表
    await test_list_voices()

if __name__ == "__main__":
    asyncio.run(test_list_voices()) 