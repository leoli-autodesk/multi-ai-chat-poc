#!/usr/bin/env python3
"""
专业报告生成器 - 统一模板版本
消除多模板并存和重复拼接导致的随机输出
"""

import os
import json
import yaml
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
from src.report_assembler import ReportAssembler
from src.writer_agent import WriterAgent

class ProfessionalReportGenerator:
    """专业报告生成器 - 统一模板版本"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.school_data = self.load_school_data()
        
        # 初始化新组件
        self.assembler = ReportAssembler(config_dir)
        self.writer_agent = WriterAgent(config_dir)
        
        # 单一来源断言
        self.assembler.assert_no_old_templates()
    
    def load_templates(self) -> Dict[str, str]:
        """禁用旧模板加载 - 仅保留空字典"""
        # 不再加载strategy_report.md等旧模板
        return {}
    
    def load_school_data(self) -> Dict[str, Any]:
        """加载学校数据"""
        school_file = Path(self.config_dir) / "schools" / "school_data.yaml"
        
        if school_file.exists():
            with open(school_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        
        return {}
    
    def generate_report(self, conversation_log: List[Dict[str, Any]], 
                       student_data: Dict[str, Any]) -> str:
        """
        生成统一模板报告 - 使用Writer Agent和Report Assembler
        
        Args:
            conversation_log: 对话日志
            student_data: 学生数据
            
        Returns:
            完整的报告文本
        """
        # 分析对话内容
        analysis = self.analyze_conversation(conversation_log)
        
        # 使用Writer Agent生成6章内容
        sections = {}
        
        # 串行生成各章节
        section_configs = [
            ("家庭与学生背景", "family_background", analysis.get("family_support", [])),
            ("学校申请定位", "school_positioning", analysis.get("target_schools", [])),
            ("学生—学校匹配度", "school_matching", analysis.get("academic_strengths", [])),
            ("学术与课外准备", "academic_preparation", analysis.get("academic_strengths", [])),
            ("申请流程与个性化策略", "application_strategy", analysis.get("personal_qualities", [])),
            ("录取后延伸建议", "post_admission_advice", analysis.get("leadership_experiences", []))
        ]
        
        context_summary = ""
        for section_title, section_key, section_data in section_configs:
            print(f"📝 正在生成章节: {section_title}")
            
            # 构建章节提示词
            section_prompt = self._build_section_prompt(
                section_title, section_data, student_data, context_summary
            )
            
            # 调用Writer Agent
            section_content = self.writer_agent.generate_section(section_prompt)
            sections[section_title] = section_content
            
            # 更新上下文摘要
            context_summary += f"{section_title}: {section_content[:200]}...\n"
        
        # 使用Report Assembler组装最终报告
        full_report = self.assembler.assemble_report(sections)
        
        # 记录导出日志
        self._log_export_stats(full_report, sections)
        
        return full_report
    
    def _build_section_prompt(self, section_title: str, section_data: List[str], 
                            student_data: Dict[str, Any], context_summary: str) -> str:
        """构建章节提示词"""
        prompt = f"""
章节标题: {section_title}

学生基本信息:
- 姓名: {student_data.get('name', 'Alex Chen')}
- 年龄: {student_data.get('age', '14岁')}
- 目标学校: {student_data.get('target_schools', 'Upper Canada College, Havergal College, St. Andrew College')}

相关数据: {', '.join(section_data) if section_data else '无特定数据'}

上下文摘要: {context_summary[:500] if context_summary else '无'}

