import os
import sys
import subprocess
import pkg_resources

class PBCNetRunner:
    """PBCNet运行器类"""
    
    def __init__(self):
        self.package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    def get_run_script_path(self):
        """获取run.py脚本路径"""
        # 尝试从包安装目录获取
        try:
            return pkg_resources.resource_filename('pbcnet', 'run.py')
        except:
            # 回退到包内路径
            return os.path.join(self.package_dir, 'run.py')
    
    def get_model_path(self, custom_path=None):
        """获取模型文件路径"""
        if custom_path:
            return custom_path
            
        # 尝试从包目录获取
        try:
            return pkg_resources.resource_filename('pbcnet', 'PBCNet2.0.pth')
        except:
            # 回退到包内路径
            return os.path.join(self.package_dir, 'PBCNet2.0.pth')
    
    def run_prediction(self, data_dir, batch_size=8, model_path=None):
        """执行预测任务"""
        # 验证输入目录
        if not os.path.exists(data_dir):
            print(f"错误：目录 {data_dir} 不存在")
            sys.exit(1)
        
        # 获取脚本和模型路径
        run_script = self.get_run_script_path()
        if not os.path.exists(run_script):
            print(f"错误：找不到运行脚本 {run_script}")
            sys.exit(1)
        
        model_file = self.get_model_path(model_path)
        if not os.path.exists(model_file):
            print(f"错误：找不到模型文件 {model_file}")
            sys.exit(1)
        
        # 构建命令
        cmd = [
            sys.executable, 
            run_script, 
            data_dir,
            '--batch_size', str(batch_size),
            '--code_path', os.path.dirname(model_file)
        ]
        
        print(f"开始预测，数据目录: {data_dir}")
        print(f"使用模型: {model_file}")
        print(f"批处理大小: {batch_size}")
        
        # 执行命令
        try:
            subprocess.run(cmd, check=True)
            print("预测完成！")
        except subprocess.CalledProcessError as e:
            print(f"执行失败: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n用户中断执行")
            sys.exit(1)