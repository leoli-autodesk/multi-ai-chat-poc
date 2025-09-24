"""
上下文分析器
负责分析对话历史，为每个角色提供深度上下文理解
"""

import re
from typing import List, Dict, Any, Tuple
from datetime import datetime

class ContextAnalyzer:
    """对话上下文分析器"""
    
    def __init__(self):
        self.conversation_topics = []
        self.key_points = []
        self.questions_asked = []
        self.answers_given = []
        self.follow_up_needed = []
    
    def analyze_conversation_history(self, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析完整的对话历史"""
        analysis = {
            "topics_discussed": [],
            "key_information": {},
            "questions_unanswered": [],
            "depth_level": 0,
            "conversation_progress": 0.0,
            "next_focus_areas": [],
            "role_specific_insights": {}
        }
        
        if not context:
            return analysis
        
        # 提取所有对话内容
        all_content = []
        for entry in context:
            role = entry.get("role", "Unknown")
            content = entry.get("content", "")
            
            if isinstance(content, dict):
                if "raw_response" in content:
                    text = content["raw_response"]
                elif "error" in content:
                    text = f"[错误] {content['error']}"
                else:
                    text = str(content)
            else:
                text = str(content)
            
            all_content.append({"role": role, "text": text})
        
        # 分析话题
        analysis["topics_discussed"] = self._extract_topics(all_content)
        
        # 分析关键信息
        analysis["key_information"] = self._extract_key_information(all_content)
        
        # 分析未回答的问题
        analysis["questions_unanswered"] = self._find_unanswered_questions(all_content)
        
        # 计算对话深度
        analysis["depth_level"] = self._calculate_depth_level(all_content)
        
        # 计算对话进展
        analysis["conversation_progress"] = self._calculate_progress(all_content)
        
        # 确定下一步重点
        analysis["next_focus_areas"] = self._determine_next_focus(all_content)
        
        # 角色特定洞察
        analysis["role_specific_insights"] = self._generate_role_insights(all_content)
        
        return analysis
    
    def _extract_topics(self, content: List[Dict[str, str]]) -> List[str]:
        """提取讨论的话题"""
        topics = []
        topic_keywords = {
            "学术发展": ["学术", "学习", "教育", "成绩", "课程", "数学", "科学", "英语"],
            "领导力": ["领导", "组织", "管理", "团队", "项目", "活动"],
            "家庭背景": ["家庭", "父母", "教育理念", "支持", "环境"],
            "兴趣爱好": ["兴趣", "爱好", "编程", "音乐", "运动", "实验"],
            "性格特点": ["性格", "内向", "外向", "自信", "沟通", "合作"],
            "未来规划": ["未来", "规划", "目标", "期望", "梦想"]
        }
        
        all_text = " ".join([entry["text"] for entry in content])
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _extract_key_information(self, content: List[Dict[str, str]]) -> Dict[str, List[str]]:
        """提取关键信息"""
        key_info = {
            "student_strengths": [],
            "student_challenges": [],
            "family_values": [],
            "academic_achievements": [],
            "leadership_experiences": []
        }
        
        for entry in content:
            text = entry["text"].lower()
            role = entry["role"]
            
            # 提取学生优势
            if any(word in text for word in ["擅长", "喜欢", "优秀", "强项", "优势"]):
                if role == "Student":
                    key_info["student_strengths"].append(entry["text"])
            
            # 提取挑战
            if any(word in text for word in ["需要", "改进", "挑战", "困难", "不足"]):
                if role == "Student":
                    key_info["student_challenges"].append(entry["text"])
            
            # 提取家庭价值观
            if any(word in text for word in ["教育理念", "价值观", "支持", "鼓励"]):
                if role == "Parent":
                    key_info["family_values"].append(entry["text"])
        
        return key_info
    
    def _find_unanswered_questions(self, content: List[Dict[str, str]]) -> List[str]:
        """找出未充分回答的问题"""
        unanswered = []
        
        # 查找招生官的问题
        for entry in content:
            if entry["role"] == "Admissions Officer":
                text = entry["text"]
                if "？" in text or "?" in text:
                    # 检查后续是否有相关回答
                    question_index = content.index(entry)
                    has_answer = False
                    
                    for i in range(question_index + 1, len(content)):
                        if content[i]["role"] in ["Student", "Parent"]:
                            # 简单检查是否有相关关键词
                            if any(word in content[i]["text"] for word in text.split()[:3]):
                                has_answer = True
                                break
                    
                    if not has_answer:
                        unanswered.append(text)
        
        return unanswered
    
    def _calculate_depth_level(self, content: List[Dict[str, str]]) -> int:
        """计算对话深度级别"""
        depth_indicators = {
            "具体例子": 2,
            "详细描述": 2,
            "数据": 3,
            "反思": 3,
            "挑战": 3,
            "解决方案": 4,
            "深度思考": 4,
            "个人成长": 4
        }
        
        max_depth = 0
        for entry in content:
            text = entry["text"].lower()
            for indicator, level in depth_indicators.items():
                if indicator in text:
                    max_depth = max(max_depth, level)
        
        return max_depth
    
    def _calculate_progress(self, content: List[Dict[str, str]]) -> float:
        """计算对话进展百分比"""
        if not content:
            return 0.0
        
        # 基于话题覆盖度和深度计算进展
        topics_covered = len(self._extract_topics(content))
        max_topics = 6  # 预期讨论的主要话题数
        
        depth_level = self._calculate_depth_level(content)
        max_depth = 4
        
        topic_progress = min(topics_covered / max_topics, 1.0)
        depth_progress = min(depth_level / max_depth, 1.0)
        
        return (topic_progress + depth_progress) / 2
    
    def _determine_next_focus(self, content: List[Dict[str, str]]) -> List[str]:
        """确定下一步重点关注的领域"""
        focus_areas = []
        
        # 分析当前话题覆盖情况
        topics = self._extract_topics(content)
        all_topics = ["学术发展", "领导力", "家庭背景", "兴趣爱好", "性格特点", "未来规划"]
        
        # 找出未充分讨论的话题
        for topic in all_topics:
            if topic not in topics:
                focus_areas.append(f"深入探讨{topic}")
        
        # 基于深度级别确定需要深化的领域
        depth_level = self._calculate_depth_level(content)
        if depth_level < 3:
            focus_areas.append("提供更多具体例子和数据")
        
        if depth_level < 4:
            focus_areas.append("探讨挑战和解决方案")
        
        return focus_areas
    
    def _generate_role_insights(self, content: List[Dict[str, str]]) -> Dict[str, str]:
        """为每个角色生成特定洞察"""
        insights = {}
        
        # 为招生官生成洞察
        insights["admissions_officer"] = self._generate_admissions_insights(content)
        
        # 为顾问生成洞察
        insights["advisor"] = self._generate_advisor_insights(content)
        
        # 为学生生成洞察
        insights["student"] = self._generate_student_insights(content)
        
        # 为家长生成洞察
        insights["parent"] = self._generate_parent_insights(content)
        
        return insights
    
    def _generate_admissions_insights(self, content: List[Dict[str, str]]) -> str:
        """为招生官生成洞察"""
        topics = self._extract_topics(content)
        depth_level = self._calculate_depth_level(content)
        
        insights = []
        
        if "学术发展" not in topics:
            insights.append("需要深入了解学生的学术能力和学习风格")
        
        if "领导力" not in topics:
            insights.append("需要评估学生的领导潜力和团队合作能力")
        
        if depth_level < 3:
            insights.append("需要更多具体例子和数据来评估学生")
        
        if not insights:
            insights.append("可以开始评估学生的整体匹配度")
        
        return "；".join(insights)
    
    def _generate_advisor_insights(self, content: List[Dict[str, str]]) -> str:
        """为顾问生成洞察"""
        unanswered = self._find_unanswered_questions(content)
        focus_areas = self._determine_next_focus(content)
        
        insights = []
        
        if unanswered:
            insights.append(f"需要帮助学生和家长回答：{unanswered[0][:50]}...")
        
        if focus_areas:
            insights.append(f"下一步重点：{focus_areas[0]}")
        
        if not insights:
            insights.append("对话进展良好，可以开始总结和规划")
        
        return "；".join(insights)
    
    def _generate_student_insights(self, content: List[Dict[str, str]]) -> str:
        """为学生生成洞察"""
        key_info = self._extract_key_information(content)
        
        insights = []
        
        if not key_info["student_strengths"]:
            insights.append("需要更自信地分享自己的优势")
        
        if not key_info["student_challenges"]:
            insights.append("可以诚实地讨论需要改进的地方")
        
        if not insights:
            insights.append("继续保持真诚和具体的回答")
        
        return "；".join(insights)
    
    def _generate_parent_insights(self, content: List[Dict[str, str]]) -> str:
        """为家长生成洞察"""
        key_info = self._extract_key_information(content)
        
        insights = []
        
        if not key_info["family_values"]:
            insights.append("需要分享家庭的教育理念和价值观")
        
        if not insights:
            insights.append("继续支持孩子的表达，补充家庭背景信息")
        
        return "；".join(insights)
    
    def generate_context_summary(self, context: List[Dict[str, Any]], role: str) -> str:
        """为特定角色生成上下文摘要"""
        analysis = self.analyze_conversation_history(context)
        
        summary_parts = []
        
        # 添加话题摘要
        if analysis["topics_discussed"]:
            summary_parts.append(f"已讨论话题：{', '.join(analysis['topics_discussed'])}")
        
        # 添加深度级别
        summary_parts.append(f"对话深度：{analysis['depth_level']}/4")
        
        # 添加进展
        progress_pct = int(analysis["conversation_progress"] * 100)
        summary_parts.append(f"对话进展：{progress_pct}%")
        
        # 添加角色特定洞察
        if role in analysis["role_specific_insights"]:
            insights = analysis["role_specific_insights"][role]
            summary_parts.append(f"建议关注：{insights}")
        
        # 添加下一步重点
        if analysis["next_focus_areas"]:
            summary_parts.append(f"下一步重点：{analysis['next_focus_areas'][0]}")
        
        return "；".join(summary_parts)
