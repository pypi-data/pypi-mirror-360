"""
配置加载模块，用于从环境变量或配置文件加载配置
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# 配置日志
logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_CONFIG = {
    "api_token": "",
    "api_base_url": "https://hfw-api.hifly.cc/api/v2/hifly",
    "database_url": "sqlite+aiosqlite:///./hifly.db",
    "db_echo": False,
    "db_pool_size": 5,
    "db_max_overflow": 10,
    "db_pool_timeout": 30,
    "db_pool_recycle": 1800,
    "server_host": "127.0.0.1",
    "server_port": 8000,
    "server_path": "/mcp/",
    "server_log_level": "info",
    "task_check_interval": 60,
    "task_max_retry": 3,
    "firecrawl_api_key": "",
    "disabled_tools": [],
    "trends_hub_custom_rss_url": ""
}

class Config:
    """配置类，用于加载和管理配置"""
    
    def __init__(self, config_path: Optional[str] = "/app/config.json"):
        """
        初始化配置
        
        Args:
            config_path: 配置文件路径，如果为None则从环境变量加载
        """
        # 加载环境变量
        load_dotenv()
        
        # 初始化配置
        self.config = DEFAULT_CONFIG.copy()
        
        # 从配置文件加载
        if config_path:
            self._load_from_file(config_path)
        
        # 从环境变量加载（优先级高于配置文件）
        self._load_from_env()
        
        # 验证必要的配置
        self._validate_config()
        
        logger.info("Configuration loaded successfully")
    
    def _load_from_file(self, config_path: str):
        """从配置文件加载配置"""
        try:
            path = Path(config_path)
            if not path.exists():
                logger.warning(f"Configuration file not found: {config_path}")
                return
            
            with open(path, 'r') as f:
                file_config = json.load(f)
            
            # 更新配置
            for key, value in file_config.items():
                if key in self.config:
                    self.config[key] = value
            
            logger.info(f"Loaded configuration from file: {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration from file: {str(e)}")
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        # API配置
        if os.getenv("FLYWORKS_API_TOKEN"):
            self.config["api_token"] = os.getenv("FLYWORKS_API_TOKEN")
        
        if os.getenv("FLYWORKS_API_BASE_URL"):
            self.config["api_base_url"] = os.getenv("FLYWORKS_API_BASE_URL")
        
        # 数据库配置
        if os.getenv("DATABASE_URL"):
            self.config["database_url"] = os.getenv("DATABASE_URL")
        
        if os.getenv("DB_ECHO"):
            self.config["db_echo"] = os.getenv("DB_ECHO").lower() == "true"
        
        if os.getenv("DB_POOL_SIZE"):
            self.config["db_pool_size"] = int(os.getenv("DB_POOL_SIZE"))
        
        if os.getenv("DB_MAX_OVERFLOW"):
            self.config["db_max_overflow"] = int(os.getenv("DB_MAX_OVERFLOW"))
        
        if os.getenv("DB_POOL_TIMEOUT"):
            self.config["db_pool_timeout"] = int(os.getenv("DB_POOL_TIMEOUT"))
        
        if os.getenv("DB_POOL_RECYCLE"):
            self.config["db_pool_recycle"] = int(os.getenv("DB_POOL_RECYCLE"))
        
        # 服务器配置
        if os.getenv("SERVER_HOST"):
            self.config["server_host"] = os.getenv("SERVER_HOST")
        
        if os.getenv("SERVER_PORT"):
            self.config["server_port"] = int(os.getenv("SERVER_PORT"))
        
        if os.getenv("SERVER_PATH"):
            self.config["server_path"] = os.getenv("SERVER_PATH")
        
        if os.getenv("SERVER_LOG_LEVEL"):
            self.config["server_log_level"] = os.getenv("SERVER_LOG_LEVEL")
        
        # 任务配置
        if os.getenv("TASK_CHECK_INTERVAL"):
            self.config["task_check_interval"] = int(os.getenv("TASK_CHECK_INTERVAL"))
        
        if os.getenv("TASK_MAX_RETRY"):
            self.config["task_max_retry"] = int(os.getenv("TASK_MAX_RETRY"))
        
        # 新增配置
        if os.getenv("FIRECRAWL_API_KEY"):
            self.config["firecrawl_api_key"] = os.getenv("FIRECRAWL_API_KEY")
            
        if os.getenv("DISABLED_TOOLS"):
            self.config["disabled_tools"] = [tool.strip() for tool in os.getenv("DISABLED_TOOLS").split(',')]
            
        if os.getenv("TRENDS_HUB_CUSTOM_RSS_URL"):
            self.config["trends_hub_custom_rss_url"] = os.getenv("TRENDS_HUB_CUSTOM_RSS_URL")
    
    def _validate_config(self):
        """验证配置是否有效"""
        if not self.config["api_token"]:
            logger.warning("API token not set, some features may not work properly")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return self.config.get(key, default)
    
    def __getitem__(self, key: str) -> Any:
        """
        通过下标获取配置值
        
        Args:
            key: 配置键
            
        Returns:
            配置值
        """
        return self.config[key]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将配置转换为字典
        
        Returns:
            配置字典
        """
        return self.config.copy()

# 创建全局配置实例
config = Config()

def load_config(config_path: Optional[str] = "/app/config.json") -> Config:
    """
    加载配置
    
    Args:
        config_path: 配置文件路径，如果为None则从环境变量加载
        
    Returns:
        配置实例
    """
    global config
    config = Config(config_path)
    return config