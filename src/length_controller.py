#!/usr/bin/env python3
"""
篇幅与排版控制器
控制报告长度和格式，确保输出约15页A4
"""

import re
import logging
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LengthConfig:
    """长度配置"""
    # 各章节最大字数（中文字符）
    family_background: int = 1000      # 家庭与学生背景 ~3页
    school_positioning: int = 800      # 学校申请定位 ~2页
    matching_analysis: int = 1500      # 学生—学校匹配度 ~4页
    academic_preparation: int = 1100  # 学术与课外准备 ~3页
    application_strategy: int = 900    # 申请流程与个性化策略 ~2.5页
    post_admission: int = 350         # 录取后延伸建议 ~0.5页
    
    # 排版设置
    font_size: int = 11               # 正文字号
    line_spacing: float = 1.25        # 行距
    paragraph_spacing_before: int = 12  # 段前距
    paragraph_spacing_after: int = 6    # 段后距
    table_font_size: int = 10         # 表格字号
    
    # 页数控制
    target_pages: int = 15            # 目标页数
    min_pages: int = 14               # 最少页数
    max_pages: int = 16               # 最多页数
    chars_per_page: int = 800         # 每页字符数估算

class LengthController:
    """长度控制器"""
    
    def __init__(self, config: LengthConfig = None):
        """
        初始化长度控制器
        
        Args:
            config: 长度配置
        """
        self.config = config or LengthConfig()
        self.section_lengths = {
            "family_background": self.config.family_background,
            "school_positioning": self.config.school_positioning,
            "matching_analysis": self.config.matching_analysis,
            "academic_preparation": self.config.academic_preparation,
            "application_strategy": self.config.application_strategy,
            "post_admission": self.config.post_admission
        }
    
    def count_chinese_chars(self, text: str) -> int:
        """
        计算中文字符数
        
        Args:
            text: 文本内容
            
        Returns:
            中文字符数
        """
        # 匹配中文字符的正则表达式
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        return len(chinese_pattern.findall(text))
    
    def estimate_page_count(self, content: str) -> int:
        """
        估算页数
        
        Args:
            content: 报告内容
            
        Returns:
            估算页数
        """
        chinese_chars = self.count_chinese_chars(content)
        estimated_pages = chinese_chars / self.config.chars_per_page
        return int(round(estimated_pages))
    
    def truncate_text(self, text: str, max_length: int, add_ellipsis: bool = True) -> str:
        """
        截断文本到指定长度
        
        Args:
            text: 原始文本
            max_length: 最大长度
            add_ellipsis: 是否添加省略号
            
        Returns:
            截断后的文本
        """
        if self.count_chinese_chars(text) <= max_length:
            return text
        
        # 按字符截断
        truncated = ""
        char_count = 0
        
        for char in text:
            if re.match(r'[\u4e00-\u9fff]', char):
                char_count += 1
            truncated += char
            
            if char_count >= max_length:
                break
        
        if add_ellipsis and char_count >= max_length:
            truncated += "..."
        
        return truncated
    
    def adjust_section_length(self, section_name: str, current_length: int, 
                           target_length: int) -> str:
        """
        调整章节长度
        
        Args:
            section_name: 章节名称
            current_length: 当前长度
            target_length: 目标长度
            
        Returns:
            调整建议
        """
        if current_length <= target_length:
            return f"章节 {section_name} 长度合适 ({current_length}字)"
        
        excess = current_length - target_length
        reduction_percent = (excess / current_length) * 100
        
        if reduction_percent <= 15:
            return f"建议减少 {excess} 字 ({reduction_percent:.1f}%)"
        else:
            return f"需要大幅缩减 {excess} 字 ({reduction_percent:.1f}%)"
    
    def analyze_content_length(self, content: str) -> Dict[str, Any]:
        """
        分析内容长度
        
        Args:
            content: 报告内容
            
        Returns:
            长度分析结果
        """
        # 按章节分割内容
        sections = self._split_content_by_sections(content)
        
        analysis = {
            "total_chars": self.count_chinese_chars(content),
            "estimated_pages": self.estimate_page_count(content),
            "sections": {},
            "recommendations": []
        }
        
        # 分析各章节
        for section_name, section_content in sections.items():
            char_count = self.count_chinese_chars(section_content)
            target_length = self.section_lengths.get(section_name, 1000)
            
            analysis["sections"][section_name] = {
                "current_length": char_count,
                "target_length": target_length,
                "status": "ok" if char_count <= target_length else "exceed",
                "adjustment": self.adjust_section_length(section_name, char_count, target_length)
            }
        
        # 生成总体建议
        total_pages = analysis["estimated_pages"]
        if total_pages > self.config.max_pages:
            analysis["recommendations"].append(f"总页数 {total_pages} 超过目标，建议缩减 {(total_pages - self.config.target_pages) * self.config.chars_per_page} 字")
        elif total_pages < self.config.min_pages:
            analysis["recommendations"].append(f"总页数 {total_pages} 不足，建议增加 {(self.config.target_pages - total_pages) * self.config.chars_per_page} 字")
        else:
            analysis["recommendations"].append(f"总页数 {total_pages} 符合目标范围")
        
        return analysis
    
    def _split_content_by_sections(self, content: str) -> Dict[str, str]:
        """
        按章节分割内容
        
        Args:
            content: 报告内容
            
        Returns:
            章节内容字典
        """
        sections = {}
        
        # 定义章节分割模式
        section_patterns = {
            "family_background": r"## 👨‍👩‍👧‍👦 家庭与学生背景.*?(?=## |$)",
            "school_positioning": r"## 🏫 学校申请定位.*?(?=## |$)",
            "matching_analysis": r"## 🏫 学生—学校匹配度.*?(?=## |$)",
            "academic_preparation": r"## 📚 学术与课外准备.*?(?=## |$)",
            "application_strategy": r"## 📅 申请流程与个性化策略.*?(?=## |$)",
            "post_admission": r"## 🎓 录取后延伸建议.*?(?=## |$)"
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, content, re.DOTALL)
            if match:
                sections[section_name] = match.group(0)
            else:
                sections[section_name] = ""
        
        return sections
    
    def optimize_content_length(self, content: str) -> str:
        """
        优化内容长度
        
        Args:
            content: 原始内容
            
        Returns:
            优化后的内容
        """
        analysis = self.analyze_content_length(content)
        
        # 如果总页数合适，直接返回
        if self.config.min_pages <= analysis["estimated_pages"] <= self.config.max_pages:
            return content
        
        # 暂时直接返回原始内容，避免重新组装问题
        # TODO: 实现真正的长度优化
        return content
    
    def _reduce_section_content(self, content: str, reduction_ratio: float) -> str:
        """
        缩减章节内容
        
        Args:
            content: 章节内容
            reduction_ratio: 缩减比例
            
        Returns:
            缩减后的内容
        """
        # 按段落分割
        paragraphs = content.split('\n\n')
        reduced_paragraphs = []
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                reduced_paragraphs.append(paragraph)
                continue
            
            # 计算段落目标长度
            current_length = self.count_chinese_chars(paragraph)
            target_length = int(current_length * reduction_ratio)
            
            if current_length > target_length:
                # 截断段落
                truncated = self.truncate_text(paragraph, target_length)
                reduced_paragraphs.append(truncated)
            else:
                reduced_paragraphs.append(paragraph)
        
        return '\n\n'.join(reduced_paragraphs)
    
    def _reassemble_content(self, sections: Dict[str, str]) -> str:
        """
        重新组装内容
        
        Args:
            sections: 章节内容字典
            
        Returns:
            组装后的内容
        """
        # 按原始顺序组装
        section_order = [
            "family_background",
            "school_positioning", 
            "matching_analysis",
            "academic_preparation",
            "application_strategy",
            "post_admission"
        ]
        
        content_parts = []
        
        # 添加标题和目录
        content_parts.append("# 🎯 私校申请策略报告")
        content_parts.append("## 📋 目录")
        content_parts.append("1. [家庭与学生背景](#家庭与学生背景) (约3页)")
        content_parts.append("2. [学校申请定位](#学校申请定位) (约2页)")
        content_parts.append("3. [学生—学校匹配度](#学生学校匹配度) (约4页)")
        content_parts.append("4. [学术与课外准备](#学术与课外准备) (约3页)")
        content_parts.append("5. [申请流程与个性化策略](#申请流程与个性化策略) (约2.5页)")
        content_parts.append("6. [录取后延伸建议](#录取后延伸建议) (约0.5页)")
        content_parts.append("---")
        
        # 添加各章节
        for section_name in section_order:
            if section_name in sections and sections[section_name]:
                content_parts.append(sections[section_name])
                content_parts.append("---")
        
        return '\n\n'.join(content_parts)
    
    def generate_length_report(self, content: str) -> str:
        """
        生成长度报告
        
        Args:
            content: 报告内容
            
        Returns:
            长度报告文本
        """
        analysis = self.analyze_content_length(content)
        
        report = f"""# 📊 报告长度分析

## 总体统计
- **总字符数**: {analysis['total_chars']} 字
- **估算页数**: {analysis['estimated_pages']} 页
- **目标页数**: {self.config.target_pages} 页
- **状态**: {'✅ 符合要求' if self.config.min_pages <= analysis['estimated_pages'] <= self.config.max_pages else '⚠️ 需要调整'}

## 各章节分析
"""
        
        for section_name, section_info in analysis['sections'].items():
            status_icon = "✅" if section_info['status'] == 'ok' else "⚠️"
            report += f"""
### {section_name}
- **当前长度**: {section_info['current_length']} 字
- **目标长度**: {section_info['target_length']} 字
- **状态**: {status_icon} {section_info['status']}
- **建议**: {section_info['adjustment']}
"""
        
        report += f"""
## 调整建议
"""
        for recommendation in analysis['recommendations']:
            report += f"- {recommendation}\n"
        
        return report

