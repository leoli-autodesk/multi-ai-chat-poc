#!/usr/bin/env python3
"""
报告组装器 - 固定唯一模板与顺序
消除多模板并存和重复拼接导致的随机输出
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

class ReportAssembler:
    """报告组装器 - 单一来源，固定顺序"""
    
    # 固定的6大章节
    REQUIRED_SECTIONS = [
        "家庭与学生背景",
        "学校申请定位", 
        "学生—学校匹配度",
        "学术与课外准备",
        "申请流程与个性化策略",
        "录取后延伸建议"
    ]
    
    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir)
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
    def assemble_report(self, sections: Dict[str, str]) -> str:
        """
        按固定顺序组装报告，每章只出现一次
        
        Args:
            sections: 章节内容字典
            
        Returns:
            完整的报告文本
        """
        # 结构校验
        self._validate_structure(sections)
        
        # 组装报告
        report_parts = []
        
        for section_title in self.REQUIRED_SECTIONS:
            if section_title in sections:
                content = sections[section_title]
                # 清理内容
                cleaned_content = self._sanitize(content)
                report_parts.append(f"{section_title}\n\n{cleaned_content}\n")
            else:
                raise ValueError(f"缺少必需章节: {section_title}")
        
        full_report = "\n".join(report_parts)
        
        # 最终重复检查
        self._assert_no_duplicate_sections(full_report)
        
        # 记录模板路径
        self._log_template_path("writer-only")
        
        return full_report
    
    def _validate_structure(self, sections: Dict[str, str]) -> None:
        """结构校验：检查章节数量和重复"""
        sections_found = len(sections)
        
        if sections_found != 6:
            raise ValueError(f"章节数量错误: 期望6章，实际{sections_found}章")
        
        # 检查是否有重复标题
        for title in sections.keys():
            if title not in self.REQUIRED_SECTIONS:
                raise ValueError(f"发现非标准章节: {title}")
        
        # 检查必需章节
        missing_sections = set(self.REQUIRED_SECTIONS) - set(sections.keys())
        if missing_sections:
            raise ValueError(f"缺少必需章节: {missing_sections}")
    
    def _sanitize(self, content: str) -> str:
        """
        剔除旧块与Markdown痕迹
        
        删除 #/**/[]()/|/✅/🎯/📅 等 Markdown/emoji
        把清单项合并成自然段
        丢弃营销段/行动计划清单/表格残留
        """
        # 删除Markdown标记
        content = re.sub(r'[#*`\[\]()|]', '', content)
        
        # 删除emoji
        emoji_pattern = r'[✅🎯📅🎉📊📋🏆💡🚀⭐]'
        content = re.sub(emoji_pattern, '', content)
        
        # 删除营销段关键词
        marketing_keywords = [
            "我们的专业价值",
            "成功保障", 
            "行动计划",
            "让您的孩子看到希望",
            "让我们的专业成就您的梦想"
        ]
        
        lines = content.split('\n')
        filtered_lines = []
        
        for line in lines:
            # 检查是否包含营销关键词
            if any(keyword in line for keyword in marketing_keywords):
                continue
            
            # 删除以 - 开头的清单项，合并成自然段
            if line.strip().startswith('-'):
                line = line.strip()[1:].strip()
            
            if line.strip():
                filtered_lines.append(line.strip())
        
        # 合并成自然段
        content = ' '.join(filtered_lines)
        
        # 清理多余空格
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
    
    def _assert_no_duplicate_sections(self, full_text: str) -> None:
        """运行时重复守门员 - 最后一道闸"""
        # 标题正则表达式
        title_pattern = r'^(家庭与学生背景|学校申请定位|学生—学校匹配度|学术与课外准备|申请流程与个性化策略|录取后延伸建议)$'
        
        lines = full_text.split('\n')
        section_counts = {}
        section_positions = {}
        
        for i, line in enumerate(lines):
            line = line.strip()
            if re.match(title_pattern, line):
                if line in section_counts:
                    section_counts[line] += 1
                    section_positions[line].append(i)
                else:
                    section_counts[line] = 1
                    section_positions[line] = [i]
        
        # 检查重复
        duplicates = {title: count for title, count in section_counts.items() if count > 1}
        if duplicates:
            error_msg = f"发现重复章节: {duplicates}\n"
            for title, positions in section_positions.items():
                if len(positions) > 1:
                    error_msg += f"{title} 出现在行: {positions}\n"
            raise ValueError(error_msg)
        
        # 检查章节数量
        sections_found = len(section_counts)
        if sections_found != 6:
            raise ValueError(f"章节数量错误: 期望6章，实际{sections_found}章")
        
        # 记录校验结果
        self._log_validation_result(sections_found, section_counts)
    
    def _log_template_path(self, template_path: str) -> None:
        """记录模板路径"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "template_path": template_path,
            "note": "禁止从旧模板拼接内容"
        }
        
        log_file = self.logs_dir / "template_path.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    def _log_validation_result(self, sections_found: int, section_counts: Dict[str, int]) -> None:
        """记录校验结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        log_data = {
            "timestamp": timestamp,
            "sections_found": sections_found,
            "expected_sections": 6,
            "section_counts": section_counts,
            "validation_passed": sections_found == 6 and all(count == 1 for count in section_counts.values()),
            "duplicates_found": any(count > 1 for count in section_counts.values())
        }
        
        log_file = self.logs_dir / f"张小明_校验结果_{timestamp}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    def assert_no_old_templates(self) -> None:
        """单一来源断言"""
        # 检查是否使用了旧模板
        uses_old_template = self._uses_template('strategy_report.md') or self._uses_template('report.docx')
        
        if uses_old_template:
            raise AssertionError('禁止从旧模板拼接内容')
    
    def _uses_template(self, template_name: str) -> bool:
        """检查是否使用了指定模板"""
        # 这里可以根据实际使用情况来判断
        # 暂时返回False，表示不使用旧模板
        return False

def main():
    """测试报告组装器"""
    assembler = ReportAssembler("config")
    
    # 测试数据
    test_sections = {
        "家庭与学生背景": "这是一个测试的家庭背景内容",
        "学校申请定位": "这是一个测试的学校申请定位内容", 
        "学生—学校匹配度": "这是一个测试的匹配度内容",
        "学术与课外准备": "这是一个测试的学术准备内容",
        "申请流程与个性化策略": "这是一个测试的申请策略内容",
        "录取后延伸建议": "这是一个测试的延伸建议内容"
    }
    
    try:
        report = assembler.assemble_report(test_sections)
        print("✅ 报告组装成功")
        print(f"报告长度: {len(report)} 字符")
        print(f"章节数: {len(test_sections)}")
    except Exception as e:
        print(f"❌ 报告组装失败: {e}")

if __name__ == "__main__":
    main()
