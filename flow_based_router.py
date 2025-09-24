"""
改进的智能路由系统模块
使用Bot管理器和固定发言顺序，确保每轮所有bot都发言
"""

import json
import re
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from bot_manager import BotManager

class FlowBasedRouter:
    """基于流程的路由器类"""
    
    def __init__(self, bot_manager: BotManager):
        self.bot_manager = bot_manager
        self.logging_enabled = True
        
    def log_decision(self, message: str, level: str = "info"):
        """记录路由决策日志"""
        if self.logging_enabled:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [ROUTER-{level.upper()}] {message}")
    
    def run_complete_round(self, context: List[Dict[str, Any]], needed_info: List[str], 
                          round_num: int, ai_interface, config, school_data, conversations) -> Dict[str, Any]:
        """运行完整的一轮对话（包含所有角色，按固定顺序）"""
        self.log_decision(f"开始第{round_num}轮完整对话")
        
        round_messages = []
        speaking_order = self.bot_manager.get_speaking_order()
        
        if not speaking_order:
            raise Exception("未找到发言顺序配置")
        
        self.log_decision(f"发言顺序: {' → '.join(speaking_order)}")
        
        # 构建基础payload
        base_payload = {
            "FAMILY_INTRO": conversations.get("current_form_data", {}).get("FAMILY_INTRO", ""),
            "TARGET_SCHOOLS": conversations.get("current_form_data", {}).get("TARGET_SCHOOLS", ""),
            "SCHOOL_DATA": school_data,
            "NEEDED_INFO": needed_info,
            "ROUND": round_num,
            "MAX_CONTENT_LENGTH": config.get("globals", {}).get("max_content_length", 300),
            "RESPONSE_TIMEOUT": config.get("globals", {}).get("response_timeout", 30)
        }
        
        # 按固定顺序让每个bot发言
        for bot_id in speaking_order:
            try:
                self.log_decision(f"Bot {bot_id} 开始发言")
                
                # 获取bot的上下文（应用隔离规则）
                # 只传递之前轮次的内容，不包含当前轮次
                bot_context = self.bot_manager.filter_context_for_bot(bot_id, context)
                
                # 构建bot特定的payload
                bot_payload = base_payload.copy()
                context_summary = self.summarize_context(bot_context)
                bot_payload["CONTEXT_WINDOW"] = context_summary
                bot_payload["context"] = bot_context  # 添加context字段供ContextAnalyzer使用
                
                # 调试信息
                self.log_decision(f"Bot {bot_id} 上下文: {context_summary[:100]}...")
                
                # 获取bot的系统提示词
                system_prompt = self.bot_manager.get_bot_system_prompt(bot_id)
                bot_name = self.bot_manager.get_bot_name(bot_id)
                
                # 调用AI
                response = ai_interface.call_llm(bot_name, system_prompt, bot_payload)
                
                # 添加到本轮消息
                round_messages.append({"role": bot_name, "content": response})
                
                self.log_decision(f"Bot {bot_id} 发言完成")
                
            except Exception as e:
                self.log_decision(f"Bot {bot_id} 发言失败: {e}", "ERROR")
                # 添加错误消息
                bot_name = self.bot_manager.get_bot_name(bot_id)
                round_messages.append({
                    "role": bot_name, 
                    "content": {"error": f"发言失败: {str(e)}"}
                })
        
        self.log_decision(f"第{round_num}轮对话完成，生成了{len(round_messages)}条消息")
        
        return {
            "round_num": round_num,
            "messages": round_messages,
            "status": "round_completed"
        }
    
    def should_continue_conversation(self, context: List[Dict[str, Any]], 
                                   needed_info: List[str], round_num: int) -> bool:
        """判断是否应该继续对话"""
        max_rounds = self.bot_manager.get_max_rounds()
        
        # 检查是否达到最大轮次
        if round_num >= max_rounds:
            self.log_decision(f"达到最大轮次 {max_rounds}，结束对话")
            return False
        
        # 强制运行10轮对话
        if round_num < 10:
            self.log_decision(f"第{round_num}轮，继续对话（需要运行10轮）")
            return True
        
        return False
    
    def analyze_conversation_progress(self, recent_context: List[Dict[str, Any]]) -> float:
        """分析对话进展"""
        if not recent_context:
            return 0.0
        
        progress_score = 0.0
        for entry in recent_context:
            content = str(entry.get("content", "")).lower()
            
            # 检查是否有新信息
            if any(word in content for word in ["新", "补充", "详细", "具体", "明确"]):
                progress_score += 0.3
            
            # 检查是否有解决方案
            if any(word in content for word in ["建议", "方案", "计划", "策略"]):
                progress_score += 0.4
            
            # 检查是否有评估
            if any(word in content for word in ["评估", "分析", "总结", "结论"]):
                progress_score += 0.3
        
        return min(1.0, progress_score)
    
    def summarize_context(self, context: List[Dict[str, Any]]) -> str:
        """总结上下文内容，让AI更容易理解"""
        if not context:
            return "对话尚未开始"
        
        summary_parts = []
        summary_parts.append("=== 之前的对话内容 ===")
        
        for i, entry in enumerate(context[-8:], 1):  # 取最近8条消息
            role = entry.get("role", "Unknown")
            content = entry.get("content", "")
            
            if isinstance(content, dict):
                # 如果是字典，提取关键信息
                if "questions" in content:
                    questions = content.get('questions', [])
                    summary_parts.append(f"{i}. {role} 提问: {', '.join(questions)}")
                elif "direct_answer" in content:
                    answer = content.get('direct_answer', '')[:100]
                    summary_parts.append(f"{i}. {role} 回答: {answer}...")
                elif "my_answer" in content:
                    answer = content.get('my_answer', '')[:100]
                    summary_parts.append(f"{i}. {role} 回答: {answer}...")
                elif "snapshot_assessment" in content:
                    assessment = content.get('snapshot_assessment', '')[:100]
                    summary_parts.append(f"{i}. {role} 评估: {assessment}...")
                else:
                    # 其他内容，提取前100字符
                    content_str = str(content)[:100]
                    summary_parts.append(f"{i}. {role}: {content_str}...")
            else:
                content_str = str(content)[:100]
                summary_parts.append(f"{i}. {role}: {content_str}...")
        
        summary_parts.append("=== 请基于以上内容调整你的回答 ===")
        return "\n".join(summary_parts)
    
    def get_conversation_summary(self, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """获取对话总结"""
        if not context:
            return {"summary": "对话尚未开始", "key_points": [], "progress": 0.0}
        
        # 按角色分组消息
        role_messages = {}
        for entry in context:
            role = entry.get("role", "Unknown")
            if role not in role_messages:
                role_messages[role] = []
            role_messages[role].append(entry.get("content", ""))
        
        # 计算进展
        progress = self.analyze_conversation_progress(context)
        
        # 提取关键点
        key_points = []
        for role, messages in role_messages.items():
            if messages:
                key_points.append(f"{role}: {len(messages)}条消息")
        
        return {
            "summary": f"对话进行中，共{len(context)}条消息",
            "key_points": key_points,
            "progress": progress,
            "role_distribution": {role: len(msgs) for role, msgs in role_messages.items()}
        }
    
    def get_routing_recommendation(self, context: List[Dict[str, Any]], 
                                 needed_info: List[str]) -> Dict[str, Any]:
        """获取路由建议（基于固定流程）"""
        speaking_order = self.bot_manager.get_speaking_order()
        
        if not context:
            return {
                "next_speaker": speaking_order[0] if speaking_order else "admissions_officer",
                "reasoning": "对话开始，按固定顺序发言",
                "priority": "high"
            }
        
        # 检查是否应该开始新的一轮
        messages_per_round = len(speaking_order)
        if len(context) % messages_per_round == 0:
            return {
                "next_speaker": speaking_order[0] if speaking_order else "admissions_officer",
                "reasoning": "开始新的一轮对话",
                "priority": "high"
            }
        
        # 根据当前轮次中的位置决定下一步
        current_position = len(context) % messages_per_round
        
        if current_position < len(speaking_order):
            next_bot = speaking_order[current_position]
            return {
                "next_speaker": next_bot,
                "reasoning": f"按固定顺序，下一个发言者是 {next_bot}",
                "priority": "high"
            }
        
        return {
            "next_speaker": speaking_order[0] if speaking_order else "admissions_officer",
            "reasoning": "默认选择第一个bot",
            "priority": "medium"
        }
