"""ANKML模型加载器"""

import os
import requests
import hashlib
from typing import Optional, Dict, Any
from .config import ANKMLConfig
from .exceptions import ModelNotFoundError, NetworkError

class ModelLoader:
    """模型加载器"""
    
    def __init__(self, config: ANKMLConfig):
        self.config = config
        self.cache_dir = config.get("cache_dir", "./ankml_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_model_path(self, model_type: str) -> Optional[str]:
        """获取模型文件路径"""
        model_config = self.config.get_model_config(model_type)
        
        if model_config.get("path") and os.path.exists(model_config["path"]):
            return model_config["path"]
        
        # 尝试从缓存目录查找
        cache_path = os.path.join(self.cache_dir, f"{model_type}.onnx")
        if os.path.exists(cache_path):
            return cache_path
        
        return None
    
    def download_model(self, model_type: str, force: bool = False) -> str:
        """下载模型文件"""
        if not force:
            existing_path = self.get_model_path(model_type)
            if existing_path:
                return existing_path
        
        # 构建下载URL
        server_url = self.config.get_server_url()
        download_url = f"{server_url}/models/{model_type}/download"
        
        try:
            response = requests.get(download_url, timeout=self.config.get("timeout", 30))
            response.raise_for_status()
            
            # 保存到缓存目录
            cache_path = os.path.join(self.cache_dir, f"{model_type}.onnx")
            with open(cache_path, 'wb') as f:
                f.write(response.content)
            
            # 更新配置
            model_config = self.config.get_model_config(model_type)
            model_config["path"] = cache_path
            model_config["hash"] = self._calculate_file_hash(cache_path)
            self.config.set_model_config(model_type, model_config)
            
            return cache_path
            
        except requests.RequestException as e:
            raise NetworkError(f"下载模型失败: {e}")
        except Exception as e:
            raise ModelNotFoundError(f"模型下载异常: {e}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return ""
    
    def check_model_update(self, model_type: str) -> Dict[str, Any]:
        """检查模型更新"""
        server_url = self.config.get_server_url()
        check_url = f"{server_url}/models/{model_type}/version"
        
        try:
            response = requests.get(check_url, timeout=self.config.get("timeout", 30))
            response.raise_for_status()
            
            server_info = response.json()
            local_config = self.config.get_model_config(model_type)
            
            return {
                "has_update": server_info.get("version") != local_config.get("version"),
                "server_version": server_info.get("version"),
                "local_version": local_config.get("version"),
                "server_hash": server_info.get("hash"),
                "local_hash": local_config.get("hash")
            }
            
        except requests.RequestException as e:
            raise NetworkError(f"检查更新失败: {e}")
    
    def update_model(self, model_type: str) -> bool:
        """更新模型"""
        try:
            update_info = self.check_model_update(model_type)
            if update_info["has_update"]:
                self.download_model(model_type, force=True)
                return True
            return False
        except Exception:
            return False