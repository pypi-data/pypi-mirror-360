"""
文件上传相关的FastMCP工具，包括获取上传地址和上传文件功能
"""

import os
import logging
from typing import Dict, Any, Optional, Tuple, BinaryIO
from fastmcp.tools import Tool

from feiying_mcp.utils.api_client import HiFlyClient

# 配置日志
logger = logging.getLogger(__name__)

# 创建全局客户端实例
client = HiFlyClient()

async def get_upload_url_tool(
    file_name: str,
    file_size: int,
    content_type: str = "application/octet-stream",
) -> Dict[str, Any]:
    """
    获取文件上传地址。
    
    Args:
        file_name: 文件名称
        file_size: 文件大小（字节）
        content_type: 文件MIME类型，默认为application/octet-stream
        
    Returns:
        包含上传URL和文件ID的信息
    """
    try:
        # 参数验证
        if not file_name:
            raise ValueError("文件名不能为空")
        
        if file_size <= 0:
            raise ValueError("文件大小必须大于0")
        
        # 使用全局客户端实例
        
        # 调用API获取上传地址
        response = await client.get_upload_url(
            file_name=file_name,
            file_size=file_size,
            content_type=content_type
        )
        
        # 获取上传URL和文件ID
        upload_url = response.get("upload_url")
        file_id = response.get("file_id")
        
        if not upload_url or not file_id:
            raise ValueError("获取上传地址失败")
        
        return {
            "upload_url": upload_url,
            "file_id": file_id,
            "file_name": file_name,
            "file_size": file_size,
            "content_type": content_type
        }
        
    except Exception as e:
        logger.error(f"获取上传地址失败: {str(e)}")
        raise ValueError(f"获取上传地址失败: {str(e)}")

async def upload_file_tool(
    file_path: str,
    content_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    上传文件到飞影API。
    
    Args:
        file_path: 本地文件路径
        content_type: 文件MIME类型，如不提供则根据文件扩展名自动判断
        
    Returns:
        包含上传结果和文件ID的信息
    """
    try:
        # 参数验证
        if not file_path:
            raise ValueError("文件路径不能为空")
        
        if not os.path.exists(file_path):
            raise ValueError(f"文件不存在: {file_path}")
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        if file_size <= 0:
            raise ValueError("文件大小必须大于0")
        
        # 获取文件名
        file_name = os.path.basename(file_path)
        
        # 如果未提供content_type，根据文件扩展名判断
        if not content_type:
            extension = os.path.splitext(file_path)[1].lower()
            content_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.mp4': 'video/mp4',
                '.mov': 'video/quicktime',
                '.mp3': 'audio/mpeg',
                '.wav': 'audio/wav',
                '.m4a': 'audio/m4a',
                '.pdf': 'application/pdf',
                '.txt': 'text/plain',
                '.json': 'application/json',
            }
            content_type = content_type_map.get(extension, 'application/octet-stream')
        
        # 使用全局客户端实例
        
        logger.info(f"开始上传文件: {file_path}")
        
        # 调用API上传文件
        success, file_id = await client.upload_file(file_path, content_type)
        
        if not success or not file_id:
            raise ValueError("文件上传失败")
        
        logger.info(f"文件上传成功，文件ID: {file_id}")
        
        return {
            "success": success,
            "file_id": file_id,
            "file_name": file_name,
            "file_size": file_size,
            "content_type": content_type
        }
        
    except Exception as e:
        logger.error(f"上传文件失败: {str(e)}")
        raise ValueError(f"上传文件失败: {str(e)}")

# 创建FastMCP工具
get_upload_url = Tool.from_function(
    get_upload_url_tool,
    name="get_upload_url",
    description="获取文件上传地址，用于后续上传文件",
    tags={"upload", "file"}
)

upload_file = Tool.from_function(
    upload_file_tool,
    name="upload_file",
    description="上传本地文件到飞影API，返回文件ID",
    tags={"upload", "file"}
)

# 导出工具列表，用于注册到FastMCP服务器
upload_tools = [
    get_upload_url,
    upload_file
] 