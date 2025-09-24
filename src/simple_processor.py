#!/usr/bin/env python3
"""
私校申请顾问AI协作系统 - 简化版
从命令行接收输入文件路径，自动处理并生成报告
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bot_manager import BotManager
from flow_based_router import FlowBasedRouter
from cursor_ai import CursorAI
from src.report_generator import ProfessionalReportGenerator
from src.word_report_generator import WordReportGenerator

class SimpleProcessor:
    """简化版处理器"""
    
    def __init__(self):
        self.bot_manager = None
        self.router = None
        self.ai = None
        self.report_generator = None
        self.word_generator = None
        
    def initialize_components(self):
        """初始化组件"""
        try:
            print("🔧 正在初始化组件...")
            self.bot_manager = BotManager("bots/configs")
            self.router = FlowBasedRouter(self.bot_manager)
            self.ai = CursorAI({})
            self.report_generator = ProfessionalReportGenerator("config")
            self.word_generator = WordReportGenerator()
            print("✅ 组件初始化完成")
            return True
        except Exception as e:
            print(f"❌ 组件初始化失败: {e}")
            return False
    
    def process_conversation(self, input_file_path, output_dir):
        """处理对话并生成报告"""
        try:
            print(f"📁 输入文件: {input_file_path}")
            print(f"📁 输出目录: {output_dir}")
            
            # 初始化组件
            if not self.initialize_components():
                raise Exception("组件初始化失败")
            
            print("\n🎯 开始对话处理...")
            
            # 运行对话
            conversation_log = []
            total_rounds = 10
            context = []
            
            for round_num in range(1, total_rounds + 1):
                print(f"   第{round_num}轮对话...", end=" ")
                
                # 执行对话
                round_messages = self.router.run_complete_round(
                    context=context,
                    needed_info=[],
                    round_num=round_num,
                    ai_interface=self.ai,
                    config={},
                    school_data={},
                    conversations={}
                )
                
                # 提取消息
                if isinstance(round_messages, dict) and 'messages' in round_messages:
                    messages = round_messages['messages']
                else:
                    messages = round_messages if isinstance(round_messages, list) else []
                
                conversation_log.extend(messages)
                context.extend(messages)
                
                print(f"✅ 完成 ({len(messages)}条消息)")
                
                # 短暂延迟
                time.sleep(0.1)
            
            print(f"\n📊 对话完成，总共生成了{len(conversation_log)}条消息")
            
            # 生成报告
            print("📝 正在生成报告...")
            
            # 准备学生数据
            student_data = {
                "name": "Alex Chen",
                "age": "14岁",
                "grade": "Grade 8",
                "gpa": "3.8/4.0",
                "target_schools": "Upper Canada College, Havergal College, St. Andrew's College"
            }
            
            # 生成报告
            report_content = self.report_generator.generate_report(conversation_log, student_data)
            
            # 保存文件
            self.save_results(input_file_path, conversation_log, report_content, output_dir)
            
            print("✅ 处理完成！")
            return True
            
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            return False
    
    def save_results(self, input_file_path, conversation_log, report_content, output_dir):
        """保存处理结果"""
        output_path = Path(output_dir)
        
        # 复制输入文件
        input_filename = Path(input_file_path).name
        output_input_path = output_path / "input.txt"
        
        with open(input_file_path, 'r', encoding='utf-8') as f:
            input_content = f.read()
        
        with open(output_input_path, 'w', encoding='utf-8') as f:
            f.write(input_content)
        
        print(f"✅ 保存输入文件: {output_input_path}")
        
        # 保存对话记录
        chat_path = output_path / "chat.txt"
        with open(chat_path, 'w', encoding='utf-8') as f:
            for i, message in enumerate(conversation_log, 1):
                role = message.get('role', 'Unknown')
                content = message.get('content', '')
                f.write(f"=== 第{i}条消息 ===\n")
                f.write(f"角色: {role}\n")
                f.write(f"内容: {content}\n\n")
        
        print(f"✅ 保存对话记录: {chat_path}")
        
        # 保存报告
        report_path = output_path / "report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ 保存报告: {report_path}")
        
        # 生成Word报告
        print("📄 正在生成Word报告...")
        word_report_path = output_path / "report.docx"
        
        # 准备学生数据
        student_data = {
            "name": "Alex Chen",
            "age": "14岁",
            "grade": "Grade 8",
            "gpa": "3.8/4.0",
            "target_schools": "Upper Canada College, Havergal College, St. Andrew's College"
        }
        
        word_result = self.word_generator.generate_word_report(
            report_content, student_data, str(word_report_path)
        )
        
        if word_result:
            print(f"✅ 保存Word报告: {word_report_path}")
        else:
            print("⚠️ Word报告生成失败，但txt报告已保存")
        
        # 保存处理总结
        summary_path = output_path / "summary.txt"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        summary_content = f"""================================================================================
私校申请顾问AI协作系统 - 处理总结
================================================================================

处理时间: {timestamp}
输入文件: {input_filename}
输出目录: {output_dir}

处理结果:
- 对话轮数: 10轮
- 消息总数: {len(conversation_log)}条
- 报告长度: {len(report_content)}字符

生成文件:
- input.txt: 输入文件副本
- chat.txt: 完整对话记录
- report.txt: 申请策略报告 (Markdown格式)
- report.docx: 申请策略报告 (Word格式)
- summary.txt: 处理总结

================================================================================
处理完成！
================================================================================
"""
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"✅ 保存处理总结: {summary_path}")

def main():
    """主函数"""
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
    
    print("🎯 私校申请顾问AI协作系统")
    print("=" * 50)
    
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

if __name__ == '__main__':
    main()
