#!/usr/bin/env python3
"""
报告质量校验模块
实现轻量自动校验，不打断流程
"""

import json
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportValidator:
    """报告质量校验器"""
    
    def __init__(self, logs_dir: str = "logs"):
        """
        初始化校验器
        
        Args:
            logs_dir: 日志目录路径
        """
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        
        # 章节字数要求
        self.section_word_requirements = {
            "家庭与学生背景": {"min": 900, "max": 1100},
            "学校申请定位": {"min": 600, "max": 800},
            "学生—学校匹配度": {"min": 1200, "max": 1500},
            "学术与课外准备": {"min": 900, "max": 1100},
            "申请流程与个性化策略": {"min": 700, "max": 900},
            "录取后延伸建议": {"min": 250, "max": 350}
        }
        
        # 禁止的符号和内容
        self.forbidden_patterns = [
            r'\*\*.*?\*\*',  # Markdown粗体
            r'\*.*?\*',      # Markdown斜体
            r'#+\s*',        # Markdown标题
            r'^\s*[-*+]\s*', # Markdown列表
            r'^\s*\d+\.\s*', # 数字列表
            r'\|.*?\|',      # 表格
            r'```.*?```',    # 代码块
            r'（由面谈补充）', # 旧占位符
            r'（TBD）',       # TBD占位符
            r'（TODO）',      # TODO占位符
        ]
        
        # Emoji模式
        self.emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002600-\U000026FF"  # miscellaneous symbols
            u"\U00002700-\U000027BF"  # dingbats
            "]+", flags=re.UNICODE)
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """
        校验报告内容
        
        Args:
            content: 报告内容
            
        Returns:
            校验结果
        """
        validation_result = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "word_count": len(content),
            "page_count": len(content) // 500,  # 粗略估算
            "has_markdown": False,
            "has_emoji": False,
            "has_placeholders": False,
            "sections_found": 0,
            "section_word_counts": {},
            "validation_issues": [],
            "needs_polish": False,
            "overall_score": 0
        }
        
        # 检查Markdown符号
        validation_result["has_markdown"] = self.check_markdown_symbols(content)
        
        # 检查Emoji
        validation_result["has_emoji"] = self.check_emoji(content)
        
        # 检查占位符
        validation_result["has_placeholders"] = self.check_placeholders(content)
        
        # 检查章节
        validation_result["sections_found"] = self.count_sections(content)
        
        # 检查章节字数
        validation_result["section_word_counts"] = self.check_section_word_counts(content)
        
        # 收集问题
        validation_result["validation_issues"] = self.collect_issues(validation_result)
        
        # 判断是否需要润色
        validation_result["needs_polish"] = self.needs_polish(validation_result)
        
        # 计算总体分数
        validation_result["overall_score"] = self.calculate_score(validation_result)
        
        # 记录校验结果
        self.log_validation_result(validation_result)
        
        return validation_result
    
    def check_markdown_symbols(self, content: str) -> bool:
        """检查是否包含Markdown符号"""
        for pattern in self.forbidden_patterns:
            if re.search(pattern, content, re.MULTILINE):
                return True
        return False
    
    def check_emoji(self, content: str) -> bool:
        """检查是否包含Emoji"""
        return bool(self.emoji_pattern.search(content))
    
    def check_placeholders(self, content: str) -> bool:
        """检查是否包含占位符"""
        placeholder_patterns = [
            r'（由面谈补充）',
            r'（TBD）',
            r'（TODO）',
            r'（待家长确认）'
        ]
        
        for pattern in placeholder_patterns:
            if re.search(pattern, content):
                return True
        return False
    
    def count_sections(self, content: str) -> int:
        """统计章节数量"""
        section_patterns = [
            r'家庭与学生背景',
            r'学校申请定位',
            r'学生—学校匹配度',
            r'学术与课外准备',
            r'申请流程与个性化策略',
            r'录取后延伸建议'
        ]
        
        count = 0
        for pattern in section_patterns:
            if re.search(pattern, content):
                count += 1
        
        return count
    
    def check_section_word_counts(self, content: str) -> Dict[str, Dict[str, int]]:
        """检查各章节字数"""
        section_counts = {}
        
        # 按章节分割内容
        sections = self.split_content_by_sections(content)
        
        for section_name, section_content in sections.items():
            word_count = len(section_content)
            requirements = self.section_word_requirements.get(section_name, {"min": 500, "max": 800})
            
            section_counts[section_name] = {
                "actual": word_count,
                "min_required": requirements["min"],
                "max_recommended": requirements["max"],
                "meets_minimum": word_count >= requirements["min"],
                "within_range": requirements["min"] <= word_count <= requirements["max"]
            }
        
        return section_counts
    
    def split_content_by_sections(self, content: str) -> Dict[str, str]:
        """按章节分割内容"""
        sections = {}
        
        section_patterns = {
            "家庭与学生背景": r"家庭与学生背景",
            "学校申请定位": r"学校申请定位",
            "学生—学校匹配度": r"学生—学校匹配度",
            "学术与课外准备": r"学术与课外准备",
            "申请流程与个性化策略": r"申请流程与个性化策略",
            "录取后延伸建议": r"录取后延伸建议"
        }
        
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 检查是否是章节标题
            for section_name, pattern in section_patterns.items():
                if re.search(pattern, line):
                    # 保存前一章节
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content)
                    
                    # 开始新章节
                    current_section = section_name
                    current_content = []
                    break
            else:
                # 添加到当前章节
                if current_section:
                    current_content.append(line)
        
        # 保存最后一章节
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def collect_issues(self, validation_result: Dict[str, Any]) -> List[str]:
        """收集校验问题"""
        issues = []
        
        if validation_result["has_markdown"]:
            issues.append("包含Markdown符号")
        
        if validation_result["has_emoji"]:
            issues.append("包含Emoji表情")
        
        if validation_result["has_placeholders"]:
            issues.append("包含占位符")
        
        if validation_result["sections_found"] < 6:
            issues.append(f"章节数量不足（期望6个，实际{validation_result['sections_found']}个）")
        
        # 检查章节字数
        for section_name, counts in validation_result["section_word_counts"].items():
            if not counts["meets_minimum"]:
                issues.append(f"{section_name}字数不足（期望{counts['min_required']}字，实际{counts['actual']}字）")
        
        return issues
    
    def needs_polish(self, validation_result: Dict[str, Any]) -> bool:
        """判断是否需要润色"""
        return (
            validation_result["has_markdown"] or
            validation_result["has_emoji"] or
            validation_result["has_placeholders"] or
            validation_result["sections_found"] < 6 or
            any(not counts["meets_minimum"] for counts in validation_result["section_word_counts"].values())
        )
    
    def calculate_score(self, validation_result: Dict[str, Any]) -> int:
        """计算总体分数（0-100）"""
        score = 100
        
        # 扣分项
        if validation_result["has_markdown"]:
            score -= 20
        if validation_result["has_emoji"]:
            score -= 15
        if validation_result["has_placeholders"]:
            score -= 10
        if validation_result["sections_found"] < 6:
            score -= (6 - validation_result["sections_found"]) * 10
        
        # 章节字数扣分
        for counts in validation_result["section_word_counts"].values():
            if not counts["meets_minimum"]:
                score -= 5
        
        return max(0, score)
    
    def log_validation_result(self, validation_result: Dict[str, Any]) -> None:
        """记录校验结果到日志"""
        try:
            # 记录到JSON文件
            log_file = self.logs_dir / "validation.json"
            
            # 读取现有日志
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # 添加新记录
            logs.append(validation_result)
            
            # 只保留最近50条记录
            if len(logs) > 50:
                logs = logs[-50:]
            
            # 写入日志
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
            
            # 记录到文本日志
            self.log_to_text_file(validation_result)
            
        except Exception as e:
            logger.error(f"记录校验结果失败: {e}")
    
    def log_to_text_file(self, validation_result: Dict[str, Any]) -> None:
        """记录到文本日志文件"""
        try:
            log_file = self.logs_dir / "validation.txt"
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n=== 校验结果 {validation_result['timestamp']} ===\n")
                f.write(f"总字数: {validation_result['word_count']}\n")
                f.write(f"页数: {validation_result['page_count']}\n")
                f.write(f"章节数: {validation_result['sections_found']}\n")
                f.write(f"总体分数: {validation_result['overall_score']}/100\n")
                
                if validation_result["validation_issues"]:
                    f.write("问题:\n")
                    for issue in validation_result["validation_issues"]:
                        f.write(f"  - {issue}\n")
                else:
                    f.write("无问题\n")
                
                f.write("\n")
                
        except Exception as e:
            logger.error(f"记录文本日志失败: {e}")
    
    def generate_validation_report(self, validation_result: Dict[str, Any]) -> str:
        """生成校验报告"""
        report = f"""# 报告质量校验结果

## 基本信息
- 校验时间: {validation_result['timestamp']}
- 总字数: {validation_result['word_count']}
- 页数: {validation_result['page_count']}
- 章节数: {validation_result['sections_found']}
- 总体分数: {validation_result['overall_score']}/100

## 章节字数统计
"""
        
        for section_name, counts in validation_result["section_word_counts"].items():
            status = "✅" if counts["meets_minimum"] else "❌"
            report += f"- {section_name}: {counts['actual']}字 {status}\n"
        
        report += "\n## 问题列表\n"
        
        if validation_result["validation_issues"]:
            for issue in validation_result["validation_issues"]:
                report += f"- {issue}\n"
        else:
            report += "- 无问题\n"
        
        report += f"\n## 建议\n"
        
        if validation_result["needs_polish"]:
            report += "- 建议进行润色处理\n"
        else:
            report += "- 质量良好，无需额外处理\n"
        
        return report
    
    def sanitize_content(self, content: str) -> str:
        """清理内容，去除Markdown符号、emoji、占位符"""
        # 去除Markdown符号
        for pattern in self.forbidden_patterns:
            content = re.sub(pattern, '', content, flags=re.MULTILINE)
        
        # 去除emoji
        content = self.emoji_pattern.sub('', content)
        
        # 清理多余的空行
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        return content.strip()


def main():
    """测试校验器"""
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
    
    print("校验结果:")
    print(f"总体分数: {result['overall_score']}/100")
    print(f"问题数量: {len(result['validation_issues'])}")
    print(f"需要润色: {result['needs_polish']}")
    
    if result['validation_issues']:
        print("\n问题列表:")
        for issue in result['validation_issues']:
            print(f"- {issue}")
    
    # 生成校验报告
    report = validator.generate_validation_report(result)
    print(f"\n校验报告:\n{report}")


if __name__ == "__main__":
    main()