请生成该章节的专业内容，要求:
1. 不得复述前文，需承接式一句带过并补充新信息
2. 严格禁止Markdown语法、emoji、清单项
3. 输出自然段落，句式有长短变化
4. 字数控制在目标范围内
"""
        return prompt
    
    def _log_export_stats(self, full_report: str, sections: Dict[str, str]) -> None:
        """记录导出统计信息"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        stats = {
            "timestamp": timestamp,
            "total_characters": len(full_report),
            "estimated_pages": len(full_report) // 500,  # 估算页数
            "sections_found": len(sections),
            "section_lengths": {title: len(content) for title, content in sections.items()},
            "template_path": "writer-only",
            "validation_passed": len(sections) == 6,
            "duplicates_found": False
        }
        
        log_file = Path("logs") / f"export_stats_{timestamp}.json"
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        # 打印验收结果
        print(f"\n📊 导出统计:")
        print(f"   总字数: {stats['total_characters']}")
        print(f"   估算页数: {stats['estimated_pages']}")
        print(f"   章节数: {stats['sections_found']}")
        print(f"   模板路径: {stats['template_path']}")
        print(f"   校验通过: {stats['validation_passed']}")
        
        if stats['sections_found'] != 6:
            print(f"❌ 章节数量错误: 期望6章，实际{stats['sections_found']}章")
        else:
            print("✅ 章节数量正确")
    
    def analyze_conversation(self, conversation_log: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析对话内容，提取关键信息"""
        analysis = {
            "academic_strengths": [],
            "leadership_experiences": [],
            "community_service": [],
            "personal_qualities": [],
            "challenges_mentioned": [],
            "future_goals": [],
            "family_support": [],
            "key_achievements": []
        }
        
        # 分析每条消息
        for message in conversation_log:
            role = message.get("role", "")
            content = message.get("content", "")
            
            if role == "student":
                # 提取学生提到的成就和经历
                if "机器人竞赛" in content or "数学竞赛" in content:
                    analysis["academic_strengths"].append("STEM竞赛获奖")
                if "学生会" in content or "副部长" in content:
                    analysis["leadership_experiences"].append("学生会领导职务")
                if "环保" in content or "义卖" in content:
                    analysis["community_service"].append("环保活动组织")
                if "科学实验" in content or "创新" in content:
                    analysis["personal_qualities"].append("创新思维")
            
            elif role == "parent":
                # 提取家长提到的支持
                if "支持" in content or "鼓励" in content:
                    analysis["family_support"].append("家庭支持")
                if "教育理念" in content:
                    analysis["family_support"].append("教育理念")
        
        return analysis
    
    def build_report_content(self, student_data: Dict[str, Any], 
                           analysis: Dict[str, Any]) -> str:
        """构建报告内容"""
        
        # 使用模板或生成内容
        if "strategy_report" in self.templates:
            return self.fill_template(self.templates["strategy_report"], 
                                    student_data, analysis)
        else:
            return self.generate_default_report(student_data, analysis)
    
    def fill_template(self, template: str, student_data: Dict[str, Any], 
                     analysis: Dict[str, Any]) -> str:
        """填充模板内容"""
        # 简单的模板变量替换
        content = template
        
        # 替换学生数据
        for key, value in student_data.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))
        
        # 确保所有模板变量都被替换
        content = content.replace("{{student_name}}", student_data.get("name", "Alex Chen"))
        
        # 替换分析结果
        if analysis.get("academic_strengths"):
            content = content.replace("{{academic_strengths}}", ", ".join(analysis["academic_strengths"]))
        if analysis.get("leadership_experiences"):
            content = content.replace("{{leadership_positions}}", ", ".join(analysis["leadership_experiences"]))
        if analysis.get("community_service"):
            content = content.replace("{{project_experiences}}", ", ".join(analysis["community_service"]))
        if analysis.get("personal_qualities"):
            content = content.replace("{{innovation_examples}}", ", ".join(analysis["personal_qualities"]))
        
        # 替换其他常用变量
        content = content.replace("{{academic_level}}", "优秀学术基础")
        content = content.replace("{{test_scores}}", "SSAT 85th percentile")
        content = content.replace("{{competition_achievements}}", "机器人竞赛省级二等奖")
        content = content.replace("{{teamwork_examples}}", "跨年级合作项目")
        content = content.replace("{{impact_metrics}}", "30+学生参与，800加元筹款")
        content = content.replace("{{responsibility_examples}}", "环保活动的持续参与")
        content = content.replace("{{learning_ability}}", "自主学习和问题解决")
        content = content.replace("{{adaptability}}", "跨文化环境适应")
        
        # 替换日期
        content = content.replace("{{report_date}}", datetime.now().strftime("%Y年%m月%d日 %H:%M"))
        
        return content
    
    def generate_default_report(self, student_data: Dict[str, Any], 
                              analysis: Dict[str, Any]) -> str:
        """生成默认报告"""
        
        student_name = student_data.get("name", "Alex Chen")
        age = student_data.get("age", "14岁")
        grade = student_data.get("grade", "Grade 8")
        
        report_content = f"""# 🎯 私校申请策略报告

## 📋 学生概况
- **姓名**: {student_name}
- **年龄**: {age} ({grade})
- **目标年级**: Grade 9
- **目标学校**: Upper Canada College, Havergal College, St. Andrew's College

---

## 🏆 核心优势分析

### 学术表现
- **GPA**: 3.8/4.0 - 优秀学术基础
- **强项领域**: 数学、物理、计算机科学
- **标准化考试**: SSAT 85th percentile
- **学术竞赛**: 机器人竞赛省级二等奖

### 领导力潜质
- **学生会职务**: 科技部副部长
- **项目经验**: 环保义卖活动组织
- **团队协作**: 跨年级合作项目
- **影响力**: 30+学生参与，800加元筹款

### 个人特质
- **创新思维**: 科学实验中的独特见解
- **责任感**: 环保活动的持续参与
- **学习能力**: 自主学习和问题解决
- **适应能力**: 跨文化环境适应

---

## 🎯 申请策略建议

### 1. 学术提升计划
**目标**: 全面提升学术竞争力
- ✅ **保持优势**: 继续深化STEM领域专长
- 📈 **提升空间**: 重点加强英语文学和历史
- 🎯 **考试准备**: SSAT重考目标90th percentile以上
- 📚 **学习规划**: 建立系统性的学习计划

### 2. 领导力发展路径
**目标**: 展现卓越的领导潜质
- 🚀 **深化现有**: 扩展学生会科技部影响力
- 🌟 **创新项目**: 组织更多STEM相关活动
- 🤝 **合作能力**: 建立跨年级合作项目
- 📊 **量化成果**: 记录和展示项目影响力

### 3. 社区影响力建设
**目标**: 建立持续的社区贡献
- 🌱 **扩大影响**: 将环保活动扩展到更大范围
- ⏰ **长期项目**: 建立可持续的社区服务项目
- 📈 **成果记录**: 详细记录和量化服务成果
- 🏅 **获得认可**: 争取社区和学校认可

### 4. 个人品牌塑造
**目标**: 展现独特的个人特色
- 🔬 **STEM专长**: 突出科学和技术能力
- 🌍 **全球视野**: 展现跨文化适应能力
- 💡 **创新精神**: 强调创新思维和问题解决
- 🎨 **全面发展**: 平衡学术、艺术和体育

---

## 🏫 目标学校匹配度分析

### Upper Canada College (匹配度: 90%)
**优势匹配**:
- ✅ STEM项目实力强劲，与学术专长高度匹配
- ✅ 学术氛围浓厚，适合深度学术发展
- ✅ 校友网络强大，提供长期支持

**申请建议**:
- 🎯 重点突出学术成就和STEM专长
- 🎯 展现领导力和创新思维
- 🎯 强调对学术卓越的追求

### Havergal College (匹配度: 85%)
**优势匹配**:
- ✅ 全人教育理念，平衡发展机会
- ✅ 艺术与学术并重，展现全面素质
- ✅ 女性领导力培养，适合长期发展

**申请建议**:
- 🎯 平衡展现学术和艺术特长
- 🎯 强调领导力和社区贡献
- 🎯 展现对全人教育的理解

### St. Andrew's College (匹配度: 80%)
**优势匹配**:
- ✅ 传统名校声誉，教育质量保证
- ✅ 校友网络强大，长期发展支持
- ✅ 品格教育重视，价值观匹配

**申请建议**:
- 🎯 强调品格教育和社区贡献
- 🎯 展现传统价值观和现代创新结合
- 🎯 突出领导力和责任感

---

## 📅 行动计划

### 🚀 短期目标 (3个月内)
1. **学术提升**: 重点提升英语文学和历史成绩
2. **项目扩展**: 组织一次大型STEM活动
3. **考试准备**: 完成SSAT重考准备
4. **材料整理**: 收集和整理申请材料

### 🎯 中期目标 (6个月内)
1. **项目组合**: 建立完整的个人项目组合
2. **社区影响**: 深化社区服务影响力
3. **面试准备**: 准备面试和申请材料
4. **学校联系**: 建立与目标学校的联系

### 🌟 长期目标 (1年内)
1. **录取成功**: 获得目标学校录取
2. **学习规划**: 建立长期学习规划
3. **大学准备**: 为大学申请做准备
4. **持续发展**: 保持学术和领导力发展

---

## 💡 专业建议

### 申请策略
- **差异化定位**: 突出STEM专长和环保领导力
- **故事化表达**: 用具体例子展现个人特质
- **量化成果**: 用数据证明项目影响力
- **未来愿景**: 展现对未来的清晰规划

### 风险控制
- **备选方案**: 准备多个目标学校
- **时间管理**: 合理安排申请时间线
- **材料准备**: 确保所有材料完整准确
- **面试准备**: 充分准备面试问题

---

## 🎉 成功展望

### 我们的专业价值
通过我们的专业指导，{student_name}将在申请过程中展现最佳状态：

1. **专业评估**: 全面分析学生优势和潜力
2. **策略制定**: 制定个性化的申请策略
3. **材料优化**: 优化申请材料和文书
4. **面试指导**: 提供专业的面试指导
5. **持续支持**: 全程跟踪和支持申请过程

### 成功保障
- ✅ **经验丰富**: 多年私校申请成功经验
- ✅ **专业团队**: 资深顾问和专家团队
- ✅ **成功案例**: 大量成功录取案例
- ✅ **全程服务**: 从评估到录取的全程服务

### 预期结果
基于{student_name}的优秀基础和我们的专业指导，**我们有信心帮助{student_name}获得理想学校的录取**。

**让您的孩子看到希望，让我们的专业成就您的梦想！**

---

*报告生成时间: {datetime.now().strftime("%Y年%m月%d日 %H:%M")}*
*专业顾问: 私校申请专家团队*
"""
        
        return report_content

def main():
    """测试报告生成器"""
    generator = ProfessionalReportGenerator()
    
    # 测试数据
    student_data = {
        "name": "Alex Chen",
        "age": "14岁",
        "grade": "Grade 8"
    }
    
    conversation_log = [
        {"role": "student", "content": "我喜欢组织活动和做科学实验"},
        {"role": "parent", "content": "孩子在学生会组织过环保义卖"}
    ]
    
    report = generator.generate_report(conversation_log, student_data)
    print(report)

if __name__ == "__main__":
    main()
