"""ANKML命令行接口

联系方式: AX3721@outlook.com
官方网站: ankml.top
"""

import argparse
import sys
import os
from typing import List

from .predictor import ANKPredictor
from .config import ANKMLConfig
from .exceptions import ANKMLError

def main():
    """主命令行入口"""
    parser = argparse.ArgumentParser(
        description="ANK恶意软件检测工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  ankml scan file.exe                    # 扫描单个文件
  ankml scan *.exe                       # 扫描多个文件
  ankml scan --model grande file.exe     # 使用指定模型
  ankml info                             # 显示模型信息
  ankml config --show                    # 显示当前配置
  ankml config --server-url <URL>        # 设置服务器地址
  ankml config --default-model grande    # 设置默认模型
  ankml config --set debug true          # 设置自定义配置项
  
联系方式: AX3721@outlook.com
官方网站: ankml.top
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # scan命令
    scan_parser = subparsers.add_parser('scan', help='扫描文件')
    scan_parser.add_argument('files', nargs='+', help='要扫描的文件路径')
    scan_parser.add_argument('--model', '-m', 
                           choices=['grande', 'tall', 'short'],
                           default='tall',
                           help='使用的模型类型 (默认: tall)')
    scan_parser.add_argument('--threshold', '-t', type=float, default=0.5,
                           help='恶意软件判定阈值 (默认: 0.5)')
    scan_parser.add_argument('--verbose', '-v', action='store_true',
                           help='显示详细信息')
    
    # info命令
    info_parser = subparsers.add_parser('info', help='显示模型信息')
    info_parser.add_argument('--model', '-m',
                           choices=['grande', 'tall', 'short'],
                           help='指定模型类型')
    
    # config命令
    config_parser = subparsers.add_parser('config', help='配置管理')
    config_parser.add_argument('--show', action='store_true', help='显示当前配置')
    config_parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), help='设置配置项')
    config_parser.add_argument('--server-url', help='设置服务器地址')
    config_parser.add_argument('--default-model', choices=['grande', 'tall', 'short'], help='设置默认模型')
    config_parser.add_argument('--cache-dir', help='设置缓存目录')
    config_parser.add_argument('--timeout', type=int, help='设置超时时间(秒)')
    config_parser.add_argument('--reset', action='store_true', help='重置为默认配置')
    
    # update命令
    update_parser = subparsers.add_parser('update', help='更新模型')
    update_parser.add_argument('--model', '-m',
                             choices=['grande', 'tall', 'short'],
                             help='指定要更新的模型类型')
    update_parser.add_argument('--check', action='store_true',
                             help='仅检查更新，不执行更新')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'scan':
            return cmd_scan(args)
        elif args.command == 'info':
            return cmd_info(args)
        elif args.command == 'config':
            return cmd_config(args)
        elif args.command == 'update':
            return cmd_update(args)
        else:
            print(f"未知命令: {args.command}")
            return 1
            
    except ANKMLError as e:
        print(f"错误: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n操作已取消")
        return 1
    except Exception as e:
        print(f"未知错误: {e}")
        return 1

def cmd_scan(args) -> int:
    """扫描命令"""
    # 展开文件路径
    files = []
    for pattern in args.files:
        if '*' in pattern or '?' in pattern:
            import glob
            files.extend(glob.glob(pattern))
        else:
            files.append(pattern)
    
    if not files:
        print("没有找到要扫描的文件")
        return 1
    
    # 验证文件存在
    valid_files = []
    for file_path in files:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            valid_files.append(file_path)
        else:
            print(f"警告: 文件不存在或不是文件: {file_path}")
    
    if not valid_files:
        print("没有有效的文件可以扫描")
        return 1
    
    print(f"使用模型: {args.model}")
    print(f"恶意软件阈值: {args.threshold}")
    print(f"扫描 {len(valid_files)} 个文件...\n")
    
    # 初始化预测器
    predictor = ANKPredictor(model_type=args.model)
    
    # 扫描文件
    malware_count = 0
    for file_path in valid_files:
        try:
            result = predictor.predict(file_path)
            probability = result['probability']
            is_malware = probability >= args.threshold
            
            if is_malware:
                malware_count += 1
                status = "恶意软件"
                color = "\033[91m"  # 红色
            else:
                status = "安全"
                color = "\033[92m"  # 绿色
            
            reset_color = "\033[0m"
            
            if args.verbose:
                print(f"{color}{file_path}: {status} (概率: {probability:.3f}){reset_color}")
            else:
                print(f"{color}{os.path.basename(file_path)}: {status}{reset_color}")
                
        except Exception as e:
            print(f"\033[93m{file_path}: 扫描失败 - {e}\033[0m")  # 黄色
    
    print(f"\n扫描完成: {len(valid_files)} 个文件, {malware_count} 个可疑文件")
    return 0

