"""
新的后端API服务器
使用Bot管理器和流程路由器，支持每轮所有bot发言
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import yaml
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List
import threading
import time
import traceback

# 导入我们的核心模块
from main import load_config, load_school_data
from bot_manager import BotManager
from flow_based_router import FlowBasedRouter
from cursor_ai import CursorAI

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局变量
config = None
school_data = None
bot_manager = None
router = None
ai_interface = None
conversations = {}  # 存储对话状态

def log_to_file(message, level="INFO"):
    """实时写入日志文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{level}] {message}"
    print(log_message)  # 同时输出到控制台
    
    # 写入日志文件
    try:
        os.makedirs("logs", exist_ok=True)
        log_file = "logs/backend_realtime.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
            f.flush()
    except Exception as e:
        print(f"写入日志文件失败: {e}")

def initialize_backend():
    """初始化后端服务"""
    global config, school_data, bot_manager, router, ai_interface
    
    log_to_file("初始化后端服务...")
    
    try:
        # 加载配置和数据
        config = load_config()
        school_data = load_school_data()
        
        # 初始化Bot管理器
        bot_manager = BotManager()
        bot_manager.print_config_summary()
        
        # 验证配置
        if not bot_manager.validate_config():
            raise Exception("Bot配置验证失败")
        
        # 初始化流程路由器和AI接口
        router = FlowBasedRouter(bot_manager)
        ai_interface = CursorAI(config)
        
        log_to_file("后端服务初始化完成")
    except Exception as e:
        log_to_file(f"后端服务初始化失败: {e}", "ERROR")
        log_to_file(traceback.format_exc(), "ERROR")
        raise

def run_conversation_round(conversation_id: str, context: List[Dict[str, Any]], 
                          needed_info: List[str], round_num: int) -> Dict[str, Any]:
    """运行一轮对话（改进版：包含所有角色，按固定顺序）"""
    try:
        log_to_file(f"开始第{round_num}轮完整对话")
        
        # 使用流程路由器运行完整轮次
        round_result = router.run_complete_round(context, needed_info, round_num, ai_interface, config, school_data, conversations)
        
        # 将本轮消息添加到总上下文中
        context.extend(round_result["messages"])
        
        log_to_file(f"第{round_num}轮对话完成，生成了{len(round_result['messages'])}条消息")
        
        # 检查是否需要更多信息
        if context:
            last_entry = context[-1]
            if isinstance(last_entry.get("content"), dict):
                content = last_entry["content"]
                if "asks_to_user" in content and content["asks_to_user"]:
                    needed_info.extend(content["asks_to_user"])
                    log_to_file(f"需要更多信息: {content['asks_to_user']}")
        
        return {
            "status": "continuing",
            "messages": context,
            "needed_info": needed_info,
            "round_num": round_num,
            "round_messages": round_result["messages"]
        }
        
    except Exception as e:
        log_to_file(f"对话轮次执行失败: {e}", "ERROR")
        log_to_file(traceback.format_exc(), "ERROR")
        return {
            "status": "error",
            "error": str(e),
            "messages": context
        }

