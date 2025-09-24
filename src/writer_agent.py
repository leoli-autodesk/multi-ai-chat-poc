#!/usr/bin/env python3
"""
Writer Agent - 专业报告撰写代理
实现精确的Writer Agent契约和调用方式
"""

import json
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from cursor_ai import CursorAI

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WriterAgent:
    """Writer Agent - 专业报告撰写代理"""
    
    def __init__(self, config_dir: str = "config"):
        """
        初始化Writer Agent
        
        Args:
            config_dir: 配置目录路径
        """
        self.config_dir = Path(config_dir)
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # 初始化AI接口 - 确定性设置
        self.ai = CursorAI({
            "globals": {"max_content_length": 300},
            "model_config": {
                "default_model": "gpt-4o",
                "temperature": 0.5,  # 固定温度
                "top_p": 0.9,
                "max_tokens": 3500,
                "seed": 42  # 固定种子（如果模型支持）
            }
        })
        
        # Writer Agent系统提示词 - 严格6章模板
        self.system_prompt = """你是一名资深私立学校申请顾问的专业撰稿人（Writer）。你的唯一产出是中文正式书面体的连贯段落，用于直接渲染到 Word。

【严格约束】
1. 仅生成以下6章内容，不得另起任何附加章节或重复段落：
   - 家庭与学生背景
   - 学校申请定位  
   - 学生—学校匹配度
   - 学术与课外准备
   - 申请流程与个性化策略
   - 录取后延伸建议

2. 严格禁止输出任何 Markdown 语法（如 #、**、[]()、-、|、表格）、emoji、口语化、感叹号、占位符（如"（由面谈补充）/TBD/TODO"）和纯列点。

3. 必须把输入的要点、打分、清单、子弹点改写为自然段落，句式有长短变化，逻辑清晰，证据充分。

4. 匹配度章节仅一次，包含逐校差异化的段落解读，禁止列表与表格。

5. 分章调用时不得复述前文，需承接式一句带过并补充新信息。

目标成品是一份约 14–15 页的专业报告，各章节字数范围如下（中文字符，不含空格）：

家庭与学生背景：900–1100
学校申请定位：600–800
学生—学校匹配度（核心）：1200–1500（含逐校推荐理由每校 120–180、潜在挑战 80–120）
学术与课外准备：900–1100
申请流程与个性化策略：700–900
录取后延伸建议：250–350

结尾避免元话语（如"本章节到此"），各段以建议或行动要点自然收束。
若输入缺项，不得输出占位符；应根据可得信息保守推断并标注"家长需核实：…"（全篇≤3处）。

【去重硬约束】：
1. 不得重复已在前文写过的观点或句子；当需要再次引用时，用 1 句承接式概括（例如"前文已论及其在 STEM 的长期投入，此处补充其在跨学科学习中的延伸表现。"），禁止复述原文。
2. 逐校"推荐理由/潜在挑战"必须差异化：每所学校至少包含 2 个与该校资源/文化/项目强相关的独有角度；禁止使用模板化句式（如"学术卓越、领导力培养、校友网络强大"等）重复出现两次以上。
3. 任何章节若与已有内容高度重叠，优先补充新的证据/示例/可执行步骤，而非换词同义改写。
4. 禁止使用"我们的专业价值/成功保障"类营销段落超过 1 次；若需要，请只保留在最后"成功展望"处。

【章节唯一性约束】：
5. 禁止重复已写过的段落或章节内容。每个章节内容只写一次。
6. 若需要承接前文，请用一句承接式总结，而不是复述。
7. 严格按照以下6个章节顺序生成，每个章节只出现一次：
   - 家庭与学生背景
   - 学校申请定位  
   - 学生—学校匹配度
   - 学术与课外准备
   - 申请流程与个性化策略
   - 录取后延伸建议"""
        
        # 章节配置
        self.section_configs = {
            "家庭与学生背景": {"min": 900, "max": 1100},
            "学校申请定位": {"min": 600, "max": 800},
            "学生—学校匹配度": {"min": 1200, "max": 1500},
            "学术与课外准备": {"min": 900, "max": 1100},
            "申请流程与个性化策略": {"min": 700, "max": 900},
            "录取后延伸建议": {"min": 250, "max": 350}
        }
    
    def write_section(self, section_name: str, section_json: Dict[str, Any], 
                     min_chars: int, max_chars: int, context_summary: str = "") -> str:
        """
        撰写单个章节
        
        Args:
            section_name: 章节名称
            section_json: 章节数据
            min_chars: 最小字数
            max_chars: 最大字数
            context_summary: 已写内容摘要
            
        Returns:
            章节内容
        """
        # 构建用户提示词
        user_prompt = f"""目标：撰写《私立学校申请咨询报告》的 {section_name} 章节，输出连贯段落。
资料（JSON）：{json.dumps(section_json, ensure_ascii=False, indent=2)}
规则：

禁止列表/表格/emoji/Markdown/占位符；只写自然段。

字数 {min_chars}–{max_chars}，优先给出细节、例证与可执行建议；避免空话。

不确定信息请审慎表述，并附"家长需核实：…"（本章最多 1 处）。

匹配度章节需对每所学校写出综合解读（学术/活动/文化/性格四维）、量化结果的文字化解释、申请切入点与面试思路；逐校"推荐理由"120–180字、"潜在挑战"80–120字，以段落表达。

不出现"本报告/本章节/如下/以上"等元话语；以行动建议或观察要点收束。"""

        # 如果有已写内容摘要，添加去重约束
        if context_summary:
            user_prompt += f"""

已写内容摘要：{context_summary}

下文撰写不得重复 context_summary 的要点；如需提及，仅用一句承接式概括，并补充新的可核查细节或步骤。"""

        # 如果是匹配度章节，添加额外要求
        if section_name == "学生—学校匹配度":
            user_prompt += """

（匹配度章额外追加）：

将 matching.ranking 的先后转写为"顾问推荐顺序"，文字解释与正文一致。

如 facts 缺失，请不输出占位符，改为给出信息收集路径（如"校方课程手册/招生办邮件核实师生比"）。"""
        
        try:
            # 调试：打印提示词
            logger.info(f"生成章节 {section_name}，字数要求: {min_chars}-{max_chars}")
            logger.info(f"用户提示词长度: {len(user_prompt)}")
            
            # 调用AI生成内容
            response = self.ai.call_llm("Writer", self.system_prompt, {"content": user_prompt})
            
            if isinstance(response, str):
                logger.info(f"AI响应长度: {len(response)}")
                
                # 清理内容
                cleaned_content = self.sanitize_to_prose(response)
                
                # 确保内容符合章节要求
                if len(cleaned_content) < min_chars:
                    logger.warning(f"章节 {section_name} 字数不足，需要扩写")
                    # 可以在这里实现扩写逻辑
                
                return cleaned_content
            else:
                logger.error(f"AI返回非字符串响应: {response}")
                return f"（待家长确认：{section_name}章节内容）"
                
        except Exception as e:
            logger.error(f"生成章节 {section_name} 失败: {e}")
            return f"（待家长确认：{section_name}章节内容）"
    
    def compose_full_report(self, data: Dict[str, Any]) -> str:
        """
        撰写完整报告
        
        Args:
            data: 完整数据
            
        Returns:
            完整报告内容
        """
        logger.info("开始撰写完整报告...")
        
        # 按固定章节顺序生成
        section_order = [
            "家庭与学生背景",
            "学校申请定位", 
            "学生—学校匹配度",
            "学术与课外准备",
            "申请流程与个性化策略",
            "录取后延伸建议"
        ]
        
        sections_content = {}
        context_summary = ""  # 已写内容摘要
        
        # 按章节顺序生成
        for section_name in section_order:
            logger.info(f"正在撰写章节: {section_name}")
            
            # 提取章节数据
            section_data = self.extract_section_data(data, section_name)
            
            # 生成章节内容（传入已写内容摘要）
            section_content = self.write_section(
                section_name, 
                section_data, 
                self.section_configs[section_name]["min"], 
                self.section_configs[section_name]["max"],
                context_summary
            )
            
            # 存储章节内容（不包含标题）
            sections_content[section_name] = section_content
            
            # 更新已写内容摘要（取前3-5句）
            section_sentences = self.extract_key_sentences(section_content)
            if section_sentences:
                context_summary += f"{section_name}要点：{' '.join(section_sentences[:3])}。"
        
        # 按模板顺序拼接章节
        full_report = self.build_report_by_template(sections_content)
        
        # 去重章节
        deduplicated_report = self.deduplicate_sections(full_report)
        
        logger.info("完整报告撰写完成")
        return deduplicated_report
    
    def generate_section(self, prompt: str) -> str:
        """生成单个章节内容"""
        try:
            # 调用AI生成内容
            response = self.ai.generate_writer_response(prompt)
            
            # 清理内容
            cleaned_content = self.clean_content(response)
            
            return cleaned_content
            
        except Exception as e:
            logger.error(f"章节生成失败: {e}")
            return f"章节内容生成失败: {str(e)}"
    
    def clean_content(self, content: str) -> str:
        """清理内容，移除Markdown和emoji"""
        # 移除Markdown标记
        content = re.sub(r'[#*`\[\]()|]', '', content)
        
        # 移除emoji
        emoji_pattern = r'[✅🎯📅🎉📊📋🏆💡🚀⭐]'
        content = re.sub(emoji_pattern, '', content)
        
        # 移除多余空格
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
    
    def extract_section_data(self, data: Dict[str, Any], section_name: str) -> Dict[str, Any]:
        """提取章节相关数据"""
        if section_name == "家庭与学生背景":
            return {
                "student": data.get("student", {}),
                "family": data.get("family", {})
            }
        elif section_name == "学校申请定位":
            return {
                "positioning": data.get("positioning", {}),
                "family": data.get("family", {})
            }
        elif section_name == "学生—学校匹配度":
            return {
                "matching": data.get("matching", {}),
                "student": data.get("student", {}),
                "family": data.get("family", {})
            }
        elif section_name == "学术与课外准备":
            return {
                "plans": data.get("plans", {}),
                "student": data.get("student", {})
            }
        elif section_name == "申请流程与个性化策略":
            return {
                "timeline": data.get("timeline", {}),
                "tests": data.get("tests", {}),
                "essays_refs_interview": data.get("essays_refs_interview", {}),
                "student": data.get("student", {})
            }
        elif section_name == "录取后延伸建议":
            return {
                "post_offer": data.get("post_offer", {}),
                "student": data.get("student", {})
            }
        else:
            return {}
    
    def sanitize_to_prose(self, content: str) -> str:
        """
        文本清洗（强制）
        删除所有可能残留的：Markdown 语法、emoji、非标准空白符
        """
        # 删除Markdown语法
        markdown_patterns = [
            r'\*\*(.*?)\*\*',  # 粗体
            r'\*(.*?)\*',      # 斜体
            r'#+\s*',          # 标题
            r'^\s*[-*+]\s*',   # 列表
            r'^\s*\d+\.\s*',   # 数字列表
            r'\|.*?\|',        # 表格
            r'```.*?```',      # 代码块
            r'\[.*?\]\(.*?\)', # 链接
            r'`.*?`',          # 行内代码
        ]
        
        for pattern in markdown_patterns:
            content = re.sub(pattern, '', content, flags=re.MULTILINE)
        
        # 删除emoji
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002600-\U000026FF"  # miscellaneous symbols
            u"\U00002700-\U000027BF"  # dingbats
            "]+", flags=re.UNICODE)
        content = emoji_pattern.sub('', content)
        
        # 删除占位符
        placeholder_patterns = [
            r'（由面谈补充）',
            r'（TBD）',
            r'（TODO）',
            r'/\*\*.*?\*\*/',  # 注释
        ]
        
        for pattern in placeholder_patterns:
            content = re.sub(pattern, '', content)
        
        # 清理多余的空行和空白符
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        # 合并过短的句子
        content = self.merge_short_sentences(content)
        
        return content.strip()
    
    def merge_short_sentences(self, content: str) -> str:
        """合并过短的句子为3-6句自然段"""
        sentences = re.split(r'[。！？]', content)
        paragraphs = []
        current_paragraph = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            current_paragraph.append(sentence)
            
            # 如果当前段落有3-6句，开始新段落
            if len(current_paragraph) >= 3:
                paragraphs.append('。'.join(current_paragraph) + '。')
                current_paragraph = []
        
        # 处理剩余的句子
        if current_paragraph:
            paragraphs.append('。'.join(current_paragraph) + '。')
        
        return '\n\n'.join(paragraphs)
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """验证内容质量"""
        validation_result = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "word_count": len(content),
            "has_markdown": bool(re.search(r'[*#|`]', content)),
            "has_emoji": bool(re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF]', content)),
            "has_placeholders": bool(re.search(r'（由面谈补充）|（TBD）|（TODO）', content)),
            "sections_found": len(re.findall(r'家庭与学生背景|学校申请定位|学生—学校匹配度|学术与课外准备|申请流程与个性化策略|录取后延伸建议', content)),
            "needs_rewrite": False,
            "rewrite_reasons": []
        }
        
        # 检查是否需要重写
        if validation_result["has_markdown"]:
            validation_result["needs_rewrite"] = True
            validation_result["rewrite_reasons"].append("包含Markdown语法")
        
        if validation_result["has_emoji"]:
            validation_result["needs_rewrite"] = True
            validation_result["rewrite_reasons"].append("包含emoji")
        
        if validation_result["has_placeholders"]:
            validation_result["needs_rewrite"] = True
            validation_result["rewrite_reasons"].append("包含占位符")
        
        if validation_result["sections_found"] < 6:
            validation_result["needs_rewrite"] = True
            validation_result["rewrite_reasons"].append("章节数量不足")
        
        return validation_result
    
    def log_writer_summary(self, validation_result: Dict[str, Any], 
                          section_counts: Dict[str, int]) -> None:
        """记录Writer摘要日志"""
        try:
            summary = {
                "timestamp": validation_result["timestamp"],
                "word_count": validation_result["word_count"],
                "sections_found": validation_result["sections_found"],
                "section_word_counts": section_counts,
                "needs_rewrite": validation_result["needs_rewrite"],
                "rewrite_reasons": validation_result["rewrite_reasons"],
                "has_markdown": validation_result["has_markdown"],
                "has_emoji": validation_result["has_emoji"],
                "has_placeholders": validation_result["has_placeholders"]
            }
            
            log_file = self.logs_dir / "writer_summary.json"
            
            # 读取现有日志
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # 添加新记录
            logs.append(summary)
            
            # 只保留最近50条记录
            if len(logs) > 50:
                logs = logs[-50:]
            
            # 写入日志
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"记录Writer摘要失败: {e}")
    
    def count_section_words(self, content: str) -> Dict[str, int]:
        """统计各章节字数"""
        section_counts = {}
        
        # 按章节分割内容
        sections = self.split_content_by_sections(content)
        
        for section_name, section_content in sections.items():
            section_counts[section_name] = len(section_content)
        
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
    
    def extract_key_sentences(self, content: str) -> List[str]:
        """提取关键句子（前3-5句）"""
        # 按句号分割句子
        sentences = re.split(r'[。！？]', content)
        
        # 过滤空句子和过短的句子
        key_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # 至少10个字符
                key_sentences.append(sentence)
                if len(key_sentences) >= 5:  # 最多取5句
                    break
        
        return key_sentences
    
    def build_report_by_template(self, sections_content: Dict[str, str]) -> str:
        """
        按模板顺序拼接章节
        
        Args:
            sections_content: 章节内容字典
            
        Returns:
            拼接后的报告
        """
        section_order = [
            "家庭与学生背景",
            "学校申请定位", 
            "学生—学校匹配度",
            "学术与课外准备",
            "申请流程与个性化策略",
            "录取后延伸建议"
        ]
        
        report_parts = []
        
        for section_name in section_order:
            if section_name in sections_content:
                # 添加章节标题
                report_parts.append(section_name)
                # 添加章节内容
                report_parts.append(sections_content[section_name])
                # 添加空行分隔
                report_parts.append("")
        
        return "\n".join(report_parts)
    
    def deduplicate_sections(self, text: str) -> str:
        """
        按标题锚点检测，只保留首次出现的内容，后续相同标题段落全部丢弃
        
        Args:
            text: 原始文本
            
        Returns:
            去重后的文本
        """
        logger.info("开始去重章节...")
        
        # 定义章节标题锚点
        section_anchors = [
            "家庭与学生背景",
            "学校申请定位", 
            "学生—学校匹配度",
            "学术与课外准备",
            "申请流程与个性化策略",
            "录取后延伸建议"
        ]
        
        lines = text.split('\n')
        deduplicated_lines = []
        seen_sections = set()
        current_section = None
        in_section = False
        
        for line in lines:
            line = line.strip()
            
            # 检查是否是章节标题
            is_section_title = False
            for anchor in section_anchors:
                if line == anchor:
                    is_section_title = True
                    break
            
            if is_section_title:
                if line not in seen_sections:
                    # 首次出现的章节，保留
                    seen_sections.add(line)
                    current_section = line
                    in_section = True
                    deduplicated_lines.append(line)
                    logger.info(f"保留章节: {line}")
                else:
                    # 重复章节，丢弃
                    current_section = None
                    in_section = False
                    logger.info(f"丢弃重复章节: {line}")
            else:
                # 普通内容行
                if in_section:
                    # 在有效章节内，保留内容
                    deduplicated_lines.append(line)
                elif not line:
                    # 空行，保留
                    deduplicated_lines.append(line)
                # 其他情况（在重复章节内的内容）丢弃
        
        result = '\n'.join(deduplicated_lines)
        
        # 清理多余的空行
        result = re.sub(r'\n\s*\n\s*\n', '\n\n', result)
        
        logger.info(f"章节去重完成，保留章节数: {len(seen_sections)}")
        return result.strip()
    
    def validate_section_count(self, text: str) -> Dict[str, Any]:
        """
        验证章节数量和质量
        
        Args:
            text: 报告文本
            
        Returns:
            验证结果
        """
        section_anchors = [
            "家庭与学生背景",
            "学校申请定位", 
            "学生—学校匹配度",
            "学术与课外准备",
            "申请流程与个性化策略",
            "录取后延伸建议"
        ]
        
        found_sections = []
        for anchor in section_anchors:
            if anchor in text:
                found_sections.append(anchor)
        
        validation_result = {
            "total_sections": len(found_sections),
            "expected_sections": 6,
            "found_sections": found_sections,
            "missing_sections": [s for s in section_anchors if s not in found_sections],
            "is_valid": len(found_sections) == 6,
            "has_duplicates": len(found_sections) != len(set(found_sections))
        }
        
        return validation_result