def main():
    """测试长度控制器"""
    controller = LengthController()
    
    # 测试内容
    test_content = """
# 🎯 私校申请策略报告

## 👨‍👩‍👧‍👦 家庭与学生背景

### 家庭教育理念与价值观
这是一个很长的段落，用来测试长度控制功能。家庭价值观对孩子的成长有着重要的影响，包括教育理念、文化背景、支持程度等方面。我们需要详细分析这些因素，以便为申请策略提供准确的指导。

### 学业与学习风格
学生的学术表现是申请成功的关键因素之一。我们需要全面评估学生的GPA、标准化考试成绩、学术竞赛成就等方面。同时，学习能力和适应能力也是重要的考量因素。

## 🏫 学校申请定位

### 家长择校标准
家长在选择学校时会考虑多个因素，包括学术水平、地理位置、学费预算、学校文化等。我们需要了解家长的具体需求和期望，以便推荐合适的学校。

### 学校资源扫描
对目标学校的资源进行全面扫描，包括师资力量、设施设备、特色项目、校友网络等方面。这些信息将帮助我们评估学校与学生的匹配度。

## 🏫 学生—学校匹配度（核心）

这是最重要的章节，需要详细分析学生与各目标学校的匹配度。我们将从学术能力、活动资源、文化价值观、性格氛围等维度进行评估，并给出具体的匹配度分数和推荐理由。

## 📚 学术与课外准备

### 学术补强计划
根据学生的学术现状和目标学校的要求，制定具体的学术提升计划。包括各科目的强化训练、语言能力提升、标准化考试准备等。

### 课外活动规划
课外活动是展示学生综合素质的重要途径。我们需要规划合适的竞赛参与、作品集制作、志愿服务等活动，以提升学生的竞争力。

## 📅 申请流程与个性化策略

### 时间线规划
制定详细的申请时间线，包括各阶段的截止日期、重要里程碑等。确保申请过程有序进行，避免遗漏关键环节。

### 个性化策略
根据学生的特点和目标学校的要求，制定个性化的申请策略。包括文书主题、推荐信策略、面试准备等。

## 🎓 录取后延伸建议

### Offer对比与选择
如果获得多个学校的录取通知，需要从多个角度进行对比分析，帮助学生和家长做出最佳选择。

### 入学前准备
录取后的衔接工作同样重要，包括学术准备、心理适应、生活安排等方面。
"""
    
    # 分析长度
    analysis = controller.analyze_content_length(test_content)
    print("长度分析结果:")
    print(f"总字符数: {analysis['total_chars']}")
    print(f"估算页数: {analysis['estimated_pages']}")
    
    # 生成长度报告
    length_report = controller.generate_length_report(test_content)
    print("\n长度报告:")
    print(length_report)

if __name__ == "__main__":
    main()