def cmd_info(args) -> int:
    """信息命令"""
    if args.model:
        models = [args.model]
    else:
        models = ['grande', 'tall', 'short']
    
    for model_type in models:
        try:
            predictor = ANKPredictor(model_type=model_type)
            info = predictor.get_model_info()
            
            print(f"\n模型类型: {info['model_type']}")
            print(f"模型名称: {info['model_name']}")
            print(f"版本: {info['version']}")
            print(f"已加载: {'是' if info['loaded'] else '否'}")
            print(f"服务器地址: {info['server_url']}")
            if info.get('path'):
                print(f"模型路径: {info['path']}")
                
        except Exception as e:
            print(f"\n获取模型 {model_type} 信息失败: {e}")
    
    return 0

def cmd_config(args) -> int:
    """配置命令"""
    config = ANKMLConfig()
    
    # 处理重置配置
    if args.reset:
        config.reset_config()
        print("配置已重置为默认值并保存")
        return 0
    
    # 处理配置设置
    config_changed = False
    
    if args.server_url:
        config.set_server_url(args.server_url)
        print(f"服务器地址已设置为: {args.server_url}")
        config_changed = True
    
    if args.default_model:
        config.set('default_model', args.default_model)
        print(f"默认模型已设置为: {args.default_model}")
        config_changed = True
    
    if args.cache_dir:
        config.set('cache_dir', args.cache_dir)
        print(f"缓存目录已设置为: {args.cache_dir}")
        config_changed = True
    
    if args.timeout:
        config.set('timeout', args.timeout)
        print(f"超时时间已设置为: {args.timeout}秒")
        config_changed = True
    
    if args.set:
        key, value = args.set
        # 尝试转换数值类型
        if value.isdigit():
            value = int(value)
        elif value.lower() in ['true', 'false']:
            value = value.lower() == 'true'
        config.set(key, value)
        print(f"配置项 {key} 已设置为: {value}")
        config_changed = True
    
    # 显示当前配置
    if args.show or not config_changed:
        print("\n=== ANKML 当前配置 ===")
        print(f"服务器地址: {config.get_server_url() or '未设置'}")
        print(f"默认模型: {config.get('default_model', 'tall')}")
        print(f"缓存目录: {config.get('cache_dir', './ankml_cache')}")
        print(f"超时设置: {config.get('timeout', 30)}秒")
        print(f"联系方式: {config.get('contact', 'AX3721@outlook.com')}")
        print(f"官方网站: {config.get('website', 'ankml.top')}")
        
        print("\n=== 配置编辑说明 ===")
        print("使用以下命令编辑配置:")
        print("  ankml config --server-url <URL>           # 设置服务器地址")
        print("  ankml config --default-model <MODEL>      # 设置默认模型 (grande/tall/short)")
        print("  ankml config --cache-dir <PATH>           # 设置缓存目录")
        print("  ankml config --timeout <SECONDS>          # 设置超时时间")
        print("  ankml config --set <KEY> <VALUE>          # 设置任意配置项")
        print("  ankml config --reset                      # 重置为默认配置")
        print("  ankml config --show                       # 显示当前配置")
        
        print("\n=== 配置示例 ===")
        print("  ankml config --server-url https://api.ankml.top")
        print("  ankml config --default-model grande")
        print("  ankml config --cache-dir /tmp/ankml_cache")
        print("  ankml config --timeout 60")
        print("  ankml config --set debug true")
        
        print(f"\n配置文件位置: {config.get_config_file_path()}")
    
    return 0

def cmd_update(args) -> int:
    """更新命令"""
    if args.model:
        models = [args.model]
    else:
        models = ['grande', 'tall', 'short']
    
    for model_type in models:
        try:
            predictor = ANKPredictor(model_type=model_type)
            
            if args.check:
                # 仅检查更新
                update_info = predictor.check_for_updates()
                if update_info.get('has_update'):
                    print(f"模型 {model_type} 有可用更新")
                    if 'latest_version' in update_info:
                        print(f"  当前版本: {predictor.get_model_version()}")
                        print(f"  最新版本: {update_info['latest_version']}")
                else:
                    print(f"模型 {model_type} 已是最新版本")
            else:
                # 执行更新
                print(f"正在更新模型 {model_type}...")
                if predictor.update_model():
                    print(f"模型 {model_type} 更新成功")
                else:
                    print(f"模型 {model_type} 无需更新或更新失败")
                    
        except Exception as e:
            print(f"处理模型 {model_type} 时出错: {e}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())