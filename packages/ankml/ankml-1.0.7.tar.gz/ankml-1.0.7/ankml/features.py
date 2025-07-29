"""ANKML特征提取器"""

import os
import numpy as np


class FeatureExtractor:
    """从文件提取特征并转换为图像"""

    def validate_file(self, file_path: str) -> bool:
        """验证文件是否可以处理"""
        if not os.path.exists(file_path):
            return False
        
        if os.path.getsize(file_path) == 0:
            return False
        
        return True

    def extract_features(self, file_path: str) -> np.ndarray:
        """将文件读取为二进制数据并转换为图像格式"""
        with open(file_path, 'rb') as file:
            binary_data = file.read()
        image = np.frombuffer(binary_data, dtype=np.uint8)
        if len(image) < 128 * 128:
            image = np.pad(image, (0, 128 * 128 - len(image)), 'constant')
        else:
            image = image[:128 * 128]
        image = image.reshape((128, 128))
        return image