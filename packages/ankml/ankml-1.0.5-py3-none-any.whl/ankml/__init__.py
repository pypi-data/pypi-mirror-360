"""ANKML - ANK恶意软件检测库

联系方式: AX3721@outlook.com
官方网站: ankml.top
"""

__version__ = "1.0.0"
__author__ = "ANK Team"
__email__ = "AX3721@outlook.com"
__website__ = "ankml.top"

from .predictor import ANKPredictor
from .config import ANKMLConfig
from .loader import ModelLoader
from .features import FeatureExtractor
from .exceptions import ANKMLError, ModelNotFoundError, NetworkError, ValidationError

__all__ = [
    'ANKPredictor', 
    'ANKMLConfig', 
    'ModelLoader', 
    'FeatureExtractor', 
    'ANKMLError', 
    'ModelNotFoundError', 
    'NetworkError', 
    'ValidationError'
]

# 便捷函数
def get_version():
    """获取版本信息"""
    return __version__

def get_contact_info():
    """获取联系信息"""
    return {
        'email': __email__,
        'website': __website__,
        'version': __version__
    }