def main():
    """测试Writer Agent"""
    writer = WriterAgent()
    
    # 测试数据
    test_data = {
        "student": {
            "name": "Alex Chen",
            "age": "14岁",
            "grade": "Grade 8",
            "gpa": "3.8/4.0",
            "academic_strengths": "数学、物理、计算机科学",
            "competition_achievements": "机器人竞赛省级二等奖",
            "leadership_positions": "科技部副部长",
            "project_experiences": "环保义卖活动组织"
        },
        "family": {
            "education_values": "重视全人教育，培养独立思考和创新能力",
            "goals": "希望孩子在国际化环境中全面发展",
            "culture": "中西文化融合，重视传统价值观",
            "support_level": "全力支持孩子的教育和发展"
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
                    "advantages": ["STEM项目丰富", "学术环境优秀"],
                    "challenges": ["竞争激烈"],
                    "strategies": ["突出领导力", "展现STEM专长"]
                }
            ],
            "ranking": [
                {"name": "UCC", "reason": "学术和STEM项目匹配度最高"},
                {"name": "Havergal", "reason": "全人教育理念契合"},
                {"name": "SAC", "reason": "传统价值观与家庭背景匹配"}
            ]
        },
        "plans": {
            "academic_preparation": "加强英语写作能力",
            "extracurricular_preparation": "参与更多STEM竞赛",
            "test_preparation": "SSAT目标90th percentile以上"
        },
        "timeline": {
            "deadlines": ["10月完成SSAT", "11月提交申请", "12月参加面试"],
            "milestones": ["材料准备", "面试准备", "最终提交"]
        },
        "tests": {
            "ssat": "目标90th percentile以上",
            "isee": "备选方案",
            "school_tests": "各校特色测试"
        },
        "essays_refs_interview": {
            "essay_themes": ["领导力经历", "STEM兴趣", "社区服务"],
            "recommendation_strategy": "来自指导老师和社团负责人",
            "interview_preparation": "突出环保义卖活动经验"
        },
        "post_offer": {
            "transition_preparation": "提前了解学校文化",
            "academic_planning": "准备学术衔接",
            "social_networking": "建立社交网络"
        }
    }
    
    # 生成完整报告
    print("正在生成完整报告...")
    full_report = writer.compose_full_report(test_data)
    
    print("报告生成完成!")
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


if __name__ == "__main__":
    main()
