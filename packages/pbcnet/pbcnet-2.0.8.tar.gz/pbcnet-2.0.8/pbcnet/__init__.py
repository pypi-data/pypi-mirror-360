"""PBCNet: 蛋白质-配体结合亲和力预测工具"""

__version__ = "2.0.8"  # 修改版本号
__author__ = "PBCNet Team"
__description__ = "Deep learning framework for protein-ligand binding affinity prediction"

# 导入主要功能
from .core.runner import PBCNetRunner

__all__ = ['PBCNetRunner', '__version__']