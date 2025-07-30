from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
import datetime

Base = declarative_base()

class Task(Base):
    """任务表，存储各类任务的信息和状态"""
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(50), unique=True, index=True, nullable=False, comment="飞影API返回的任务ID")
    task_type = Column(Integer, nullable=False, comment="任务类型，1:作品, 2:数字人克隆, 3:声音克隆, 4:音频创作")
    status = Column(Integer, default=1, comment="任务状态，1:等待中, 2:处理中, 3:完成, 4:失败")
    title = Column(String(100), comment="任务标题")
    message = Column(String(500), default="", comment="任务消息，通常是错误信息")
    code = Column(Integer, default=0, comment="错误码")
    request_id = Column(String(50), comment="请求ID")
    user_id = Column(String(50), index=True, comment="用户ID")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, comment="更新时间")
    
    # 关系
    avatars = relationship("Avatar", back_populates="task")
    voices = relationship("Voice", back_populates="task")
    videos = relationship("Video", back_populates="task")
    audios = relationship("Audio", back_populates="task")
    
    def __repr__(self):
        return f"<Task(id='{self.id}', task_id='{self.task_id}', status={self.status})>"


class Avatar(Base):
    """数字人表，存储数字人信息"""
    __tablename__ = "avatars"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    avatar_id = Column(String(50), unique=True, index=True, nullable=True, comment="飞影API返回的数字人ID")
    title = Column(String(100), comment="数字人名称")
    kind = Column(Integer, default=1, comment="数字人类型，1:自己克隆的, 2:公共数字人")
    task_id = Column(String(50), ForeignKey("tasks.task_id"), nullable=True, comment="关联的任务ID")
    user_id = Column(String(50), index=True, comment="用户ID")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, comment="创建时间")
    
    # 关系
    task = relationship("Task", back_populates="avatars")
    videos = relationship("Video", back_populates="avatar")
    
    def __repr__(self):
        return f"<Avatar(id='{self.id}', avatar_id='{self.avatar_id}', title='{self.title}')>"


class Voice(Base):
    """声音表，存储声音信息和参数"""
    __tablename__ = "voices"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    voice_id = Column(String(50), unique=True, index=True, nullable=True, comment="飞影API返回的声音ID")
    title = Column(String(100), comment="声音名称")
    voice_type = Column(Integer, comment="声音类型，8:基础版声音V2, 10:公版声音, 20:高保真声音")
    rate = Column(String(10), default="1.0", comment="语速")
    volume = Column(String(10), default="1.0", comment="音量")
    pitch = Column(String(10), default="1.0", comment="语调")
    task_id = Column(String(50), ForeignKey("tasks.task_id"), nullable=True, comment="关联的任务ID")
    demo_url = Column(String(500), nullable=True, comment="试听声音文件地址")
    user_id = Column(String(50), index=True, comment="用户ID")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, comment="创建时间")
    
    # 关系
    task = relationship("Task", back_populates="voices")
    videos = relationship("Video", back_populates="voice")
    
    def __repr__(self):
        return f"<Voice(id='{self.id}', voice_id='{self.voice_id}', title='{self.title}')>"


class Video(Base):
    """视频作品表，存储视频作品信息"""
    __tablename__ = "videos"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(100), comment="作品名称")
    avatar_id = Column(String(50), ForeignKey("avatars.avatar_id"), comment="使用的数字人ID")
    voice_id = Column(String(50), ForeignKey("voices.voice_id"), nullable=True, comment="使用的声音ID")
    task_id = Column(String(50), ForeignKey("tasks.task_id"), comment="关联的任务ID")
    video_url = Column(String(500), nullable=True, comment="视频URL")
    duration = Column(Integer, nullable=True, comment="视频时长(秒)")
    text = Column(Text, nullable=True, comment="生成视频的文本内容")
    audio_url = Column(String(500), nullable=True, comment="音频URL")
    file_id = Column(String(50), nullable=True, comment="文件ID")
    user_id = Column(String(50), index=True, comment="用户ID")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, comment="创建时间")
    
    # 关系
    task = relationship("Task", back_populates="videos")
    avatar = relationship("Avatar", back_populates="videos")
    voice = relationship("Voice", back_populates="videos")
    
    def __repr__(self):
        return f"<Video(id='{self.id}', title='{self.title}', duration={self.duration})>"


class Audio(Base):
    """音频作品表，存储音频作品信息"""
    __tablename__ = "audios"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(100), comment="作品名称")
    voice_id = Column(String(50), ForeignKey("voices.voice_id"), comment="使用的声音ID")
    task_id = Column(String(50), ForeignKey("tasks.task_id"), comment="关联的任务ID")
    audio_url = Column(String(500), nullable=True, comment="音频URL")
    text = Column(Text, nullable=True, comment="生成音频的文本内容")
    duration = Column(Integer, nullable=True, comment="音频时长(秒)")
    user_id = Column(String(50), index=True, comment="用户ID")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, comment="创建时间")
    
    # 关系
    task = relationship("Task", back_populates="audios")
    
    def __repr__(self):
        return f"<Audio(id='{self.id}', title='{self.title}')>"


class UploadFile(Base):
    """上传文件表，存储上传文件信息"""
    __tablename__ = "upload_files"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String(50), unique=True, index=True, nullable=False, comment="飞影API返回的文件ID")
    file_extension = Column(String(10), comment="文件扩展名")
    upload_url = Column(String(1000), comment="上传地址")
    content_type = Column(String(100), comment="文件MIME类型")
    uploaded = Column(Boolean, default=False, comment="是否已上传")
    user_id = Column(String(50), index=True, comment="用户ID")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, comment="创建时间")
    
    def __repr__(self):
        return f"<UploadFile(id='{self.id}', file_id='{self.file_id}', uploaded={self.uploaded})>" 