#!/usr/bin/env python3
"""
测试新的LLM驱动报告生成pipeline
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from llm_report_generator import LLMReportGenerator
from enhanced_report_generator import EnhancedReportGenerator
from report_validator import ReportValidator

def test_llm_pipeline():
    """测试LLM驱动pipeline"""
    print("=== 测试LLM驱动报告生成pipeline ===")
    
    try:
        # 初始化生成器
        generator = LLMReportGenerator()
        
        # 测试数据
        student_data = {
            "name": "Alex Chen",
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
                }
            ]
        }
        
        conversation_log = [
            {"role": "student", "content": "我喜欢组织活动和做科学实验"},
            {"role": "parent", "content": "孩子在学生会组织过环保义卖"}
        ]
        
        # 生成报告
        print("正在生成报告...")
        report_result = generator.generate_report(conversation_log, student_data)
        
        print("✅ LLM Pipeline报告生成成功!")
        print(f"页数: {report_result['metadata']['page_count']}")
        print(f"字数: {report_result['metadata']['word_count']}")
        print(f"校验分数: {report_result['validation']['overall_score']}/100")
        
        # 导出报告
        print("正在导出报告...")
        exported_files = generator.export_report(report_result, "all")
        
        print("\n导出文件:")
        for format_type, file_path in exported_files.items():
            print(f"  {format_type}: {file_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM Pipeline测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_pipeline():
    """测试增强版pipeline（支持两种模式）"""
    print("\n=== 测试增强版报告生成器 ===")
    
    try:
        # 测试LLM模式
        print("测试LLM模式...")
        generator_llm = EnhancedReportGenerator(use_llm_pipeline=True)
        
        student_data = {
            "name": "Alex Chen",
            "age": "14岁",
            "grade": "Grade 8",
            "gpa": "3.8/4.0",
            "academic_strengths": "数学、物理、计算机科学"
        }
        
        conversation_log = [
            {"role": "student", "content": "我喜欢组织活动和做科学实验"},
            {"role": "parent", "content": "孩子在学生会组织过环保义卖"}
        ]
        
        report_result = generator_llm.generate_comprehensive_report(conversation_log, student_data)
        print(f"✅ LLM模式成功 - 字数: {report_result['metadata']['word_count']}")
        
        # 测试传统模式
        print("测试传统模式...")
        generator_traditional = EnhancedReportGenerator(use_llm_pipeline=False)
        
        report_result_traditional = generator_traditional.generate_comprehensive_report(conversation_log, student_data)
        print(f"✅ 传统模式成功 - 字数: {report_result_traditional['metadata']['word_count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 增强版pipeline测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validator():
    """测试校验器"""
    print("\n=== 测试报告校验器 ===")
    
    try:
        validator = ReportValidator()
        
        # 测试内容
        test_content = """家庭与学生背景

Alex Chen是一名14岁的学生，目前在Grade 8就读。他的GPA为3.8/4.0，在数学、物理和计算机科学方面表现突出。

**学术表现**：
- 机器人竞赛省级二等奖
- 科技部副部长职务
- 环保义卖活动组织经验

学校申请定位

基于Alex的学术背景和兴趣，我们建议申请以下学校：
1. Upper Canada College
2. Havergal College
3. St. Andrew's College

学生—学校匹配度

Upper Canada College与Alex的匹配度较高，主要体现在：
- 学术环境优秀 ✅
- STEM项目丰富 🎯
- 文化氛围适合

学术与课外准备

建议Alex在以下方面进行准备：
- 加强英语写作能力
- 参与更多STEM竞赛
- 发展领导力技能

申请流程与个性化策略

申请时间线：
- 10月：完成SSAT考试
- 11月：提交申请材料
- 12月：参加面试

录取后延伸建议

如果成功录取，建议：
- 提前了解学校文化
- 准备学术衔接
- 建立社交网络
"""
        
        # 校验内容
        result = validator.validate_content(test_content)
        
        print(f"✅ 校验器测试成功!")
        print(f"总体分数: {result['overall_score']}/100")
        print(f"问题数量: {len(result['validation_issues'])}")
        print(f"需要润色: {result['needs_polish']}")
        
        if result['validation_issues']:
            print("问题列表:")
            for issue in result['validation_issues']:
                print(f"  - {issue}")
        
        # 测试清理功能
        cleaned_content = validator.sanitize_content(test_content)
        print(f"\n清理后内容长度: {len(cleaned_content)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 校验器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试新的报告生成pipeline...")
    
    results = []
    
    # 测试各个组件
    results.append(test_validator())
    results.append(test_llm_pipeline())
    results.append(test_enhanced_pipeline())
    
    # 总结测试结果
    print("\n=== 测试结果总结 ===")
    passed = sum(results)
    total = len(results)
    
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！新的LLM驱动pipeline已就绪。")
    else:
        print("⚠️ 部分测试失败，请检查错误信息。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
