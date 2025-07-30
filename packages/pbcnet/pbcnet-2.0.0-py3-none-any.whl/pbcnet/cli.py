import argparse
import sys
import os
from .core.runner import PBCNetRunner
from . import __version__

def main():
    """PBCNet命令行接口主入口"""
    parser = argparse.ArgumentParser(
        description='PBCNet: 蛋白质-配体结合亲和力预测工具',
        prog='pbcnet'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # run子命令
    run_parser = subparsers.add_parser('run', help='运行预测')
    run_parser.add_argument('data_dir', help='目标文件所在文件夹路径')
    run_parser.add_argument('--batch-size', type=int, default=8, help='批处理大小 (默认: 8)')
    run_parser.add_argument('--model-path', help='自定义模型文件路径')
    
    # version子命令
    version_parser = subparsers.add_parser('version', help='显示版本信息')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        runner = PBCNetRunner()
        runner.run_prediction(args.data_dir, args.batch_size, args.model_path)
    elif args.command == 'version':
        print(f"PBCNet version {__version__}")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()