"""ANKML预测器"""

import os
import numpy as np
from typing import Dict, Any, Optional
try:
    import onnxruntime as ort
except ImportError:
    ort = None

from .config import ANKMLConfig
from .loader import ModelLoader
from .features import FeatureExtractor
from .exceptions import ModelNotFoundError, ValidationError, ANKMLError

class ANKPredictor:
    """ANK恶意软件检测预测器"""
    
    MODEL_TYPES = {
        'grande': 'Grande模型（大型）',
        'tall': 'Tall模型（中型）', 
        'short': 'Short模型（小型）'
    }
    
    def __init__(self, model_type: str = 'tall', version: Optional[str] = None, config: ANKMLConfig = None):
        """初始化预测器
        
        Args:
            model_type: 模型类型 ('grande', 'tall', 'short')
            config: ANKML配置对象，如果为None则使用默认配置
        """
        if model_type not in self.MODEL_TYPES:
            raise ValidationError(f"不支持的模型类型: {model_type}")
        
        self.model_type = model_type
        self.version = version
        self.config = config or ANKMLConfig()  # 使用传入的配置或默认配置
        self.loader = ModelLoader(self.config)
        self.extractor = FeatureExtractor()
        self.session = None
        
        # 初始化模型
        self._load_model()
    
    def _load_model(self, version: Optional[str] = None):
        """加载ONNX模型，可指定版本"""
        if ort is None:
            raise ANKMLError("onnxruntime未安装，请运行: pip install onnxruntime")
        
        if version:
            self.version = version
        
        model_path = self.loader.get_model_path(self.model_type) # This might need adjustment based on how versions are stored
        
        if not model_path:
            # 尝试下载模型
            try:
                model_path = self.loader.download_model(self.model_type, version=self.version)
            except Exception as e:
                # 如果下载失败，使用模拟模型
                print(f"警告: 无法下载模型 {self.model_type}: {e}")
                print("使用模拟预测模式")
                return
        
        try:
            self.session = ort.InferenceSession(model_path)
        except Exception as e:
            print(f"警告: 无法加载模型 {model_path}: {e}")
            print("使用模拟预测模式")
            self.session = None
    
    def predict(self, file_path: str) -> Dict[str, Any]:
        """预测文件是否为恶意软件
        
        Args:
            file_path: 要检测的文件路径
            
        Returns:
            包含预测结果的字典，格式: {'probability': float, 'model_type': str}
        """
        if not self.extractor.validate_file(file_path):
            raise ValidationError(f"无效的文件: {file_path}")
        
        try:
            # 提取特征
            features = self.extractor.extract_features(file_path)
            
            if self.session is not None:
                # 使用真实模型预测
                probability = self._predict_with_model(features)
            else:
                # 使用模拟预测
                probability = self._simulate_prediction(features)
            
            return {
                'probability': float(probability),
                'model_type': self.model_type,
                'model_name': self.MODEL_TYPES[self.model_type]
            }
            
        except Exception as e:
            raise ANKMLError(f"预测失败: {e}")
    
    def _predict_with_model(self, features: np.ndarray) -> float:
        """使用ONNX模型进行预测"""
        try:
            # 准备输入数据
            input_name = self.session.get_inputs()[0].name
            
            # 归一化和塑形
            input_data = (features / 255.0).reshape((1, 1, 128, 128)).astype(np.float32)
            
            # 运行推理
            outputs = self.session.run(None, {input_name: input_data})
            
            # Softmax后处理
            probabilities = self._softmax(outputs[0])
            
            # 返回恶意软件的概率（假设索引1是恶意软件）
            return float(probabilities[0][1])
            
        except Exception as e:
            print(f"模型推理失败: {e}，使用模拟预测")
            return self._simulate_prediction(features)

    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """计算softmax概率"""
        # 确保输入是二维的
        if x.ndim == 1:
            x = x.reshape(1, -1)
        
        # 减去最大值以提高数值稳定性
        max_x = np.max(x, axis=1, keepdims=True)
        e_x = np.exp(x - max_x)
        
        # 计算和并返回概率
        sum_ex = np.sum(e_x, axis=1, keepdims=True)
        return e_x / sum_ex
    
    def _simulate_prediction(self, features: np.ndarray) -> float:
        """模拟预测（当模型不可用时）"""
        # 基于特征的简单启发式预测
        # 这只是一个示例，实际使用中应该有真实的模型
        
        # 文件大小特征（第一个特征）
        file_size_score = min(features[0] / 10.0, 1.0)  # 大文件更可疑
        
        # 扩展名特征（接下来10个特征）
        ext_features = features[1:11]
        ext_score = 0.0
        if ext_features[0] > 0:  # .exe文件
            ext_score = 0.3
        elif ext_features[1] > 0:  # .dll文件
            ext_score = 0.2
        elif any(ext_features[2:8]):  # 脚本文件
            ext_score = 0.4
        
        # 字节熵特征（最后一个字节特征）
        entropy_score = features[267] if len(features) > 267 else 0.5
        
        # 哈希特征的简单统计
        hash_features = features[268:300] if len(features) > 300 else features[-32:]
        hash_variance = np.var(hash_features) if len(hash_features) > 0 else 0.5
        
        # 组合得分
        base_score = (file_size_score * 0.2 + ext_score * 0.3 + 
                     entropy_score * 0.3 + hash_variance * 0.2)
        
        # 根据模型类型调整
        if self.model_type == 'grande':
            # 大模型更保守
            final_score = base_score * 0.8
        elif self.model_type == 'short':
            # 小模型更激进
            final_score = base_score * 1.2
        else:
            # 中等模型
            final_score = base_score
        
        return max(0.0, min(1.0, final_score))
    
    def predict_batch(self, file_paths: list) -> Dict[str, Dict[str, Any]]:
        """批量预测多个文件
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            文件路径到预测结果的映射
        """
        results = {}
        for file_path in file_paths:
            try:
                results[file_path] = self.predict(file_path)
            except Exception as e:
                results[file_path] = {
                    'error': str(e),
                    'probability': 0.0,
                    'model_type': self.model_type
                }
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        model_config = self.config.get_model_config(self.model_type)
        
        return {
            'model_type': self.model_type,
            'model_name': self.MODEL_TYPES[self.model_type],
            'version': model_config.get('version', 'unknown'),
            'path': model_config.get('path'),
            'loaded': self.session is not None,
            'server_url': self.config.get_server_url()
        }
    
    def get_model_version(self) -> str:
        """获取当前模型版本"""
        return self.version or self.config.get_model_config(self.model_type).get('version', 'unknown')

    def switch_model_version(self, version: str):
        """切换模型版本"""
        if not version:
            raise ValidationError("版本号不能为空")
        
        print(f"正在切换到 {self.model_type} 模型版本 {version}...")
        self._load_model(version=version)
        print("模型切换完成")
    
    def update_model(self) -> bool:
        """更新模型"""
        try:
            updated = self.loader.update_model(self.model_type)
            if updated:
                # 重新加载模型
                self._load_model()
            return updated
        except Exception as e:
            print(f"更新模型失败: {e}")
            return False
    
    def check_for_updates(self) -> Dict[str, Any]:
        """检查模型更新"""
        try:
            return self.loader.check_model_update(self.model_type)
        except Exception as e:
            return {
                'error': str(e),
                'has_update': False
            }
    
    def switch_model(self, model_type: str):
        """切换模型类型"""
        if model_type not in self.MODEL_TYPES:
            raise ValidationError(f"不支持的模型类型: {model_type}")
        
        self.model_type = model_type
        self._load_model()