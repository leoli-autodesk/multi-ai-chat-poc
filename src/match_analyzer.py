#!/usr/bin/env python3
"""
学校匹配度评分与排序逻辑
实现学生与学校的匹配度计算和排序功能
"""

import json
import logging
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import re

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SchoolScore:
    """学校评分数据结构"""
    name: str
    academic: int
    activities: int
    culture: int
    personality: int
    weights: Dict[str, float]
    match_percentage: int
    rationale: str

class MatchAnalyzer:
    """匹配度分析器"""
    
    def __init__(self, default_weights: Dict[str, float] = None):
        """
        初始化匹配度分析器
        
        Args:
            default_weights: 默认权重配置
        """
        self.default_weights = default_weights or {
            "academic": 0.35,
            "activities": 0.25,
            "culture": 0.20,
            "personality": 0.20
        }
        
        # 验证权重总和
        if abs(sum(self.default_weights.values()) - 1.0) > 0.01:
            logger.warning("权重总和不为1.0，将自动调整")
            total = sum(self.default_weights.values())
            self.default_weights = {k: v/total for k, v in self.default_weights.items()}
    
    def compute_match_percentage(self, scores: Dict[str, int], weights: Dict[str, float] = None) -> int:
        """
        计算匹配度百分比
        
        Args:
            scores: 各维度得分 (1-5分)
            weights: 权重配置
            
        Returns:
            匹配度百分比 (0-100)
        """
        if weights is None:
            weights = self.default_weights
        
        # 验证权重总和
        if abs(sum(weights.values()) - 1.0) > 0.01:
            logger.warning("权重总和不为1.0，使用默认权重")
            weights = self.default_weights
        
        # 检查缺失分数并设置默认值
        for dimension in self.default_weights.keys():
            if dimension not in scores or scores[dimension] is None:
                logger.warning(f"维度 {dimension} 缺失分数，设置为默认值3分")
                scores[dimension] = 3
        
        # 验证分数范围
        for dimension, score in scores.items():
            if not isinstance(score, (int, float)) or score < 1 or score > 5:
                logger.warning(f"维度 {dimension} 分数 {score} 超出范围(1-5)，设置为3分")
                scores[dimension] = 3
        
        # 计算加权总分
        weighted_score = sum(scores[dim] * weights[dim] for dim in weights.keys())
        
        # 转换为百分比 (1-5分 -> 0-100%)
        percentage = int(round(weighted_score * 20))
        
        # 确保在0-100范围内
        percentage = max(0, min(100, percentage))
        
        return percentage
    
    def generate_rationale(self, school_name: str, scores: Dict[str, int], 
                          student_profile: Dict[str, Any]) -> str:
        """
        生成推荐理由
        
        Args:
            school_name: 学校名称
            scores: 各维度得分
            student_profile: 学生画像
            
        Returns:
            推荐理由文本
        """
        # 找出最高分的维度
        max_score_dim = max(scores.items(), key=lambda x: x[1])
        max_dimension = max_score_dim[0]
        max_score = max_score_dim[1]
        
        # 维度中文映射
        dimension_names = {
            "academic": "学术能力",
            "activities": "活动资源",
            "culture": "文化价值观",
            "personality": "性格氛围"
        }
        
        # 学生特点映射
        student_traits = {
            "academic": student_profile.get("academic_strengths", "学术基础扎实"),
            "activities": student_profile.get("leadership_positions", "领导力突出"),
            "culture": student_profile.get("family_culture", "家庭价值观良好"),
            "personality": student_profile.get("learning_ability", "学习适应能力强")
        }
        
        # 生成推荐理由
        rationale_parts = []
        
        # 主要匹配点
        if max_score >= 4:
            rationale_parts.append(f"在{dimension_names[max_dimension]}方面表现突出")
        
        # 学生特点匹配
        if max_dimension in student_traits:
            rationale_parts.append(f"学生{student_traits[max_dimension]}与学校特色高度契合")
        
        # 综合评估
        total_score = sum(scores.values())
        if total_score >= 16:  # 平均4分以上
            rationale_parts.append("综合匹配度优秀")
        elif total_score >= 12:  # 平均3分以上
            rationale_parts.append("匹配度良好")
        else:
            rationale_parts.append("有提升空间但具备潜力")
        
        # 限制长度在40-60字
        rationale = "，".join(rationale_parts)
        if len(rationale) > 60:
            rationale = rationale[:57] + "..."
        
        return rationale
    
    def rank_schools(self, target_schools: List[Dict[str, Any]], 
                    student_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        对学校进行排序
        
        Args:
            target_schools: 目标学校列表
            student_profile: 学生画像
            
        Returns:
            排序后的学校信息和top3推荐
        """
        school_scores = []
        
        for school in target_schools:
            # 获取分数和权重
            scores = school.get("scores", {})
            weights = school.get("weights", self.default_weights)
            
            # 计算匹配度
            match_percentage = self.compute_match_percentage(scores, weights)
            
            # 生成推荐理由
            rationale = self.generate_rationale(school["name"], scores, student_profile)
            
            # 创建学校评分对象
            school_score = SchoolScore(
                name=school["name"],
                academic=scores.get("academic", 3),
                activities=scores.get("activities", 3),
                culture=scores.get("culture", 3),
                personality=scores.get("personality", 3),
                weights=weights,
                match_percentage=match_percentage,
                rationale=rationale
            )
            
            school_scores.append(school_score)
        
        # 按匹配度排序
        school_scores.sort(key=lambda x: x.match_percentage, reverse=True)
        
        # 更新学校数据
        for i, school_score in enumerate(school_scores):
            for school in target_schools:
                if school["name"] == school_score.name:
                    school["match_percentage"] = f"{school_score.match_percentage}"
                    school["rationale"] = school_score.rationale
                    break
        
        # 生成top3推荐
        top_recommendations = {}
        for i in range(min(3, len(school_scores))):
            school_score = school_scores[i]
            top_recommendations[f"top{i+1}"] = {
                "name": school_score.name,
                "match_percentage": f"{school_score.match_percentage}",
                "reason": school_score.rationale
            }
        
        return {
            "target_schools": target_schools,
            "top_recommendations": top_recommendations,
            "ranking_summary": f"共评估{len(school_scores)}所学校，推荐前3名"
        }
    
    def analyze_student_school_fit(self, student_data: Dict[str, Any], 
                                 school_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析学生与学校的匹配度
        
        Args:
            student_data: 学生数据
            school_data: 学校数据
            
        Returns:
            匹配度分析结果
        """
        # 提取学生画像
        student_profile = {
            "academic_strengths": student_data.get("academic_strengths", ""),
            "leadership_positions": student_data.get("leadership_positions", ""),
            "family_culture": student_data.get("family", {}).get("culture", ""),
            "learning_ability": student_data.get("learning_ability", ""),
            "competition_achievements": student_data.get("competition_achievements", ""),
            "project_experiences": student_data.get("project_experiences", "")
        }
        
        # 获取目标学校
        target_schools = student_data.get("target_schools", [])
        
        # 为每个学校计算匹配度
        for school in target_schools:
            school_name = school["name"]
            
            # 基于学校特点和学生特点计算各维度分数
            scores = self._calculate_dimension_scores(school_name, school_data, student_profile)
            school["scores"] = scores
            
            # 设置默认权重
            if "weights" not in school:
                school["weights"] = self.default_weights.copy()
        
        # 排序学校
        ranking_result = self.rank_schools(target_schools, student_profile)
        
        return ranking_result
    
    def _calculate_dimension_scores(self, school_name: str, school_data: Dict[str, Any], 
                                   student_profile: Dict[str, Any]) -> Dict[str, int]:
        """
        计算各维度分数
        
        Args:
            school_name: 学校名称
            school_data: 学校数据
            student_profile: 学生画像
            
        Returns:
            各维度分数
        """
        scores = {"academic": 3, "activities": 3, "culture": 3, "personality": 3}
        
        if school_name not in school_data.get("schools", {}):
            logger.warning(f"未找到学校 {school_name} 的详细数据，使用默认分数")
            return scores
        
        school_info = school_data["schools"][school_name]
        
        # 学术维度评分
        scores["academic"] = self._score_academic_dimension(school_info, student_profile)
        
        # 活动维度评分
        scores["activities"] = self._score_activities_dimension(school_info, student_profile)
        
        # 文化维度评分
        scores["culture"] = self._score_culture_dimension(school_info, student_profile)
        
        # 性格维度评分
        scores["personality"] = self._score_personality_dimension(school_info, student_profile)
        
        return scores
    
    def _score_academic_dimension(self, school_info: Dict[str, Any], 
                                student_profile: Dict[str, Any]) -> int:
        """学术维度评分"""
        score = 3  # 基础分
        
        # 基于学校学术要求
        requirements = school_info.get("requirements", {})
        academic_req = requirements.get("academic", "")
        
        if "85th percentile" in academic_req:
            score += 1
        elif "80th percentile" in academic_req:
            score += 0
        
        # 基于学生学术成就
        academic_strengths = student_profile.get("academic_strengths", "").lower()
        competition_achievements = student_profile.get("competition_achievements", "")
        
        # 处理competition_achievements可能是列表的情况
        if isinstance(competition_achievements, list):
            competition_achievements = " ".join(competition_achievements).lower()
        else:
            competition_achievements = str(competition_achievements).lower()
        
        if any(keyword in academic_strengths for keyword in ["数学", "物理", "科学", "stem"]):
            score += 1
        if any(keyword in competition_achievements for keyword in ["竞赛", "获奖", "省级", "国家级"]):
            score += 1
        
        return min(5, max(1, score))
    
    def _score_activities_dimension(self, school_info: Dict[str, Any], 
                                  student_profile: Dict[str, Any]) -> int:
        """活动维度评分"""
        score = 3  # 基础分
        
        # 基于学校特色项目
        strengths = school_info.get("strengths", [])
        if "体育" in strengths or "艺术" in strengths:
            score += 1
        
        # 基于学生领导力
        leadership_positions = student_profile.get("leadership_positions", "")
        
        # 处理leadership_positions可能是列表的情况
        if isinstance(leadership_positions, list):
            leadership_positions = " ".join(leadership_positions).lower()
        else:
            leadership_positions = str(leadership_positions).lower()
        
        project_experiences = student_profile.get("project_experiences", "")
        
        # 处理project_experiences可能是列表的情况
        if isinstance(project_experiences, list):
            project_experiences = " ".join(project_experiences).lower()
        else:
            project_experiences = str(project_experiences).lower()
        
        if any(keyword in leadership_positions for keyword in ["学生会", "部长", "主席", "领导"]):
            score += 1
        if any(keyword in project_experiences for keyword in ["组织", "项目", "活动", "义卖"]):
            score += 1
        
        return min(5, max(1, score))
    
    def _score_culture_dimension(self, school_info: Dict[str, Any], 
                               student_profile: Dict[str, Any]) -> int:
        """文化维度评分"""
        score = 3  # 基础分
        
        # 基于学校文化
        culture = school_info.get("culture", "").lower()
        philosophy = school_info.get("philosophy", "").lower()
        
        if any(keyword in culture for keyword in ["创新", "包容", "卓越"]):
            score += 1
        if any(keyword in philosophy for keyword in ["全面发展", "品格培养", "领导力"]):
            score += 1
        
        # 基于家庭文化
        family_culture = student_profile.get("family_culture", "").lower()
        if any(keyword in family_culture for keyword in ["教育", "价值观", "支持"]):
            score += 1
        
        return min(5, max(1, score))
    
    def _score_personality_dimension(self, school_info: Dict[str, Any], 
                                  student_profile: Dict[str, Any]) -> int:
        """性格维度评分"""
        score = 3  # 基础分
        
        # 基于学校氛围
        culture = school_info.get("culture", "").lower()
        if any(keyword in culture for keyword in ["创新", "合作", "团队"]):
            score += 1
        
        # 基于学生学习能力
        learning_ability = student_profile.get("learning_ability", "").lower()
        if any(keyword in learning_ability for keyword in ["自主", "适应", "问题解决"]):
            score += 1
        
        return min(5, max(1, score))

def main():
    """测试匹配度分析器"""
    analyzer = MatchAnalyzer()
    
    # 测试数据
    student_data = {
        "name": "Alex Chen",
        "academic_strengths": "数学、物理、计算机科学",
        "competition_achievements": "机器人竞赛省级二等奖",
        "leadership_positions": "科技部副部长",
        "project_experiences": "环保义卖活动组织",
        "learning_ability": "自主学习和问题解决",
        "family": {
            "culture": "重视教育，支持孩子发展"
        },
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
            },
            {
                "name": "St. Andrew's College",
                "scores": {"academic": 3, "activities": 4, "culture": 3, "personality": 4},
                "weights": {"academic": 0.35, "activities": 0.25, "culture": 0.2, "personality": 0.2}
            }
        ]
    }
    
    school_data = {
        "schools": {
            "Upper Canada College": {
                "requirements": {"academic": "SSAT 85th percentile以上"},
                "strengths": ["学术", "领导力", "体育", "艺术"],
                "culture": "严谨、创新、包容、卓越",
                "philosophy": "培养未来领导者，全面发展"
            },
            "Havergal College": {
                "requirements": {"academic": "SSAT 80th percentile以上"},
                "strengths": ["学术", "STEM", "艺术", "体育"],
                "culture": "创新、独立、自信、服务",
                "philosophy": "培养独立自信的女性领导者"
            },
            "St. Andrew's College": {
                "requirements": {"academic": "SSAT 80th percentile以上"},
                "strengths": ["学术", "体育", "艺术", "寄宿教育"],
                "culture": "传统、卓越、团队精神",
                "philosophy": "全面发展，品格培养"
            }
        }
    }
    
    # 分析匹配度
    result = analyzer.analyze_student_school_fit(student_data, school_data)
    
    print("匹配度分析结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
