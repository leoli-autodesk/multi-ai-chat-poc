#!/usr/bin/env python3
"""
测试Writer Agent
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from writer_agent import WriterAgent
from llm_report_generator import LLMReportGenerator

def test_writer_agent():
    """测试Writer Agent"""
    print("=== 测试Writer Agent ===")
    
    try:
        # 初始化Writer Agent
        writer = WriterAgent()
        
        # 测试数据（Writer Agent格式）
        test_data = {
            "student": {
                "name": "Alex Chen",
                "age": "14岁",
                "grade": "Grade 8",
                "gpa": "3.8/4.0",
                "academic_strengths": "数学、物理、计算机科学",
                "competition_achievements": "机器人竞赛省级二等奖",
                "leadership_positions": "科技部副部长",
                "project_experiences": "环保义卖活动组织",
                "learning_ability": "自主学习和问题解决",
                "adaptability": "跨文化环境适应"
            },
            "family": {
                "education_values": "重视全人教育，培养独立思考和创新能力",
                "goals": "希望孩子在国际化环境中全面发展",
                "culture": "中西文化融合，重视传统价值观",
                "support_level": "全力支持孩子的教育和发展",
                "expectations": "希望孩子成为有责任感的未来领导者",
                "resource_commitment": "愿意投入充足的时间和资源支持教育"
            },
            "positioning": {
                "parent_criteria": ["学术", "全人教育", "体育", "艺术"],
                "school_type_preference": "私立学校",
                "location_preference": "多伦多地区",
                "budget_range": "中等偏上"
            },
            "matching": {
                "weights": {"academic": 0.35, "activities": 0.25, "culture": 0.2, "personality": 0.2},
                "schools": [
                    {
                        "name": "Upper Canada College",
                        "facts": {"ratio": "8:1", "location": "Toronto", "tuition": 55000, "class_size": "20–25"},
                        "scores": {"academic": 5, "activities": 5, "culture": 5, "personality": 5},
                        "match_percentage": 92,
                        "advantages": ["STEM项目丰富", "学术环境优秀", "文化氛围适合"],
                        "challenges": ["竞争激烈", "需要更强的英语能力"],
                        "strategies": ["突出领导力", "展现STEM专长", "强调社区服务"]
                    },
                    {
                        "name": "Havergal College",
                        "facts": {"ratio": "7:1", "location": "Toronto", "tuition": 52000, "class_size": "18–22"},
                        "scores": {"academic": 4, "activities": 4, "culture": 5, "personality": 4},
                        "match_percentage": 88,
                        "advantages": ["全人教育理念", "艺术项目丰富", "女性领导力培养"],
                        "challenges": ["单性别环境", "需要适应期"],
                        "strategies": ["强调全面发展", "展现艺术才能", "突出领导力"]
                    }
                ],
                "ranking": [
                    {"name": "Upper Canada College", "reason": "学术和STEM项目匹配度最高"},
                    {"name": "Havergal College", "reason": "全人教育理念契合"},
                    {"name": "St. Andrew's College", "reason": "传统价值观与家庭背景匹配"}
                ]
            },
            "plans": {
                "academic_preparation": "加强英语写作能力，保持STEM优势",
                "extracurricular_preparation": "参与更多STEM竞赛，发展领导力",
                "test_preparation": "SSAT目标90th percentile以上"
            },
            "timeline": {
                "deadlines": ["10月完成SSAT考试", "11月提交申请材料", "12月参加面试"],
                "milestones": ["材料准备完成", "面试准备就绪", "最终提交"]
            },
            "tests": {
                "ssat": "目标90th percentile以上",
                "isee": "备选方案",
                "school_tests": "各校特色测试准备"
            },
            "essays_refs_interview": {
                "essay_themes": ["领导力经历", "STEM兴趣发展", "社区服务贡献"],
                "recommendation_strategy": "来自指导老师和社团负责人",
                "interview_preparation": "突出环保义卖活动经验和领导力"
            },
            "post_offer": {
                "transition_preparation": "提前了解学校文化和环境",
                "academic_planning": "准备学术衔接和课程选择",
                "social_networking": "建立社交网络和友谊"
            }
        }
        
        # 生成完整报告
        print("正在生成完整报告...")
        full_report = writer.compose_full_report(test_data)
        
        print("✅ Writer Agent报告生成成功!")
        print(f"总字数: {len(full_report)}")
        
        # 验证内容
        validation_result = writer.validate_content(full_report)
        print(f"验证结果: {validation_result}")
        
        # 统计章节字数
        section_counts = writer.count_section_words(full_report)
        print(f"章节字数: {section_counts}")
        
        # 记录日志
        writer.log_writer_summary(validation_result, section_counts)
        
        # 保存报告
        output_file = Path("output") / f"writer_agent_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_report)
        
        print(f"报告已保存到: {output_file}")
        
        # 显示报告预览
        print("\n=== 报告预览 ===")
        preview_lines = full_report.split('\n')[:20]
        for line in preview_lines:
            print(line)
        print("...")
        
        return True
        
    except Exception as e:
        print(f"❌ Writer Agent测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integrated_pipeline():
    """测试集成的pipeline"""
    print("\n=== 测试集成的LLM Pipeline ===")
    
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
        
        print("✅ 集成Pipeline报告生成成功!")
        print(f"页数: {report_result['metadata']['page_count']}")
        print(f"字数: {report_result['metadata']['word_count']}")
        print(f"校验结果: {report_result['validation']}")
        
        # 导出报告
        print("正在导出报告...")
        exported_files = generator.export_report(report_result, "all")
        
        print("\n导出文件:")
        for format_type, file_path in exported_files.items():
            print(f"  {format_type}: {file_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 集成Pipeline测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试Writer Agent...")
    
    results = []
    
    # 测试Writer Agent
    results.append(test_writer_agent())
    
    # 测试集成pipeline
    results.append(test_integrated_pipeline())
    
    # 总结测试结果
    print("\n=== 测试结果总结 ===")
    passed = sum(results)
    total = len(results)
    
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！Writer Agent已就绪。")
    else:
        print("⚠️ 部分测试失败，请检查错误信息。")
    
    return passed == total

if __name__ == "__main__":
    from datetime import datetime
    success = main()
    sys.exit(0 if success else 1)
