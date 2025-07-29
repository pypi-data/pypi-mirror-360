"""ANKML异常定义"""

class ANKMLError(Exception):
    """ANKML基础异常类"""
    pass

class ModelNotFoundError(ANKMLError):
    """模型未找到异常"""
    pass

class ConfigError(ANKMLError):
    """配置错误异常"""
    pass

class NetworkError(ANKMLError):
    """网络错误异常"""
    pass

class ValidationError(ANKMLError):
    """验证错误异常"""
    pass