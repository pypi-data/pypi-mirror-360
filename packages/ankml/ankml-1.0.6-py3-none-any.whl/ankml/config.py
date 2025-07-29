"""ANKML配置管理

联系方式: AX3721@outlook.com
官方网站: ankml.top
"""

from typing import Dict, Any
from .exceptions import ConfigError

class ANKMLConfig:
    """ANKML配置管理器（内存配置）"""
    
    def __init__(self):
        self.config = self._load_default_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            "server_url": None,  # 需要开发者手动设置
            "default_model": "tall",
            "cache_dir": "./ankml_cache",
            "timeout": 30,
            "contact": "AX3721@outlook.com",
            "website": "ankml.top",
            "models": {
                "grande": {"version": None, "path": None},
                "tall": {"version": None, "path": None},
                "short": {"version": None, "path": None}
            }
        }
    

    
    def get(self, key: str, default=None):
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值（仅内存）"""
        self.config[key] = value
    
    def set_server_url(self, url: str):
        """设置服务器地址"""
        self.set("server_url", url)
    
    def get_server_url(self) -> str:
        """获取服务器地址"""
        return self.get("server_url")
    
    def get_model_config(self, model_type: str) -> Dict[str, Any]:
        """获取模型配置"""
        return self.config["models"].get(model_type, {})
    
    def set_model_config(self, model_type: str, config: Dict[str, Any]):
        """设置模型配置（仅内存）"""
        if "models" not in self.config:
            self.config["models"] = {}
        self.config["models"][model_type] = config