#!/usr/bin/env python3
"""
私校申请顾问AI协作系统 - 主程序
简化版本，支持命令行输入文件处理
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """主程序入口"""
    print("🎯 私校申请顾问AI协作系统")
    print("=" * 50)
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python3 src/main.py <输入文件路径>")
        print("  python3 src/main.py <输入文件路径> -o <输出目录>")
        print("")
        print("示例:")
        print("  python3 src/main.py input.txt")
        print("  python3 src/main.py input.txt -o output/my_result")
        sys.exit(1)
    
    # 检查必要目录
    ensure_directories()
    
    # 启动简化处理器
    start_simple_processor()

def ensure_directories():
    """确保必要的目录存在"""
    directories = [
        'output',
        'config/bots',
        'config/schools', 
        'config/templates',
        'tests'
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ 目录已准备: {dir_path}")

def start_simple_processor():
    """启动简化处理器"""
    print("\n🚀 启动简化处理器...")
    print("📁 处理输入文件并生成报告")
    print("📊 结果将保存到 output/ 目录")
    print("")
    
    # 导入并运行简化处理器
    try:
        from simple_processor import SimpleProcessor
        import argparse
        
        # 解析命令行参数
        parser = argparse.ArgumentParser(description='私校申请顾问AI协作系统')
        parser.add_argument('input_file', help='输入文件路径')
        parser.add_argument('-o', '--output', help='输出目录 (默认: output/<timestamp>)')
        parser.add_argument('--rounds', type=int, default=10, help='对话轮数 (默认: 10)')
        
        args = parser.parse_args()
        
        # 检查输入文件
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"❌ 错误: 输入文件不存在: {input_path}")
            sys.exit(1)
        
        # 确定输出目录
        if args.output:
            output_dir = Path(args.output)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path("output") / timestamp
        
        # 创建输出目录
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建处理器并运行
        processor = SimpleProcessor()
        success = processor.process_conversation(str(input_path), str(output_dir))
        
        if success:
            print(f"\n🎉 处理成功完成！")
            print(f"📁 结果保存在: {output_dir}")
            print(f"📄 包含文件:")
            for file_path in output_dir.glob('*.txt'):
                print(f"   - {file_path.name}")
        else:
            print(f"\n❌ 处理失败")
            sys.exit(1)
            
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 运行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()