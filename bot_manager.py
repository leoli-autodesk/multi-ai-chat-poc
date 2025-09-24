"""
Bot管理器
负责加载和管理所有bot的配置文件
"""

import os
import yaml
from typing import Dict, Any, List
from pathlib import Path

class BotManager:
    """Bot管理器类"""
    
    def __init__(self, config_dir: str = "bots/configs"):
        self.config_dir = config_dir
        self.bots = {}
        self.flow_config = None
        self.load_all_configs()
    
    def load_all_configs(self):
        """加载所有bot配置和流程配置"""
        try:
            # 加载流程配置
            flow_file = os.path.join(self.config_dir, "conversation_flow.yaml")
            if os.path.exists(flow_file):
                with open(flow_file, "r", encoding="utf-8") as f:
                    self.flow_config = yaml.safe_load(f)
                print(f"✅ 加载流程配置: {flow_file}")
            else:
                print(f"❌ 流程配置文件不存在: {flow_file}")
                return
            
            # 加载所有bot配置
            config_files = [
                "admissions_officer.yaml",
                "parent.yaml", 
                "student.yaml",
                "advisor.yaml",
                "writer.yaml"
            ]
            
            for config_file in config_files:
                bot_id = config_file.replace(".yaml", "")
                config_path = os.path.join(self.config_dir, config_file)
                
                if os.path.exists(config_path):
                    with open(config_path, "r", encoding="utf-8") as f:
                        bot_config = yaml.safe_load(f)
                        self.bots[bot_id] = bot_config
                        print(f"✅ 加载Bot配置: {bot_id}")
                else:
                    print(f"❌ Bot配置文件不存在: {config_path}")
            
            print(f"✅ 成功加载 {len(self.bots)} 个Bot配置")
            
        except Exception as e:
            print(f"❌ 加载配置失败: {e}")
            raise
    
    def get_bot_config(self, bot_id: str) -> Dict[str, Any]:
        """获取指定bot的配置"""
        return self.bots.get(bot_id, {})
    
    def get_bot_system_prompt(self, bot_id: str) -> str:
        """获取指定bot的系统提示词"""
        bot_config = self.get_bot_config(bot_id)
        return bot_config.get("system_prompt", "")
    
    def get_bot_output_schema(self, bot_id: str) -> List[str]:
        """获取指定bot的输出字段定义"""
        bot_config = self.get_bot_config(bot_id)
        return bot_config.get("output_schema", [])
    
    def get_bot_weight(self, bot_id: str) -> float:
        """获取指定bot的权重"""
        bot_config = self.get_bot_config(bot_id)
        return bot_config.get("weight", 1.0)
    
    def get_speaking_order(self) -> List[str]:
        """获取发言顺序"""
        if self.flow_config:
            return self.flow_config.get("speaking_order", [])
        return []
    
    def get_context_visibility(self, bot_id: str) -> List[str]:
        """获取指定bot的上下文可见性"""
        bot_config = self.get_bot_config(bot_id)
        return bot_config.get("context_visibility", [])
    
    def get_max_rounds(self) -> int:
        """获取最大轮次数"""
        if self.flow_config:
            return self.flow_config.get("rounds", {}).get("max_rounds", 10)
        return 10
    
    def get_context_isolation_rules(self) -> Dict[str, Dict[str, Any]]:
        """获取上下文隔离规则"""
        if self.flow_config:
            return self.flow_config.get("context_isolation", {})
        return {}
    
    def filter_context_for_bot(self, bot_id: str, full_context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """为指定bot过滤上下文"""
        isolation_rules = self.get_context_isolation_rules()
        bot_rules = isolation_rules.get(bot_id, {})
        
        visible_roles = bot_rules.get("visible_roles", [])
        hidden_roles = bot_rules.get("hidden_roles", [])
        
        if not visible_roles and not hidden_roles:
            # 如果没有隔离规则，返回完整上下文
            return full_context
        
        filtered_context = []
        for entry in full_context:
            role = entry.get("role", "")
            
            # 将角色名转换为小写进行匹配
            role_lower = role.lower()
            
            # 如果指定了可见角色，只保留可见角色
            if visible_roles:
                if role_lower in visible_roles:
                    filtered_context.append(entry)
            # 如果指定了隐藏角色，排除隐藏角色
            elif hidden_roles:
                if role_lower not in hidden_roles:
                    filtered_context.append(entry)
            else:
                filtered_context.append(entry)
        
        return filtered_context
    
    def get_all_bot_ids(self) -> List[str]:
        """获取所有bot的ID列表"""
        return list(self.bots.keys())
    
    def get_bot_name(self, bot_id: str) -> str:
        """获取bot的显示名称"""
        bot_config = self.get_bot_config(bot_id)
        return bot_config.get("name", bot_id)
    
    def get_bot_description(self, bot_id: str) -> str:
        """获取bot的描述"""
        bot_config = self.get_bot_config(bot_id)
        return bot_config.get("description", "")
    
    def get_bot_keywords(self, bot_id: str) -> Dict[str, List[str]]:
        """获取bot的关键词映射"""
        bot_config = self.get_bot_config(bot_id)
        return bot_config.get("keywords", {"positive": [], "negative": []})
    
    def get_bot_topic_weights(self, bot_id: str) -> Dict[str, float]:
        """获取bot的话题权重"""
        bot_config = self.get_bot_config(bot_id)
        return bot_config.get("topic_weights", {})
    
    def validate_config(self) -> bool:
        """验证配置的完整性"""
        required_bots = ["admissions_officer", "parent", "student", "advisor", "writer"]
        
        for bot_id in required_bots:
            if bot_id not in self.bots:
                print(f"❌ 缺少必需的Bot配置: {bot_id}")
                return False
            
            bot_config = self.bots[bot_id]
            required_fields = ["name", "system_prompt", "weight"]
            
            for field in required_fields:
                if field not in bot_config:
                    print(f"❌ Bot {bot_id} 缺少必需字段: {field}")
                    return False
        
        if not self.flow_config:
            print("❌ 缺少流程配置")
            return False
        
        required_flow_fields = ["speaking_order", "rounds"]
        for field in required_flow_fields:
            if field not in self.flow_config:
                print(f"❌ 流程配置缺少必需字段: {field}")
                return False
        
        print("✅ 配置验证通过")
        return True
    
    def print_config_summary(self):
        """打印配置摘要"""
        print("\n" + "="*60)
        print("Bot配置摘要")
        print("="*60)
        
        for bot_id, config in self.bots.items():
            name = config.get("name", bot_id)
            weight = config.get("weight", 1.0)
            print(f"• {bot_id}: {name} (权重: {weight})")
        
        print(f"\n发言顺序: {' → '.join(self.get_speaking_order())}")
        print(f"最大轮次: {self.get_max_rounds()}")
        
        print("\n上下文隔离规则:")
        isolation_rules = self.get_context_isolation_rules()
        for bot_id, rules in isolation_rules.items():
            visible = rules.get("visible_roles", [])
            hidden = rules.get("hidden_roles", [])
            print(f"• {bot_id}: 可见={visible}, 隐藏={hidden}")
        
        print("="*60)
