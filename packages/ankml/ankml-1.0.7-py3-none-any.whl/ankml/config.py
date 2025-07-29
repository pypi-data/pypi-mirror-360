"""ANKML配置管理

联系方式: AX3721@outlook.com
官方网站: ankml.top
"""

import os
import json
from typing import Dict, Any
from .exceptions import ConfigError

class ANKMLConfig:
    """ANKML配置管理器（支持永久保存）"""
    
    def __init__(self):
        self.config_file = os.path.expanduser("~/.ankml_config.json")
        self.config = self._load_config()
    
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
    
    def _load_config(self) -> Dict[str, Any]:
        """从文件加载配置，如果文件不存在则使用默认配置"""
        default_config = self._load_default_config()
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                # 合并配置，确保新的默认配置项也被包含
                for key, value in default_config.items():
                    if key not in file_config:
                        file_config[key] = value
                return file_config
            except (json.JSONDecodeError, IOError) as e:
                print(f"警告: 配置文件读取失败 ({e})，使用默认配置")
                return default_config
        else:
            return default_config
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            # 确保配置目录存在
            config_dir = os.path.dirname(self.config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise ConfigError(f"配置文件保存失败: {e}")
    

    
    def get(self, key: str, default=None):
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值并保存到文件"""
        self.config[key] = value
        self._save_config()
    
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
        """设置模型配置并保存到文件"""
        if "models" not in self.config:
            self.config["models"] = {}
        self.config["models"][model_type] = config
        self._save_config()
    
    def reset_config(self):
        """重置配置为默认值并保存"""
        self.config = self._load_default_config()
        self._save_config()
    
    def get_config_file_path(self) -> str:
        """获取配置文件路径"""
        return self.config_file