def save_conversation_log(conversation_id: str, conversation: Dict[str, Any]):
    """保存对话记录到文件"""
    try:
        os.makedirs("logs", exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # 保存为YAML格式（结构化数据）
        yaml_data = {
            "conversation_id": conversation_id,
            "form_data": conversation.get("form_data", {}),
            "messages": conversation.get("context", []),
            "needed_info": conversation.get("needed_info", []),
            "round_num": conversation.get("round_num", 0),
            "status": conversation.get("status", ""),
            "created_at": conversation.get("created_at", ""),
            "completed_at": datetime.now().isoformat()
        }
        yaml_filename = f"logs/conversation_{conversation_id}_{timestamp}.yaml"
        with open(yaml_filename, "w", encoding="utf-8") as f:
            yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True)

        # 保存为TXT格式（可读性强的对话记录）
        txt_filename = f"logs/conversation_{conversation_id}_{timestamp}.txt"
        with open(txt_filename, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("私校申请顾问AI协作系统 - 对话记录\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"对话ID: {conversation_id}\n")
            f.write(f"创建时间: {conversation.get('created_at', '')}\n")
            f.write(f"完成时间: {datetime.now().isoformat()}\n")
            f.write(f"对话轮次: {conversation.get('round_num', 0)}\n")
            f.write(f"状态: {conversation.get('status', '')}\n\n")
            
            # 写入对话内容 - 简化格式
            f.write("对话内容:\n")
            f.write("-" * 40 + "\n")
            for i, msg in enumerate(conversation.get("context", []), 1):
                role = msg.get("role", "Unknown")
                content = msg.get("content", "")
                
                # 简化格式：<Role>: <chat>
                if isinstance(content, dict):
                    # 如果是字典，提取主要信息
                    if "raw_response" in content:
                        content_text = content["raw_response"]
                    elif "error" in content:
                        content_text = f"[错误] {content['error']}"
                    else:
                        content_text = str(content)
                else:
                    content_text = str(content)
                
                # 自动换行，每行不超过80字符
                wrapped_content = ""
                words = content_text.split()
                current_line = ""
                for word in words:
                    if len(current_line + " " + word) <= 80:
                        current_line += (" " + word) if current_line else word
                    else:
                        wrapped_content += current_line + "\n"
                        current_line = word
                if current_line:
                    wrapped_content += current_line
                
                f.write(f"{role}: {wrapped_content}\n\n")
            
            # 写入最终报告
            if conversation.get("report"):
                f.write(f"\n\n最终报告:\n")
                f.write("-" * 40 + "\n")
                f.write(str(conversation["report"]))
        
        log_to_file(f"对话记录已保存:")
        log_to_file(f"  YAML格式: {yaml_filename}")
        log_to_file(f"  TXT格式: {txt_filename}")
    except Exception as e:
        log_to_file(f"保存对话记录失败: {e}", "ERROR")

# API路由
@app.route('/api/start-conversation', methods=['POST'])
def start_conversation():
    """启动新对话"""
    try:
        log_to_file("收到启动对话请求")
        
        form_data = request.json
        conversation_id = str(uuid.uuid4())
        
        conversations[conversation_id] = {
            "conversation_id": conversation_id,
            "form_data": form_data,
            "context": [],
            "needed_info": [],
            "round_num": 0,
            "status": "started",
            "created_at": datetime.now().isoformat()
        }
        
        # 保存当前表单数据供其他函数使用
        conversations["current_form_data"] = form_data
        
        log_to_file(f"对话启动成功: {conversation_id}")
        
        return jsonify({
            "success": True,
            "conversationId": conversation_id
        })
        
    except Exception as e:
        log_to_file(f"启动对话失败: {e}", "ERROR")
        return jsonify({"error": str(e)}), 500

@app.route('/api/conversation/<conversation_id>/start', methods=['POST'])
def start_conversation_round(conversation_id):
    """开始对话轮次"""
    try:
        log_to_file(f"开始对话轮次: {conversation_id}")
        
        if conversation_id not in conversations:
            return jsonify({"error": "对话不存在"}), 404
        
        conversation = conversations[conversation_id]
        conversation["status"] = "running"
        
        log_to_file(f"对话轮次开始成功: {conversation_id}")
        
        return jsonify({"success": True})
        
    except Exception as e:
        log_to_file(f"开始对话轮次失败: {e}", "ERROR")
        return jsonify({"error": str(e)}), 500

@app.route('/api/conversation/<conversation_id>/run', methods=['POST'])
def run_conversation(conversation_id):
    """运行对话"""
    try:
        log_to_file(f"运行对话: {conversation_id}")
        
        if conversation_id not in conversations:
            return jsonify({"error": "对话不存在"}), 404
        
        conversation = conversations[conversation_id]
        
        # 检查是否应该继续对话
        if not router.should_continue_conversation(
            conversation["context"],
            conversation["needed_info"],
            conversation["round_num"]
        ):
            # 生成最终报告
            log_to_file("生成最终报告...")
            report = run_role("writer", conversation["context"], conversation["needed_info"])
            conversation["status"] = "completed"
            conversation["report"] = report
            
            # 保存对话记录
            save_conversation_log(conversation_id, conversation)
            
            log_to_file("对话完成，报告已生成")
            
            return jsonify({
                "success": True,
                "status": "completed",
                "messages": conversation["context"],
                "report": report
            })
        
        # 运行下一轮对话
        conversation["round_num"] += 1
        result = run_conversation_round(
            conversation_id,
            conversation["context"],
            conversation["needed_info"],
            conversation["round_num"]
        )
        
        # 更新对话状态
        conversation["context"] = result["messages"]
        conversation["needed_info"] = result.get("needed_info", [])
        
        if result["status"] == "error":
            conversation["status"] = "error"
            log_to_file(f"对话出错: {result.get('error', '未知错误')}", "ERROR")
            return jsonify({
                "success": False,
                "status": "error",
                "error": result.get("error", "未知错误"),
                "messages": conversation["context"]
            })
        
        log_to_file(f"第{conversation['round_num']}轮对话完成")
        
        return jsonify({
            "success": True,
            "status": "continuing",
            "messages": conversation["context"],
            "round_num": conversation["round_num"]
        })
        
    except Exception as e:
        log_to_file(f"运行对话失败: {e}", "ERROR")
        log_to_file(traceback.format_exc(), "ERROR")
        return jsonify({"error": str(e)}), 500

@app.route('/api/conversation/<conversation_id>/status', methods=['GET'])
def get_conversation_status(conversation_id):
    """获取对话状态"""
    try:
        if conversation_id not in conversations:
            return jsonify({"error": "对话不存在"}), 404
        
        conversation = conversations[conversation_id]
        
        return jsonify({
            "conversationId": conversation_id,
            "status": conversation["status"],
            "roundNum": conversation["round_num"],
            "messageCount": len(conversation["context"])
        })
        
    except Exception as e:
        log_to_file(f"获取对话状态失败: {e}", "ERROR")
        return jsonify({"error": str(e)}), 500

@app.route('/api/conversation/<conversation_id>/report', methods=['GET'])
def get_conversation_report(conversation_id):
    """获取对话报告"""
    try:
        if conversation_id not in conversations:
            return jsonify({"error": "对话不存在"}), 404
        
        conversation = conversations[conversation_id]
        
        if conversation["status"] != "completed":
            return jsonify({"error": "对话尚未完成"}), 400
        
        return jsonify({
            "conversationId": conversation_id,
            "report": conversation.get("report", "")
        })
        
    except Exception as e:
        log_to_file(f"获取对话报告失败: {e}", "ERROR")
        return jsonify({"error": str(e)}), 500

def run_role(role_key: str, context: List[Dict[str, Any]], needed_info: List[str], 
             extra_payload: Dict[str, Any] = None) -> Dict[str, Any]:
    """运行角色"""
    try:
        # 获取bot配置
        system_prompt = bot_manager.get_bot_system_prompt(role_key)
        bot_name = bot_manager.get_bot_name(role_key)
        
        # 获取bot的上下文（应用隔离规则）
        bot_context = bot_manager.filter_context_for_bot(role_key, context)
        
        # 构建payload
        payload = {
            "FAMILY_INTRO": conversations.get("current_form_data", {}).get("FAMILY_INTRO", ""),
            "TARGET_SCHOOLS": conversations.get("current_form_data", {}).get("TARGET_SCHOOLS", ""),
            "SCHOOL_DATA": school_data,
            "CONTEXT_WINDOW": router.summarize_context(bot_context),
            "NEEDED_INFO": needed_info,
            "ROUND": len(context) + 1,
            "MAX_CONTENT_LENGTH": config.get("globals", {}).get("max_content_length", 300),
            "RESPONSE_TIMEOUT": config.get("globals", {}).get("response_timeout", 30)
        }
        
        if extra_payload:
            payload.update(extra_payload)
        
        # 调用AI
        log_to_file(f"调用AI角色: {role_key}")
        out = ai_interface.call_llm(bot_name, system_prompt, payload)
        
        return out
        
    except Exception as e:
        log_to_file(f"运行角色失败: {e}", "ERROR")
        log_to_file(traceback.format_exc(), "ERROR")
        raise

if __name__ == '__main__':
    initialize_backend()
    log_to_file("启动Flask服务器...")
    app.run(host='0.0.0.0', port=5000, debug=True)
