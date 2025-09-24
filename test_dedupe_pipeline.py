#!/usr/bin/env python3
"""
测试去重精修流水线
验证Writer约束升级和去重精修功能
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

def test_dedupe_pipeline():
    """测试去重精修流水线"""
    print("🧪 开始测试去重精修流水线...")
    
    # 初始化生成器
    generator = LLMReportGenerator()
    
    # 测试数据（包含重复内容）
    student_data = {
        "name": "张小明",
        "age": "14岁",
        "grade": "Grade 8",
        "gpa": "3.8/4.0",
        "academic_strengths": "数学、物理、计算机科学",
        "competition_achievements": "机器人竞赛省级二等奖",
        "leadership_positions": "科技部副部长",
        "project_experiences": "环保义卖活动组织",
        "learning_ability": "自主学习和问题解决",
        "adaptability": "跨文化环境适应",
        "target_schools": [
            {
                "name": "Upper Canada College",
                "scores": {"academic": 4, "activities": 4, "culture": 5, "personality": 4},
                "weights": {"academic": 0.35, "activities": 0.25, "culture": 0.2, "personality": 0.2}
            },
            {
                "name": "Havergal College", 
                "scores": {"academic": 4, "activities": 3, "culture": 4, "personality": 3},
                "weights": {"academic": 0.35, "activities": 0.25, "culture": 0.2, "personality": 0.2}
            },
            {
                "name": "St. Andrew's College",
                "scores": {"academic": 3, "activities": 4, "culture": 4, "personality": 4},
                "weights": {"academic": 0.35, "activities": 0.25, "culture": 0.2, "personality": 0.2}
            }
        ]
    }
    
    conversation_log = [
        {"role": "student", "content": "我喜欢组织活动和做科学实验，特别是机器人编程"},
        {"role": "parent", "content": "孩子在学生会组织过环保义卖，展现了很好的领导力"},
        {"role": "student", "content": "我希望能在STEM领域继续发展，特别是数学和物理"},
        {"role": "parent", "content": "我们家庭重视全人教育，希望孩子在国际化环境中全面发展"}
    ]
    
    try:
        # 生成报告（包含去重精修）
        print("📝 生成报告...")
        report_result = generator.generate_report(conversation_log, student_data)
        
        print("✅ 报告生成成功!")
        print(f"📊 报告统计:")
        print(f"   - 总字数: {report_result['metadata']['word_count']}")
        print(f"   - 页数: {report_result['metadata']['page_count']}")
        
        # 显示去重结果
        if 'dedupe_validation' in report_result:
            dedupe_val = report_result['dedupe_validation']
            print(f"🔄 去重结果:")
            print(f"   - 字数减少: {dedupe_val['reduction_percentage']:.1f}%")
            print(f"   - 符合标准: {dedupe_val['meets_criteria']}")
            
            if dedupe_val.get('issues'):
                print(f"   - 问题: {', '.join(dedupe_val['issues'])}")
        
        # 导出报告
        print("\n📁 导出报告...")
        exported_files = generator.export_report(report_result, "all")
        
        print("📋 导出文件:")
        for format_type, file_path in exported_files.items():
            print(f"   - {format_type}: {file_path}")
        
        # 显示部分内容
        print("\n📖 报告内容预览:")
        content_lines = report_result['content'].split('\n')
        for i, line in enumerate(content_lines[:20]):  # 显示前20行
            if line.strip():
                print(f"   {line}")
        
        if len(content_lines) > 20:
            print(f"   ... (还有 {len(content_lines) - 20} 行)")
        
        print("\n🎉 去重精修流水线测试完成!")
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        print(f"❌ 测试失败: {e}")
        raise

def test_dedupe_module_only():
    """单独测试去重模块"""
    print("🧪 单独测试去重模块...")
    
    from dedupe import DedupeAndPolish
    
    dedupe = DedupeAndPolish()
    
    # 测试文本（包含重复内容）
    test_text = """
    家庭与学生背景

    张小明是一名14岁的八年级学生，在数学、物理和计算机科学方面表现突出。他的GPA为3.8/4.0，在机器人竞赛中获得省级二等奖。作为科技部副部长，他展现了出色的领导力和组织能力。

    学校申请定位

    基于张小明的学术优势和家庭价值观，我们推荐申请多伦多地区的顶级私立学校。这些学校在学术卓越、领导力培养、校友网络强大方面具有显著优势。

    学生—学校匹配度

    对于Upper Canada College，张小明在学术能力方面表现突出，与学校特色高度契合。该校的STEM项目丰富，能够充分发挥张小明的数学和物理专长。推荐理由包括：学术卓越、领导力培养、校友网络强大。潜在挑战是竞争激烈，需要更强的英语能力。

    对于Havergal College，张小明同样在学术能力方面表现突出，与学校特色高度契合。该校注重全人教育理念，与张小明的家庭价值观匹配。推荐理由包括：学术卓越、领导力培养、校友网络强大。潜在挑战是申请难度较高。

    对于St. Andrew's College，张小明在学术能力方面表现突出，与学校特色高度契合。该校的传统价值观与张小明的家庭背景匹配。推荐理由包括：学术卓越、领导力培养、校友网络强大。潜在挑战是需要适应寄宿生活。

    学术与课外准备

    在学术准备方面，建议张小明加强英语写作能力，保持STEM优势。在课外活动方面，建议参与更多STEM竞赛，发展领导力。在考试准备方面，SSAT目标90th percentile以上。

    申请流程与个性化策略

    申请时间线包括：10月完成SSAT考试，11月提交申请材料，12月参加面试。个性化策略包括：突出领导力，展现STEM专长，强调社区服务。

    录取后延伸建议

    录取后建议：提前了解学校文化，准备学术衔接，建立社交网络。我们的专业价值在于提供全方位的申请指导，确保成功保障。
    """
    
    ctx = {
        "sectionAnchors": ["家庭与学生背景", "学校申请定位", "学生—学校匹配度", 
                         "学术与课外准备", "申请流程与个性化策略", "录取后延伸建议"]
    }
    
    # 执行去重
    result = dedupe.dedupe_and_polish(test_text, ctx)
    
    # 验证结果
    validation = dedupe.validate_dedupe_result(test_text, result)
    
    print("📊 去重结果:")
    print(f"   - 原文长度: {validation['original_length']}")
    print(f"   - 去重后长度: {validation['deduped_length']}")
    print(f"   - 减少字数: {validation['length_reduction']}")
    print(f"   - 减少比例: {validation['reduction_percentage']:.1f}%")
    print(f"   - 符合标准: {validation['meets_criteria']}")
    
    if validation['issues']:
        print("   - 问题:")
        for issue in validation['issues']:
            print(f"     * {issue}")
    
    print("\n📖 去重后内容预览:")
    result_lines = result.split('\n')
    for i, line in enumerate(result_lines[:15]):  # 显示前15行
        if line.strip():
            print(f"   {line}")
    
    if len(result_lines) > 15:
        print(f"   ... (还有 {len(result_lines) - 15} 行)")
    
    print("\n✅ 去重模块测试完成!")

if __name__ == "__main__":
    print("🚀 去重精修流水线测试")
    print("="*50)
    
    # 选择测试模式
    if len(sys.argv) > 1 and sys.argv[1] == "--dedupe-only":
        test_dedupe_module_only()
    else:
        test_dedupe_pipeline()
    
    print("\n" + "="*50)
    print("🎯 测试完成！")
