#!/usr/bin/env python3
"""
去重精修流水线
实现语义+字符双通道去重器，对writer产出的全文做精修
"""

import json
import re
import logging
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from cursor_ai import CursorAI

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DedupeAndPolish:
    """语义+字符双通道去重器"""
    
    def __init__(self, config_dir: str = "config"):
        """
        初始化去重器
        
        Args:
            config_dir: 配置目录路径
        """
        self.config_dir = Path(config_dir)
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # 初始化AI接口
        self.ai = CursorAI({
            "globals": {"max_content_length": 300},
            "model_config": {
                "default_model": "gpt-4o",
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2000
            }
        })
        
        # 模板句黑名单
        self.template_blacklist = [
            "学术卓越，领导力培养，校友网络强大",
            "在学术能力方面表现突出，与学校特色高度契合",
            "展现领导力和创新思维",
            "全人教育理念",
            "国际化程度高",
            "我们的专业价值",
            "成功保障",
            "专业团队",
            "丰富经验",
            "优质服务"
        ]
        
        # 学校相关关键词（用于差异化改写）
        self.school_keywords = {
            "项目": ["STEM", "AP", "IB", "STEAM", "机器人", "编程", "科学实验"],
            "课程": ["数学", "物理", "化学", "生物", "计算机", "艺术", "音乐", "体育"],
            "活动": ["社团", "竞赛", "辩论", "模拟联合国", "学生会", "志愿者"],
            "设施": ["实验室", "图书馆", "体育馆", "艺术中心", "宿舍", "食堂"],
            "文化": ["传统", "价值观", "多元化", "包容性", "创新", "卓越"],
            "地理": ["多伦多", "温哥华", "蒙特利尔", "郊区", "市区", "寄宿", "走读"]
        }
    
    def dedupe_and_polish(self, fulltext: str, ctx: Dict[str, Any]) -> str:
        """
        去重和精修主函数
        
        Args:
            fulltext: 完整文本
            ctx: 上下文信息（包含sectionAnchors等）
            
        Returns:
            去重后的文本
        """
        logger.info("开始去重精修流程...")
        
        # 1. 分割段落
        paras = self.split_to_paragraphs(fulltext)
        logger.info(f"分割得到 {len(paras)} 个段落")
        
        # 2. 计算向量相似度
        vectors = self.embed_paragraphs(paras)
        
        # 3. 初始化保留标记
        keep = [True] * len(paras)
        actions = []
        
        # 4. 检测重复段落
        for i in range(len(paras)):
            for j in range(i + 1, len(paras)):
                if not keep[i] or not keep[j]:
                    continue
                
                sim = self.cosine_similarity(vectors[i], vectors[j])
                
                # 检查是否高度重复
                if sim >= 0.92 or (sim >= 0.85 and self.has_shared_key_phrases(paras[i], paras[j])):
                    chosen_idx, replaced_idx = self.choose_paragraph_to_keep(paras[i], paras[j], i, j)
                    
                    # 检查是否在同一学校块内
                    anchor = self.in_same_school_block(paras[i], paras[j], ctx)
                    
                    if anchor:
                        # 改写为该校独有角度
                        paras[replaced_idx] = self.llm_rephrase_unique(
                            paras[replaced_idx], anchor
                        )
                        actions.append({
                            "type": "rephrase",
                            "i": i,
                            "j": j,
                            "sim": sim,
                            "reason": "同校块内重复，改写为独有角度"
                        })
                    else:
                        # 直接删除低信息量段落
                        keep[replaced_idx] = False
                        actions.append({
                            "type": "drop",
                            "i": i,
                            "j": j,
                            "sim": sim,
                            "reason": "跨章节重复，删除低信息量段落"
                        })
        
        # 5. 处理模板句黑名单
        template_actions = self.enforce_template_blacklist(paras, keep)
        actions.extend(template_actions)
        
        # 6. 重建文本
        cleaned_paras = [paras[i] for i in range(len(paras)) if keep[i]]
        joined = self.rebuild_with_clean_spacing(cleaned_paras)
        
        # 7. 记录日志
        self.log_dedupe_report(actions)
        
        logger.info(f"去重完成，删除了 {len(paras) - len(cleaned_paras)} 个重复段落")
        return joined
    
    def split_to_paragraphs(self, text: str) -> List[str]:
        """分割文本为段落"""
        # 按双换行分割段落
        paragraphs = re.split(r'\n\s*\n', text)
        
        # 清理段落
        cleaned_paras = []
        for para in paragraphs:
            para = para.strip()
            if para and len(para) > 20:  # 过滤过短的段落
                cleaned_paras.append(para)
        
        return cleaned_paras
    
    def embed_paragraphs(self, paragraphs: List[str]) -> List[List[float]]:
        """计算段落向量（简化版，使用字符级特征）"""
        vectors = []
        
        for para in paragraphs:
            # 使用简化的特征向量（字符频率、长度、关键词密度等）
            vector = self.compute_simple_vector(para)
            vectors.append(vector)
        
        return vectors
    
    def compute_simple_vector(self, text: str) -> List[float]:
        """计算简化的文本向量"""
        # 字符长度特征
        length_feature = min(len(text) / 500, 1.0)  # 归一化到0-1
        
        # 关键词密度特征
        keyword_features = []
        for category, keywords in self.school_keywords.items():
            density = sum(text.count(keyword) for keyword in keywords) / len(text) * 100
            keyword_features.append(density)
        
        # 模板句特征
        template_features = []
        for template in self.template_blacklist:
            template_features.append(1.0 if template in text else 0.0)
        
        # 组合所有特征
        vector = [length_feature] + keyword_features + template_features
        
        # 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = [v / norm for v in vector]
        
        return vector
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def has_shared_key_phrases(self, para1: str, para2: str, min_len: int = 12, min_count: int = 3) -> bool:
        """检查是否有共享关键短语"""
        # 提取长度>=min_len的子串
        def extract_substrings(text: str, min_length: int) -> set:
            substrings = set()
            for i in range(len(text) - min_length + 1):
                substrings.add(text[i:i + min_length])
            return substrings
        
        substrings1 = extract_substrings(para1, min_len)
        substrings2 = extract_substrings(para2, min_len)
        
        shared_count = len(substrings1.intersection(substrings2))
        return shared_count >= min_count
    
    def choose_paragraph_to_keep(self, para1: str, para2: str, idx1: int, idx2: int) -> Tuple[int, int]:
        """选择保留哪个段落（基于信息密度）"""
        density1 = self.info_density(para1)
        density2 = self.info_density(para2)
        
        if density1 >= density2:
            return idx1, idx2
        else:
            return idx2, idx1
    
    def info_density(self, text: str) -> float:
        """计算信息密度"""
        # 实体名数量
        entities = len(re.findall(r'[A-Z][a-z]+ [A-Z][a-z]+', text))  # 人名、地名等
        
        # 数字数量
        numbers = len(re.findall(r'\d+', text))
        
        # 具体动作/里程碑
        actions = len(re.findall(r'(完成|实现|达到|获得|参与|组织|领导)', text))
        
        # 总长度
        length = len(text)
        
        if length == 0:
            return 0.0
        
        # 信息密度 = (实体 + 数字 + 动作) / 长度
        density = (entities + numbers + actions) / length * 100
        return density
    
    def in_same_school_block(self, para1: str, para2: str, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """检查两个段落是否在同一学校块内"""
        section_anchors = ctx.get("sectionAnchors", [])
        
        # 检查是否都包含学校名称
        school_names = ["Upper Canada College", "Havergal College", "St. Andrew's College", "UCC", "SAC"]
        
        para1_schools = [school for school in school_names if school in para1]
        para2_schools = [school for school in school_names if school in para2]
        
        if para1_schools and para2_schools:
            common_schools = set(para1_schools).intersection(set(para2_schools))
            if common_schools:
                return {
                    "school": list(common_schools)[0],
                    "meta": {
                        "school_name": list(common_schools)[0],
                        "context": "学校推荐理由或潜在挑战"
                    }
                }
        
        return None
    
    def llm_rephrase_unique(self, paragraph: str, anchor: Dict[str, Any]) -> str:
        """
        使用LLM改写段落为该校独有角度
        
        Args:
            paragraph: 待改写段落
            anchor: 学校上下文信息
            
        Returns:
            改写后的段落
        """
        school_name = anchor["meta"]["school_name"]
        
        system_prompt = """你是一名专业的学校申请顾问，负责改写重复的段落内容，使其更具针对性和独特性。"""
        
        user_prompt = f"""请将以下段落改写为针对 {school_name} 的独有角度，避免模板化表述：

原段落：{paragraph}

改写要求：
1. 必须包含该校的具体项目名、课程设置、社团活动、设施特色等独有信息
2. 禁止使用"学术卓越、领导力培养、校友网络强大"等通用模板句
3. 补充该校的具体文化特色、地理位置、寄宿/走读制度等细节
4. 保持专业、客观的语调，避免营销性语言
5. 字数与原段落相近
6. 输出纯文本，不使用任何Markdown格式

改写后的段落："""
        
        try:
            response = self.ai.call_llm("Writer", system_prompt, {"content": user_prompt})
            if isinstance(response, str):
                return response.strip()
            else:
                return paragraph
        except Exception as e:
            logger.error(f"LLM改写失败: {e}")
            return paragraph
    
    def enforce_template_blacklist(self, paragraphs: List[str], keep: List[bool]) -> List[Dict[str, Any]]:
        """执行模板句黑名单规则"""
        actions = []
        template_counts = {}
        
        for i, para in enumerate(paragraphs):
            if not keep[i]:
                continue
                
            for template in self.template_blacklist:
                if template in para:
                    template_counts[template] = template_counts.get(template, 0) + 1
                    
                    # 如果出现超过1次，改写后续出现的
                    if template_counts[template] > 1:
                        # 改写为承接+新增信息
                        rewritten = self.rewrite_template_sentence(para, template)
                        paragraphs[i] = rewritten
                        
                        actions.append({
                            "type": "template_rewrite",
                            "paragraph_idx": i,
                            "template": template,
                            "reason": f"模板句'{template}'重复出现"
                        })
        
        return actions
    
    def rewrite_template_sentence(self, paragraph: str, template: str) -> str:
        """改写模板句为承接+新增信息"""
        # 简单的改写策略：替换模板句
        replacements = {
            "学术卓越，领导力培养，校友网络强大": "该校在STEM教育方面具有独特优势，特别是在机器人竞赛和科学实验项目上表现突出",
            "在学术能力方面表现突出，与学校特色高度契合": "学生的数学和物理专长与该校的AP课程体系高度匹配",
            "展现领导力和创新思维": "通过环保义卖等具体项目展现了实际的组织能力和创新精神",
            "全人教育理念": "该校注重学术与品格并重的教育理念",
            "国际化程度高": "该校拥有多元化的学生群体和丰富的国际交流项目"
        }
        
        if template in replacements:
            return paragraph.replace(template, replacements[template])
        
        return paragraph
    
    def rebuild_with_clean_spacing(self, paragraphs: List[str]) -> str:
        """重建文本并清理间距"""
        # 合并段落，确保适当的间距
        cleaned_text = "\n\n".join(paragraphs)
        
        # 清理多余的空行
        cleaned_text = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_text)
        
        return cleaned_text.strip()
    
    def log_dedupe_report(self, actions: List[Dict[str, Any]]) -> None:
        """记录去重报告"""
        report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_actions": len(actions),
            "actions": actions,
            "summary": {
                "rephrase_count": len([a for a in actions if a["type"] == "rephrase"]),
                "drop_count": len([a for a in actions if a["type"] == "drop"]),
                "template_rewrite_count": len([a for a in actions if a["type"] == "template_rewrite"])
            }
        }
        
        log_file = self.logs_dir / "dedupe_report.json"
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"去重报告已保存: {log_file}")
        except Exception as e:
            logger.error(f"保存去重报告失败: {e}")
    
    def validate_dedupe_result(self, original_text: str, deduped_text: str) -> Dict[str, Any]:
        """验证去重结果"""
        validation = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "original_length": len(original_text),
            "deduped_length": len(deduped_text),
            "length_reduction": len(original_text) - len(deduped_text),
            "reduction_percentage": (len(original_text) - len(deduped_text)) / len(original_text) * 100 if len(original_text) > 0 else 0,
            "meets_criteria": True,
            "issues": []
        }
        
        # 检查字数保护（不能减少超过8%）
        if validation["reduction_percentage"] > 8:
            validation["meets_criteria"] = False
            validation["issues"].append(f"字数减少过多: {validation['reduction_percentage']:.1f}%")
        
        # 检查是否还有重复段落
        original_paras = self.split_to_paragraphs(original_text)
        deduped_paras = self.split_to_paragraphs(deduped_text)
        
        if len(deduped_paras) < len(original_paras) * 0.5:
            validation["meets_criteria"] = False
            validation["issues"].append("删除段落过多，可能影响内容完整性")
        
        return validation


