#!/usr/bin/env python3
"""
测试修复后的重复章节问题
验证Writer严格按照报告模板生成
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from llm_report_generator import LLMReportGenerator
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_fixed_section_deduplication():
    """测试修复后的重复章节问题"""
    print("🧪 开始测试修复后的重复章节问题...")
    
    # 初始化生成器
    generator = LLMReportGenerator()
    
    # 测试数据
    student_data = {
        "name": "李小明",
        "age": "15岁",
        "grade": "Grade 9",
        "gpa": "3.9/4.0",
        "academic_strengths": "数学、物理、化学",
        "competition_achievements": "数学竞赛全国一等奖",
        "leadership_positions": "学生会主席",
        "project_experiences": "科技创新项目",
        "learning_ability": "自主学习能力强",
        "adaptability": "适应能力强",
        "target_schools": [
            {
                "name": "Upper Canada College",
                "scores": {"academic": 5, "activities": 4, "culture": 4, "personality": 4},
                "weights": {"academic": 0.35, "activities": 0.25, "culture": 0.2, "personality": 0.2}
            },
            {
                "name": "Havergal College", 
                "scores": {"academic": 4, "activities": 4, "culture": 5, "personality": 4},
                "weights": {"academic": 0.35, "activities": 0.25, "culture": 0.2, "personality": 0.2}
            }
        ]
    }
    
    conversation_log = [
        {"role": "student", "content": "我热爱数学和科学，希望能在STEM领域发展"},
        {"role": "parent", "content": "孩子学习能力强，希望接受优质教育"},
        {"role": "student", "content": "我担任学生会主席，有领导经验"},
        {"role": "parent", "content": "我们重视全人教育，希望孩子全面发展"}
    ]
    
    try:
        # 生成报告（包含修复后的去重逻辑）
        print("📝 生成报告...")
        report_result = generator.generate_report(conversation_log, student_data)
        
        print("✅ 报告生成成功!")
        print(f"📊 报告统计:")
        print(f"   - 总字数: {report_result['metadata']['word_count']}")
        print(f"   - 页数: {report_result['metadata']['page_count']}")
        
        # 显示章节验证结果
        if 'section_validation' in report_result:
            section_val = report_result['section_validation']
            print(f"📋 章节验证结果:")
            print(f"   - 章节数量: {section_val['total_sections']}/6")
            print(f"   - 是否有效: {section_val['is_valid']}")
            print(f"   - 发现的章节: {', '.join(section_val['found_sections'])}")
            
            if section_val['missing_sections']:
                print(f"   - 缺失章节: {', '.join(section_val['missing_sections'])}")
        
        # 显示去重结果
        if 'dedupe_validation' in report_result:
            dedupe_val = report_result['dedupe_validation']
            print(f"🔄 去重结果:")
            print(f"   - 字数减少: {dedupe_val['reduction_percentage']:.1f}%")
            print(f"   - 符合标准: {dedupe_val['meets_criteria']}")
        
        # 导出报告
        print("\n📁 导出报告...")
        exported_files = generator.export_report(report_result, "all")
        
        print("📋 导出文件:")
        for format_type, file_path in exported_files.items():
            print(f"   - {format_type}: {file_path}")
        
        # 显示部分内容
        print("\n📖 报告内容预览:")
        content_lines = report_result['content'].split('\n')
        section_count = 0
        for i, line in enumerate(content_lines[:50]):  # 显示前50行
            if line.strip():
                # 检查是否是章节标题
                if line in ["家庭与学生背景", "学校申请定位", "学生—学校匹配度", 
                           "学术与课外准备", "申请流程与个性化策略", "录取后延伸建议"]:
                    section_count += 1
                    print(f"   📌 第{section_count}章: {line}")
                else:
                    print(f"   {line}")
        
        if len(content_lines) > 50:
            print(f"   ... (还有 {len(content_lines) - 50} 行)")
        
        print(f"\n📊 章节统计: 发现 {section_count} 个章节标题")
        
        print("\n🎉 修复后的重复章节问题测试完成!")
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        print(f"❌ 测试失败: {e}")
        raise

def test_section_deduplication_only():
    """单独测试章节去重功能"""
    print("🧪 单独测试章节去重功能...")
    
    from writer_agent import WriterAgent
    
    writer = WriterAgent()
    
    # 测试文本（包含重复章节）
    test_text = """
    家庭与学生背景
    
    李小明同学现年15岁，就读于Grade 9，在学术方面表现优异。
    
    学校申请定位
    
    基于李小明的学术优势，我们推荐申请多伦多地区的顶级私立学校。
    
    学生—学校匹配度
    
    Upper Canada College是李小明的首选学校，匹配度达到95%。
    
    学术与课外准备
    
    在学术准备方面，李小明需要加强英语写作能力。
    
    申请流程与个性化策略
    
    申请时间线包括：10月完成SSAT考试，11月提交申请材料。
    
    录取后延伸建议
    
    录取后，李小明应该提前了解学校文化。
    
    家庭与学生背景
    
    重复的家庭背景内容...
    
    学校申请定位
    
    重复的申请定位内容...
    
    学生—学校匹配度
    
    重复的匹配度内容...
    """
    
    # 执行章节去重
    result = writer.deduplicate_sections(test_text)
    
    # 验证结果
    validation = writer.validate_section_count(result)
    
    print("📊 章节去重结果:")
    print(f"   - 发现章节数: {validation['total_sections']}")
    print(f"   - 期望章节数: {validation['expected_sections']}")
    print(f"   - 是否有效: {validation['is_valid']}")
    print(f"   - 发现的章节: {', '.join(validation['found_sections'])}")
    
    if validation['missing_sections']:
        print(f"   - 缺失章节: {', '.join(validation['missing_sections'])}")
    
    print("\n📖 去重后内容预览:")
    result_lines = result.split('\n')
    for i, line in enumerate(result_lines[:30]):  # 显示前30行
        if line.strip():
            print(f"   {line}")
    
    if len(result_lines) > 30:
        print(f"   ... (还有 {len(result_lines) - 30} 行)")
    
    print("\n✅ 章节去重功能测试完成!")

if __name__ == "__main__":
    print("🚀 修复后的重复章节问题测试")
    print("="*50)
    
    # 选择测试模式
    if len(sys.argv) > 1 and sys.argv[1] == "--dedupe-only":
        test_section_deduplication_only()
    else:
        test_fixed_section_deduplication()
    
    print("\n" + "="*50)
    print("🎯 测试完成！")
