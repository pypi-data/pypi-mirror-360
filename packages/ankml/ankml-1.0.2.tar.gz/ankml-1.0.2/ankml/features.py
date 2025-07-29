"""ANKML特征提取器"""

import os
import hashlib
import struct
from typing import List, Dict, Any
import numpy as np
from .exceptions import ValidationError

class FeatureExtractor:
    """特征提取器"""
    
    def __init__(self):
        self.feature_size = 1000  # 固定特征向量大小
    
    def extract_features(self, file_path: str) -> np.ndarray:
        """从文件提取特征"""
        if not os.path.exists(file_path):
            raise ValidationError(f"文件不存在: {file_path}")
        
        try:
            # 基础文件特征
            basic_features = self._extract_basic_features(file_path)
            
            # 字节序列特征
            byte_features = self._extract_byte_features(file_path)
            
            # 哈希特征
            hash_features = self._extract_hash_features(file_path)
            
            # 组合所有特征
            all_features = np.concatenate([basic_features, byte_features, hash_features])
            
            # 确保特征向量大小固定
            if len(all_features) > self.feature_size:
                features = all_features[:self.feature_size]
            else:
                features = np.pad(all_features, (0, self.feature_size - len(all_features)), 'constant')
            
            return features.astype(np.float32)
            
        except Exception as e:
            raise ValidationError(f"特征提取失败: {e}")
    
    def _extract_basic_features(self, file_path: str) -> np.ndarray:
        """提取基础文件特征"""
        features = []
        
        # 文件大小
        file_size = os.path.getsize(file_path)
        features.append(min(file_size / 1024 / 1024, 100))  # MB，最大100MB
        
        # 文件扩展名特征
        ext = os.path.splitext(file_path)[1].lower()
        ext_features = [0] * 10  # 10种常见扩展名
        ext_map = {'.exe': 0, '.dll': 1, '.bat': 2, '.cmd': 3, '.scr': 4, 
                  '.com': 5, '.pif': 6, '.vbs': 7, '.js': 8, '.jar': 9}
        if ext in ext_map:
            ext_features[ext_map[ext]] = 1
        features.extend(ext_features)
        
        return np.array(features, dtype=np.float32)
    
    def _extract_byte_features(self, file_path: str, max_bytes: int = 8192) -> np.ndarray:
        """提取字节序列特征"""
        features = []
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read(max_bytes)
            
            if len(data) == 0:
                return np.zeros(256, dtype=np.float32)
            
            # 字节频率分布
            byte_counts = np.zeros(256, dtype=np.float32)
            for byte in data:
                byte_counts[byte] += 1
            
            # 归一化
            byte_freq = byte_counts / len(data)
            
            # 熵计算
            entropy = 0
            for freq in byte_freq:
                if freq > 0:
                    entropy -= freq * np.log2(freq)
            
            features.extend(byte_freq)
            features.append(entropy / 8.0)  # 归一化熵值
            
        except Exception:
            features = [0] * 257  # 256字节频率 + 1熵值
        
        return np.array(features, dtype=np.float32)
    
    def _extract_hash_features(self, file_path: str) -> np.ndarray:
        """提取哈希特征"""
        features = []
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # MD5哈希的前32位转换为数值特征
            md5_hash = hashlib.md5(data).hexdigest()
            for i in range(0, min(32, len(md5_hash)), 2):
                hex_byte = md5_hash[i:i+2]
                features.append(int(hex_byte, 16) / 255.0)
            
            # SHA1哈希的前32位
            sha1_hash = hashlib.sha1(data).hexdigest()
            for i in range(0, min(32, len(sha1_hash)), 2):
                hex_byte = sha1_hash[i:i+2]
                features.append(int(hex_byte, 16) / 255.0)
            
        except Exception:
            features = [0] * 32  # 16个MD5特征 + 16个SHA1特征
        
        return np.array(features, dtype=np.float32)
    
    def validate_file(self, file_path: str) -> bool:
        """验证文件是否可以处理"""
        if not os.path.exists(file_path):
            return False
        
        if os.path.getsize(file_path) == 0:
            return False
        
        if os.path.getsize(file_path) > 100 * 1024 * 1024:  # 100MB限制
            return False
        
        return True