def main():
    """测试去重器"""
    dedupe = DedupeAndPolish()
    
    # 测试文本（包含重复内容）
    test_text = """
    家庭与学生背景

    Alex Chen是一名14岁的八年级学生，在数学、物理和计算机科学方面表现突出。他的GPA为3.8/4.0，在机器人竞赛中获得省级二等奖。作为科技部副部长，他展现了出色的领导力和组织能力。

    学校申请定位

    基于Alex的学术优势和家庭价值观，我们推荐申请多伦多地区的顶级私立学校。这些学校在学术卓越、领导力培养、校友网络强大方面具有显著优势。

    学生—学校匹配度

    对于Upper Canada College，Alex在学术能力方面表现突出，与学校特色高度契合。该校的STEM项目丰富，能够充分发挥Alex的数学和物理专长。推荐理由包括：学术卓越、领导力培养、校友网络强大。潜在挑战是竞争激烈，需要更强的英语能力。

    对于Havergal College，Alex同样在学术能力方面表现突出，与学校特色高度契合。该校注重全人教育理念，与Alex的家庭价值观匹配。推荐理由包括：学术卓越、领导力培养、校友网络强大。潜在挑战是申请难度较高。

    学术与课外准备

    在学术准备方面，建议Alex加强英语写作能力，保持STEM优势。在课外活动方面，建议参与更多STEM竞赛，发展领导力。在考试准备方面，SSAT目标90th percentile以上。

    申请流程与个性化策略

    申请时间线包括：10月完成SSAT考试，11月提交申请材料，12月参加面试。个性化策略包括：突出领导力，展现STEM专长，强调社区服务。

    录取后延伸建议

    录取后建议：提前了解学校文化，准备学术衔接，建立社交网络。我们的专业价值在于提供全方位的申请指导，确保成功保障。
    """
    
    ctx = {
        "sectionAnchors": ["家庭与学生背景", "学校申请定位", "学生—学校匹配度", "学术与课外准备", "申请流程与个性化策略", "录取后延伸建议"]
    }
    
    # 执行去重
    result = dedupe.dedupe_and_polish(test_text, ctx)
    
    # 验证结果
    validation = dedupe.validate_dedupe_result(test_text, result)
    
    print("去重结果:")
    print(f"原文长度: {validation['original_length']}")
    print(f"去重后长度: {validation['deduped_length']}")
    print(f"减少字数: {validation['length_reduction']}")
    print(f"减少比例: {validation['reduction_percentage']:.1f}%")
    print(f"符合标准: {validation['meets_criteria']}")
    
    if validation['issues']:
        print("问题:")
        for issue in validation['issues']:
            print(f"- {issue}")
    
    print("\n去重后的文本:")
    print(result)


if __name__ == "__main__":
    main()
