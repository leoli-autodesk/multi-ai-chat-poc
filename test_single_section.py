#!/usr/bin/env python3
"""
测试Writer Agent单个章节生成
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from writer_agent import WriterAgent

def test_single_section():
    """测试单个章节生成"""
    print("=== 测试Writer Agent单个章节生成 ===")
    
    writer = WriterAgent()
    
    # 测试数据
    section_data = {
        "student": {
            "name": "张小明",
            "age": "14岁",
            "grade": "Grade 8",
            "gpa": "3.9/4.0",
            "academic_strengths": "数学、物理、计算机科学、英语写作",
            "competition_achievements": "机器人竞赛省级二等奖，数学竞赛市级一等奖",
            "leadership_positions": "学生会科技部副部长，环保社团创始人",
            "project_experiences": "组织环保义卖活动，筹集资金5000元，开发校园垃圾分类APP"
        },
        "family": {
            "education_values": "重视全人教育，培养独立思考和创新能力",
            "goals": "希望孩子在国际化环境中全面发展，成为有责任感的未来领导者",
            "culture": "中西文化融合，重视传统价值观和现代教育理念"
        }
    }
    
    # 生成家庭与学生背景章节
    print("正在生成'家庭与学生背景'章节...")
    content = writer.write_section("家庭与学生背景", section_data, 900, 1100)
    
    print(f"生成内容长度: {len(content)}")
    print(f"生成内容预览:")
    print("-" * 50)
    print(content[:500])
    print("-" * 50)
    
    # 验证内容
    validation = writer.validate_content(content)
    print(f"验证结果: {validation}")
    
    return content

if __name__ == "__main__":
    test_single_section()
