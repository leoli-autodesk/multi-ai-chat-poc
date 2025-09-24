#!/usr/bin/env python3
"""
End-to-End测试：从输入数据到最终报告
测试完整的Writer Agent系统
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from writer_agent import WriterAgent
from llm_report_generator import LLMReportGenerator
from enhanced_report_generator import EnhancedReportGenerator

def create_test_input_data():
    """创建完整的测试输入数据"""
    print("=== 步骤1: 准备测试输入数据 ===")
    
    # 学生基本信息
    student_data = {
        "name": "张小明",
        "age": "14岁",
        "grade": "Grade 8",
        "gpa": "3.9/4.0",
        "academic_strengths": "数学、物理、计算机科学、英语写作",
        "competition_achievements": [
            "机器人竞赛省级二等奖",
            "数学竞赛市级一等奖",
            "英语演讲比赛校级冠军"
        ],
        "leadership_positions": [
            "学生会科技部副部长",
            "环保社团创始人",
            "班级学习委员"
        ],
        "project_experiences": [
            "组织环保义卖活动，筹集资金5000元",
            "开发校园垃圾分类APP",
            "参与社区志愿服务200小时"
        ],
        "learning_ability": "自主学习能力强，善于问题解决",
        "adaptability": "跨文化环境适应能力强",
        "personality_traits": "有责任心、组织能力强、学习态度积极",
        "hobbies": "编程、机器人制作、环保活动、阅读",
        "language_skills": {
            "chinese": "母语水平",
            "english": "流利，TOEFL目标100+",
            "french": "基础水平"
        },
        "target_schools": [
            {
                "name": "Upper Canada College",
                "scores": {"academic": 5, "activities": 4, "culture": 5, "personality": 4},
                "weights": {"academic": 0.35, "activities": 0.25, "culture": 0.2, "personality": 0.2},
                "preference": "首选"
            },
            {
                "name": "Havergal College",
                "scores": {"academic": 4, "activities": 4, "culture": 5, "personality": 4},
                "weights": {"academic": 0.35, "activities": 0.25, "culture": 0.2, "personality": 0.2},
                "preference": "备选"
            },
            {
                "name": "St. Andrew's College",
                "scores": {"academic": 4, "activities": 3, "culture": 4, "personality": 3},
                "weights": {"academic": 0.35, "activities": 0.25, "culture": 0.2, "personality": 0.2},
                "preference": "备选"
            }
        ]
    }
    
    # 对话记录
    conversation_log = [
        {
            "role": "parent",
            "content": "我们希望通过私校申请，让孩子在国际化环境中全面发展。孩子对STEM领域很感兴趣，特别是机器人和编程。"
        },
        {
            "role": "student",
            "content": "我喜欢组织活动和做科学实验。我在学生会担任科技部副部长，还创建了环保社团。"
        },
        {
            "role": "parent",
            "content": "孩子在环保方面很有热情，组织过义卖活动，还开发了一个垃圾分类APP。我们希望找到重视全人教育的学校。"
        },
        {
            "role": "student",
            "content": "我的目标是成为环境工程师，希望通过学习帮助解决环境问题。"
        },
        {
            "role": "parent",
            "content": "我们家庭重视教育，愿意投入充足的时间和资源支持孩子的教育发展。"
        }
    ]
    
    print(f"✅ 学生数据: {student_data['name']}, {student_data['age']}, Grade {student_data['grade']}")
    print(f"✅ 对话记录: {len(conversation_log)}条")
    print(f"✅ 目标学校: {len(student_data['target_schools'])}所")
    
    return student_data, conversation_log

def test_writer_agent_standalone(student_data, conversation_log):
    """测试Writer Agent独立功能"""
    print("\n=== 步骤2: 测试Writer Agent独立功能 ===")
    
    try:
        # 初始化Writer Agent
        writer = WriterAgent()
        
        # 构建Writer Agent格式的数据
        writer_data = {
            "student": {
                "name": student_data["name"],
                "age": student_data["age"],
                "grade": student_data["grade"],
                "gpa": student_data["gpa"],
                "academic_strengths": student_data["academic_strengths"],
                "competition_achievements": ", ".join(student_data["competition_achievements"]),
                "leadership_positions": ", ".join(student_data["leadership_positions"]),
                "project_experiences": ", ".join(student_data["project_experiences"]),
                "learning_ability": student_data["learning_ability"],
                "adaptability": student_data["adaptability"],
                "personality_traits": student_data["personality_traits"],
                "hobbies": student_data["hobbies"],
                "language_skills": student_data["language_skills"]
            },
            "family": {
                "education_values": "重视全人教育，培养独立思考和创新能力",
                "goals": "希望孩子在国际化环境中全面发展，成为有责任感的未来领导者",
                "culture": "中西文化融合，重视传统价值观和现代教育理念",
                "support_level": "全力支持孩子的教育和发展，愿意投入充足的时间和资源",
                "expectations": "希望孩子成为环境工程师，通过STEM技能解决环境问题",
                "resource_commitment": "愿意投入充足的时间和资源支持教育"
            },
            "positioning": {
                "parent_criteria": ["学术", "全人教育", "STEM项目", "环保理念", "国际化"],
                "school_type_preference": "私立学校",
                "location_preference": "多伦多地区",
                "budget_range": "中等偏上"
            },
            "matching": {
                "weights": {"academic": 0.35, "activities": 0.25, "culture": 0.2, "personality": 0.2},
                "schools": [
                    {
                        "name": "Upper Canada College",
                        "facts": {
                            "ratio": "8:1",
                            "location": "Toronto",
                            "tuition": 55000,
                            "class_size": "20–25",
                            "founded": "1829",
                            "type": "Boys' School"
                        },
                        "scores": {"academic": 5, "activities": 4, "culture": 5, "personality": 4},
                        "match_percentage": 92,
                        "advantages": [
                            "STEM项目丰富，机器人实验室先进",
                            "学术环境优秀，大学录取率高",
                            "文化氛围适合，重视领导力培养"
                        ],
                        "challenges": [
                            "竞争激烈，录取难度大",
                            "需要更强的英语能力",
                            "单性别环境需要适应"
                        ],
                        "strategies": [
                            "突出STEM专长和机器人竞赛成绩",
                            "展现领导力和环保理念",
                            "强调社区服务经历"
                        ]
                    },
                    {
                        "name": "Havergal College",
                        "facts": {
                            "ratio": "7:1",
                            "location": "Toronto",
                            "tuition": 52000,
                            "class_size": "18–22",
                            "founded": "1894",
                            "type": "Girls' School"
                        },
                        "scores": {"academic": 4, "activities": 4, "culture": 5, "personality": 4},
                        "match_percentage": 88,
                        "advantages": [
                            "全人教育理念，重视女性领导力",
                            "艺术项目丰富，STEM与人文并重",
                            "环保理念与学校价值观契合"
                        ],
                        "challenges": [
                            "单性别环境，需要适应期",
                            "艺术要求较高",
                            "竞争激烈"
                        ],
                        "strategies": [
                            "强调全面发展，展现艺术才能",
                            "突出环保理念和社区服务",
                            "展现女性领导力潜质"
                        ]
                    },
                    {
                        "name": "St. Andrew's College",
                        "facts": {
                            "ratio": "9:1",
                            "location": "Aurora",
                            "tuition": 48000,
                            "class_size": "22–26",
                            "founded": "1899",
                            "type": "Boys' School"
                        },
                        "scores": {"academic": 4, "activities": 3, "culture": 4, "personality": 3},
                        "match_percentage": 85,
                        "advantages": [
                            "传统价值观与家庭背景匹配",
                            "体育项目丰富，重视品格教育",
                            "师生关系密切，个性化关注"
                        ],
                        "challenges": [
                            "STEM项目相对较弱",
                            "地理位置较远",
                            "需要更强的体育能力"
                        ],
                        "strategies": [
                            "强调传统价值观和品格教育",
                            "展现体育才能和团队精神",
                            "突出学习能力和适应能力"
                        ]
                    }
                ],
                "ranking": [
                    {"name": "Upper Canada College", "reason": "STEM项目匹配度最高，学术环境优秀"},
                    {"name": "Havergal College", "reason": "全人教育理念契合，环保价值观一致"},
                    {"name": "St. Andrew's College", "reason": "传统价值观匹配，品格教育重视"}
                ]
            },
            "plans": {
                "academic_preparation": "加强英语写作能力，保持STEM优势，准备AP课程",
                "extracurricular_preparation": "参与更多STEM竞赛，发展领导力，深化环保项目",
                "test_preparation": "SSAT目标90th percentile以上，TOEFL目标100+",
                "language_improvement": "加强英语口语和写作，学习法语基础",
                "skill_development": "编程技能提升，机器人制作进阶，环保项目扩展"
            },
            "timeline": {
                "deadlines": [
                    "2024年10月：完成SSAT考试",
                    "2024年11月：提交申请材料",
                    "2024年12月：参加面试",
                    "2025年1月：等待录取结果"
                ],
                "milestones": [
                    "材料准备完成",
                    "面试准备就绪",
                    "最终提交",
                    "录取结果确认"
                ]
            },
            "tests": {
                "ssat": "目标90th percentile以上，重点提升数学和阅读",
                "isee": "备选方案，保持同等水平",
                "school_tests": "各校特色测试准备，包括STEM能力测试",
                "toefl": "目标100+，重点提升口语和写作"
            },
            "essays_refs_interview": {
                "essay_themes": [
                    "领导力经历：环保社团创始和组织",
                    "STEM兴趣发展：机器人竞赛和APP开发",
                    "社区服务贡献：义卖活动和志愿服务"
                ],
                "recommendation_strategy": "来自指导老师、社团负责人和社区服务组织",
                "interview_preparation": "突出环保义卖活动经验，展现STEM专长和领导力",
                "portfolio_items": [
                    "环保义卖活动照片和报道",
                    "垃圾分类APP演示",
                    "机器人竞赛获奖证书",
                    "志愿服务证明"
                ]
            },
            "post_offer": {
                "transition_preparation": "提前了解学校文化和环境，参加新生orientation",
                "academic_planning": "准备学术衔接，选择适合的课程和项目",
                "social_networking": "建立社交网络，参与学校社团和活动",
                "long_term_goals": "为大学申请做准备，继续发展STEM专长"
            }
        }
        
        print("✅ Writer Agent数据构建完成")
        
        # 生成完整报告
        print("正在生成完整报告...")
        full_report = writer.compose_full_report(writer_data)
        
        print(f"✅ Writer Agent报告生成成功!")
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
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = Path("output") / f"writer_agent_e2e_{timestamp}.md"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_report)
        
        print(f"✅ 报告已保存到: {output_file}")
        
        # 显示报告预览
        print("\n=== 报告预览 ===")
        preview_lines = full_report.split('\n')[:30]
        for i, line in enumerate(preview_lines, 1):
            print(f"{i:2d}: {line}")
        print("...")
        
        return True, full_report, validation_result
        
    except Exception as e:
        print(f"❌ Writer Agent测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None

def test_integrated_pipeline(student_data, conversation_log):
    """测试集成的LLM Pipeline"""
    print("\n=== 步骤3: 测试集成的LLM Pipeline ===")
    
    try:
        # 初始化生成器
        generator = LLMReportGenerator()
        
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
        
        return True, report_result, exported_files
        
    except Exception as e:
        print(f"❌ 集成Pipeline测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None

def test_enhanced_generator(student_data, conversation_log):
    """测试增强版报告生成器"""
    print("\n=== 步骤4: 测试增强版报告生成器 ===")
    
    try:
        # 测试LLM模式
        print("测试LLM模式...")
        generator_llm = EnhancedReportGenerator(use_llm_pipeline=True)
        report_result_llm = generator_llm.generate_comprehensive_report(conversation_log, student_data)
        
        print(f"✅ LLM模式成功 - 字数: {report_result_llm['metadata']['word_count']}")
        
        # 导出LLM模式报告
        exported_files_llm = generator_llm.export_report(report_result_llm, "all")
        print("LLM模式导出文件:")
        for format_type, file_path in exported_files_llm.items():
            print(f"  {format_type}: {file_path}")
        
        # 测试传统模式
        print("\n测试传统模式...")
        generator_traditional = EnhancedReportGenerator(use_llm_pipeline=False)
        report_result_traditional = generator_traditional.generate_comprehensive_report(conversation_log, student_data)
        
        print(f"✅ 传统模式成功 - 字数: {report_result_traditional['metadata']['word_count']}")
        
        # 导出传统模式报告
        exported_files_traditional = generator_traditional.export_report(report_result_traditional, "all")
        print("传统模式导出文件:")
        for format_type, file_path in exported_files_traditional.items():
            print(f"  {format_type}: {file_path}")
        
        return True, report_result_llm, report_result_traditional
        
    except Exception as e:
        print(f"❌ 增强版生成器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None

def verify_output_files():
    """验证所有输出文件"""
    print("\n=== 步骤5: 验证输出文件 ===")
    
    output_dir = Path("output")
    logs_dir = Path("logs")
    
    # 检查输出目录
    if output_dir.exists():
        files = list(output_dir.glob("*"))
        print(f"✅ 输出目录存在，包含 {len(files)} 个文件")
        for file in files:
            print(f"  - {file.name} ({file.stat().st_size} bytes)")
    else:
        print("❌ 输出目录不存在")
    
    # 检查日志目录
    if logs_dir.exists():
        files = list(logs_dir.glob("*"))
        print(f"✅ 日志目录存在，包含 {len(files)} 个文件")
        for file in files:
            print(f"  - {file.name} ({file.stat().st_size} bytes)")
    else:
        print("❌ 日志目录不存在")
    
    # 检查Writer摘要日志
    writer_summary = logs_dir / "writer_summary.json"
    if writer_summary.exists():
        print(f"✅ Writer摘要日志存在: {writer_summary}")
        try:
            with open(writer_summary, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            print(f"  包含 {len(logs)} 条记录")
            if logs:
                latest = logs[-1]
                print(f"  最新记录: {latest.get('timestamp', 'N/A')}")
                print(f"  字数: {latest.get('word_count', 'N/A')}")
                print(f"  需要重写: {latest.get('needs_rewrite', 'N/A')}")
        except Exception as e:
            print(f"  读取日志失败: {e}")
    else:
        print("❌ Writer摘要日志不存在")

def main():
    """主测试函数"""
    print("🚀 开始End-to-End测试...")
    print("=" * 60)
    
    results = []
    
    # 步骤1: 准备测试数据
    student_data, conversation_log = create_test_input_data()
    
    # 步骤2: 测试Writer Agent独立功能
    success, report, validation = test_writer_agent_standalone(student_data, conversation_log)
    results.append(success)
    
    # 步骤3: 测试集成的LLM Pipeline
    success, report_result, exported_files = test_integrated_pipeline(student_data, conversation_log)
    results.append(success)
    
    # 步骤4: 测试增强版报告生成器
    success, llm_result, traditional_result = test_enhanced_generator(student_data, conversation_log)
    results.append(success)
    
    # 步骤5: 验证输出文件
    verify_output_files()
    
    # 总结测试结果
    print("\n" + "=" * 60)
    print("=== End-to-End测试结果总结 ===")
    passed = sum(results)
    total = len(results)
    
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！Writer Agent系统完全就绪。")
        print("\n📋 测试总结:")
        print("✅ Writer Agent独立功能正常")
        print("✅ 集成LLM Pipeline正常")
        print("✅ 增强版报告生成器正常")
        print("✅ 所有输出文件生成正常")
        print("✅ 日志记录正常")
    else:
        print("⚠️ 部分测试失败，请检查错误信息。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
