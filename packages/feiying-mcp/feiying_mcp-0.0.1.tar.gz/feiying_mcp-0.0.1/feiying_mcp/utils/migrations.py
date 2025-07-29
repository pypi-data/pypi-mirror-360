import asyncio
import logging
from alembic.config import Config
from alembic import command
from pathlib import Path
import os

# 配置日志
logger = logging.getLogger(__name__)

# 获取项目根目录
BASE_DIR = Path(__file__).parent.absolute()

def create_alembic_config() -> Config:
    """
    创建Alembic配置
    """
    # 创建配置对象
    config = Config()
    
    # 设置alembic.ini文件路径
    config.set_main_option("script_location", str(BASE_DIR / "migrations"))
    
    # 设置其他配置选项
    config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./hifly.db"))
    config.set_main_option("file_template", "%%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d_%%(slug)s")
    
    return config

def create_migration(message: str) -> None:
    """
    创建新的迁移脚本
    
    Args:
        message: 迁移说明
    """
    try:
        config = create_alembic_config()
        
        # 确保migrations目录存在
        migrations_dir = BASE_DIR / "migrations"
        versions_dir = migrations_dir / "versions"
        
        if not migrations_dir.exists():
            migrations_dir.mkdir(exist_ok=True)
            (migrations_dir / "env.py").touch()
            (migrations_dir / "README").touch()
            (migrations_dir / "script.py.mako").touch()
        
        if not versions_dir.exists():
            versions_dir.mkdir(exist_ok=True)
        
        # 创建迁移脚本
        command.revision(config, message=message, autogenerate=True)
        logger.info(f"Migration script created with message: {message}")
    except Exception as e:
        logger.error(f"Error creating migration: {e}")
        raise

def upgrade_database() -> None:
    """
    升级数据库到最新版本
    """
    try:
        config = create_alembic_config()
        command.upgrade(config, "head")
        logger.info("Database upgraded to latest version")
    except Exception as e:
        logger.error(f"Error upgrading database: {e}")
        raise

def downgrade_database(revision: str = "-1") -> None:
    """
    降级数据库
    
    Args:
        revision: 要降级到的版本，默认为上一个版本
    """
    try:
        config = create_alembic_config()
        command.downgrade(config, revision)
        logger.info(f"Database downgraded to {revision}")
    except Exception as e:
        logger.error(f"Error downgrading database: {e}")
        raise

async def run_migrations() -> None:
    """
    运行数据库迁移
    """
    try:
        # 在异步环境中运行同步代码
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, upgrade_database)
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        raise

if __name__ == "__main__":
    # 当直接运行此脚本时，创建迁移脚本或升级数据库
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "create" and len(sys.argv) > 2:
            create_migration(sys.argv[2])
        elif sys.argv[1] == "upgrade":
            upgrade_database()
        elif sys.argv[1] == "downgrade":
            revision = sys.argv[2] if len(sys.argv) > 2 else "-1"
            downgrade_database(revision)
        else:
            print("Usage: python migrations.py [create <message>|upgrade|downgrade [revision]]")
    else:
        print("Usage: python migrations.py [create <message>|upgrade|downgrade [revision]]") 