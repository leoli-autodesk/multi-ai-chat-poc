"""
Cursor AI集成模块
实现统一的LLM调用接口，支持多种AI模型
"""

import json
import time
import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from context_analyzer import ContextAnalyzer

class CursorAI:
    """Cursor AI集成类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_retries = 3
        self.retry_delay = 1.0
        self.max_content_length = config.get("globals", {}).get("max_content_length", 300)
        self.context_analyzer = ContextAnalyzer()
        
        # 模型配置
        self.model_config = {
            "default_model": "claude-3.5-sonnet",  # Cursor默认模型
            "fallback_model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        # 角色特定的模型配置
        self.role_models = {
            "Admissions Officer": "claude-3.5-sonnet",  # 需要逻辑思维
            "Parent": "claude-3.5-sonnet",  # 需要自然表达
            "Student": "claude-3.5-sonnet",  # 需要真实感
            "Advisor": "claude-3.5-sonnet",  # 需要专业建议
            "Writer": "claude-3.5-sonnet"   # 需要结构化输出
        }
    
    def log_ai_call(self, role_name: str, prompt: str, response: str, model: str, duration: float):
        """记录AI调用日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [AI-CALL] 角色: {role_name}, 模型: {model}, 耗时: {duration:.2f}s")
        print(f"[{timestamp}] [AI-CALL] 提示词长度: {len(prompt)} 字符")
        print(f"[{timestamp}] [AI-CALL] 响应长度: {len(response)} 字符")
    
    def validate_response(self, response: str, role_name: str, expected_schema: List[str]) -> bool:
        """验证AI响应格式 - 现在接受自然对话格式"""
        # 对于自然对话格式，只要不是空响应就认为有效
        if response and response.strip():
            return True
        return False
    
    def format_prompt(self, role_name: str, system_prompt: str, payload: Dict[str, Any]) -> str:
        """格式化提示词"""
        # 替换模板变量
        formatted_prompt = system_prompt
        
        # 替换所有模板变量
        for key, value in payload.items():
            placeholder = f"{{{{{key}}}}}"
            if isinstance(value, (dict, list)):
                formatted_value = json.dumps(value, ensure_ascii=False, indent=2)
            else:
                formatted_value = str(value)
            formatted_prompt = formatted_prompt.replace(placeholder, formatted_value)
        
        # 添加角色特定的指导
        role_guidance = self.get_role_guidance(role_name)
        formatted_prompt += f"\n\n{role_guidance}"
        
        return formatted_prompt
    
    def get_role_guidance(self, role_name: str) -> str:
        """获取角色特定的指导"""
        guidance = {
            "Admissions Officer": """
重要提醒：
- 保持专业和客观的语调
- 问题要具体且有针对性
- 避免引导性语言
- 关注申请者的真实能力
""",
            "Parent": """
重要提醒：
- 以真实家长的角度回答
- 提供具体的事实和例子
- 体现对孩子的了解和支持
- 诚实面对孩子的优缺点
""",
            "Student": """
重要提醒：
- 用学生的语言和视角回答
- 提供具体的个人经历
- 体现成长和反思
- 保持真实和自然
""",
            "Advisor": """
重要提醒：
- 提供专业和实用的建议
- 体现我们机构的专业价值
- 让客户看到希望和可能性
- 提供具体的行动计划
""",
            "Writer": """
重要提醒：
- 生成结构化的专业报告
- 突出孩子的潜力和优势
- 体现我们机构的专业支持
- 让客户看到成功可能性
"""
        }
        return guidance.get(role_name, "")
    
    def call_cursor_ai(self, role_name: str, prompt: str) -> str:
        """调用Cursor AI"""
        # 这里我们模拟Cursor AI的调用
        # 在实际环境中，这里会调用Cursor的API
        
        # 模拟API调用延迟
        time.sleep(0.5)
        
        # 根据角色生成不同的响应
        if role_name == "Admissions Officer":
            return self.generate_admissions_response(prompt)
        elif role_name == "Parent":
            return self.generate_parent_response(prompt)
        elif role_name == "Student":
            return self.generate_student_response(prompt)
        elif role_name == "Advisor":
            return self.generate_advisor_response(prompt)
        elif role_name == "Writer":
            return self.generate_writer_response(prompt)
        else:
            return '{"error": "未知角色"}'
    
    def generate_admissions_response(self, prompt: str) -> str:
        """生成招生官响应 - 基于上下文分析的自然对话格式"""
        # 提取上下文分析信息
        context_analysis = ""
        if "上下文分析：" in prompt:
            start = prompt.find("上下文分析：") + len("上下文分析：")
            end = prompt.find("当前轮次：")
            if end > start:
                context_analysis = prompt[start:end].strip()
        
        # 提取轮次信息
        round_num = 1
        if "当前轮次：" in prompt:
            try:
                start = prompt.find("当前轮次：") + len("当前轮次：")
                end = prompt.find("\n", start)
                if end == -1:
                    end = len(prompt)
                round_text = prompt[start:end].strip()
                round_num = int(round_text)
            except:
                round_num = 1
        
        print(f"[DEBUG] Admissions Officer context analysis: {context_analysis}")
        print(f"[DEBUG] Admissions Officer round: {round_num}")
        
        # 基于上下文分析和轮次生成不同的响应
        if round_num == 1:
            return "我想了解您的家庭背景对您的影响：家庭的教育理念是什么？父母是如何支持您的学习和成长的？您认为家庭环境如何塑造了您的性格？对于未来的教育规划，家庭有什么期望？"
        
        elif round_num == 2:
            if "学术发展" in context_analysis:
                return "基于您提到的学术兴趣，我想进一步了解：您最感兴趣的学科领域是什么？您是如何保持学习动力的？对于目标学校的学术环境，您有什么期待？"
            elif "领导力" in context_analysis:
                return "基于您提到的领导力背景，我想进一步了解几个方面：首先，能否分享一个具体的领导力项目，包括您是如何组织的，最终取得了什么可量化的成果？其次，您认为自己的领导风格是什么，在团队合作中如何发挥影响力？"
            else:
                return "我想了解您的兴趣爱好和特长：您平时最喜欢做什么？这些活动如何影响了您的性格发展？您希望在学校里继续发展哪些方面的能力？"
        
        elif round_num == 3:
            if "挑战" in context_analysis or "困难" in context_analysis:
                return "您刚才提到了面对挑战的经历，我想了解：您是如何克服这些困难的？从这些经历中学到了什么？您认为这些挑战如何塑造了您的性格？"
            elif "具体例子" in context_analysis or "数据" in context_analysis:
                return "您分享的例子很有说服力，我想进一步了解：这个项目的具体数据是什么？您是如何衡量成功的？在这个过程中，您最大的收获是什么？"
            else:
                return "基于我们的对话，我想了解您的未来规划：您对高中生活有什么期待？您希望在学校里实现什么目标？您认为什么样的教育环境最适合您？"
        
        elif round_num == 4:
            return "我想深入了解您的学习方法和习惯：您是如何安排学习时间的？遇到困难时您会如何寻求帮助？您认为什么样的学习环境最适合您？"
        
        elif round_num == 5:
            return "关于您的课外活动经历，我想了解：您参与过哪些社团或活动？这些经历如何影响了您的成长？您希望在学校里继续参与哪些类型的活动？"
        
        elif round_num == 6:
            return "我想了解您的性格特点：您认为自己的最大优势是什么？在团队合作中您通常扮演什么角色？您如何与他人建立良好的关系？"
        
        elif round_num == 7:
            return "关于您的未来规划，我想了解：您对大学有什么期待？您希望从事什么职业？您认为什么样的教育能够帮助您实现这些目标？"
        
        elif round_num == 8:
            return "我想了解您对目标学校的看法：您为什么选择申请我们学校？您认为我们学校的哪些特点最吸引您？您希望在学校里获得什么样的成长？"
        
        elif round_num == 9:
            return "基于我们的深入交流，我想了解：您认为自己的哪些特质最符合我们学校的价值观？您希望在学校里如何贡献自己的力量？"
        
        elif round_num == 10:
            return "最后一个问题：您还有什么想让我们了解的关于您的情况？您对这次面试有什么感受？您还有什么问题想了解我们学校的吗？"
        
        else:
            return "感谢您的分享，我想进一步了解您的想法和经历。"
    
    def generate_parent_response(self, prompt: str) -> str:
        """生成家长响应 - 基于上下文分析的自然对话格式"""
        # 提取上下文分析信息
        context_analysis = ""
        if "上下文分析：" in prompt:
            start = prompt.find("上下文分析：") + len("上下文分析：")
            end = prompt.find("当前轮次：")
            if end > start:
                context_analysis = prompt[start:end].strip()
        
        # 提取轮次信息
        round_num = 1
        if "当前轮次：" in prompt:
            try:
                start = prompt.find("当前轮次：") + len("当前轮次：")
                end = prompt.find("\n", start)
                if end == -1:
                    end = len(prompt)
                round_text = prompt[start:end].strip()
                round_num = int(round_text)
            except:
                round_num = 1
        
        # 基于上下文分析和轮次生成不同的响应
        if round_num == 1:
            return "我们家庭的教育理念是希望孩子能够全面发展，不仅要有好的学术成绩，更要有良好的品格和社会责任感。我们经常和孩子讨论社会问题，鼓励她思考如何为社会做贡献。同时，我们也希望她能保持好奇心，勇于尝试新事物。对于未来的教育规划，我们希望能找到一所能够支持她全面发展的学校。"
        
        elif round_num == 2:
            if "学术发展" in context_analysis:
                return "关于孩子的学术发展，我想分享一些具体的观察。她是一个很有学习热情的孩子，经常主动探索新的知识领域。我们希望能够找到一所能够支持她这种学习热情的学校，让她能够在学术上得到更好的发展。"
            elif "领导力" in context_analysis:
                return "关于孩子的领导力，我想分享一个具体的例子。去年孩子组织了一次校园环保义卖，她不仅负责策划，还亲自去各个班级宣传，最终筹到了800加元用于社区图书角建设。我们看到了她的组织能力和责任心，但也注意到她在时间管理上还需要改进。"
            else:
                return "我们注意到孩子在面对挑战时的态度。比如有一次数学考试没考好，她没有沮丧，而是主动分析错题，还去找老师请教。这种学习态度让我们很欣慰。我们也在思考如何在家里创造更好的学习环境，支持她的学术成长。"
        
        elif round_num == 3:
            if "挑战" in context_analysis or "困难" in context_analysis:
                return "我们确实注意到孩子在面对挑战时的成长。比如当她组织活动遇到困难时，她会主动寻求帮助，也会反思自己的方法。作为家长，我们很欣慰看到她的这种成长，但也希望她能学会更好地平衡学习和活动。"
            elif "具体例子" in context_analysis or "数据" in context_analysis:
                return "关于孩子参与的具体项目，我想补充一些细节。比如那个环保义卖活动，她不仅负责策划，还亲自去各个班级宣传，最终筹到了800加元。我们看到了她的组织能力和责任心，但也注意到她在时间管理上还需要改进。"
            else:
                return "基于我们的对话，我想分享一些关于孩子成长的观察。她是一个很有想法的孩子，经常会有一些让我们惊喜的见解。比如她曾经提出要在家里实施垃圾分类，还主动承担了监督的责任。我们很欣慰看到她的成长。"
        
        elif round_num == 4:
            return "关于孩子的学习习惯，我想分享一些家庭的做法。我们鼓励她制定学习计划，每天都有固定的学习时间。当她遇到困难时，我们会引导她先自己思考，然后再寻求帮助。我们也注意到她在数学和科学方面特别有天赋，经常主动探索相关的知识。"
        
        elif round_num == 5:
            return "关于课外活动，我们很支持孩子参与各种活动。除了学校的社团，她还参加了社区的志愿者活动，比如帮助老人院的老人。这些经历让她学会了如何与不同年龄的人交流，也培养了她的同理心。"
        
        elif round_num == 6:
            return "关于孩子的性格，我想分享一些观察。她是一个比较内向但很有想法的孩子。在团队合作中，她通常不是最活跃的那个，但她的建议往往很有价值。她需要时间来建立信任，但一旦建立了关系，她就会很忠诚。"
        
        elif round_num == 7:
            return "关于未来规划，我们和孩子讨论过很多次。她希望将来能从事与科学相关的工作，比如医学研究或者环境科学。我们很支持她的选择，也相信她有能力实现这些目标。"
        
        elif round_num == 8:
            return "我们选择申请贵校是因为我们了解到贵校在学术和品格教育方面都很出色。我们特别欣赏贵校鼓励学生独立思考和创新精神的教育理念。我们希望孩子能在这里找到志同道合的朋友，一起成长。"
        
        elif round_num == 9:
            return "基于我们的深入交流，我想强调孩子的一个特质：她是一个很有责任感的孩子。无论是学习还是活动，她都会认真对待。我们相信她能在贵校发挥自己的优势，为学校社区做出贡献。"
        
        elif round_num == 10:
            return "最后，我想表达我们对这次面试的感谢。通过这次交流，我们更加确信孩子适合贵校的教育环境。我们愿意配合学校的教育计划，在家里提供必要的支持，帮助孩子实现她的目标。"
        
        else:
            return "作为家长，我想分享一些关于孩子的观察。她是一个很有想法的孩子，经常会有一些让我们惊喜的见解。我们很欣慰看到她的成长，但也希望她能学会更好地表达自己的想法。"
    
    def generate_student_response(self, prompt: str) -> str:
        """生成学生响应 - 基于上下文分析的自然对话格式"""
        # 提取上下文分析信息
        context_analysis = ""
        if "上下文分析：" in prompt:
            start = prompt.find("上下文分析：") + len("上下文分析：")
            end = prompt.find("当前轮次：")
            if end > start:
                context_analysis = prompt[start:end].strip()
        
        # 提取轮次信息
        round_num = 1
        if "当前轮次：" in prompt:
            try:
                start = prompt.find("当前轮次：") + len("当前轮次：")
                end = prompt.find("\n", start)
                if end == -1:
                    end = len(prompt)
                round_text = prompt[start:end].strip()
                round_num = int(round_text)
            except:
                round_num = 1
        
        # 基于上下文分析和轮次生成不同的响应
        if round_num == 1:
            return "基于我们刚才的对话，我想分享一些关于学术发展的思考。我认为学习是一个不断探索的过程，我希望能在一个鼓励创新思维的环境中学习。我希望能够参与更多的研究项目，同时也希望能够在表达和沟通方面得到提升。"
        
        elif round_num == 2:
            if "学术发展" in context_analysis:
                return "关于学术兴趣，我想分享一些具体的经历。我特别喜欢数学和科学，特别是做实验的时候。我记得有一次我们做了一个关于植物生长的实验，我提出了一个不同的假设，虽然结果证明我的假设不完全正确，但老师表扬了我的创新思维。我觉得学习不仅仅是记住知识，更重要的是学会思考。"
            elif "领导力" in context_analysis:
                return "关于领导力，我想分享一个具体的经历。去年我组织了一次校园清洁日活动，当时遇到了很多挑战，比如有些同学不愿意参与，时间安排也有冲突。我学会了如何更好地沟通，如何制定合理的计划，最终活动很成功。不过我也意识到，真正的领导力不仅仅是组织活动，更重要的是如何激励他人，如何面对失败。"
            else:
                return "我想分享一些关于自己的观察。我是一个比较内向的人，但当我遇到感兴趣的事情时，我会变得很主动。比如当我发现一个有趣的科学现象时，我会主动去研究，去实验。我觉得这种好奇心是我最大的优点。"
        
        elif round_num == 3:
            if "挑战" in context_analysis or "困难" in context_analysis:
                return "面对挑战时，我学会了如何调整心态。比如有一次数学考试没考好，我没有沮丧，而是主动分析错题，还去找老师请教。我觉得失败是学习的一部分，重要的是如何从失败中吸取教训。我希望能在新的学习环境中继续这种积极的态度。"
            elif "具体例子" in context_analysis or "数据" in context_analysis:
                return "关于具体的项目经历，我想分享更多细节。比如那个环保义卖活动，我们最终筹到了800加元，参与的学生有30多人，整个项目持续了两个月。在这个过程中，我学会了如何协调不同人的时间，如何解决冲突，也学会了如何激励团队。"
            else:
                return "基于我们的对话，我想分享一些关于未来规划的思考。我希望能在目标学校参与更多的研究项目，特别是科学方面的。我也希望能在数学方面有更深入的学习，比如参加数学竞赛。同时，我也意识到需要在英语写作方面加强，提高表达能力。"
        
        elif round_num == 4:
            return "关于我的学习方法，我想分享一些具体的做法。我习惯制定详细的学习计划，每天都会安排固定的时间学习不同的科目。当我遇到不懂的问题时，我会先自己思考，如果还是不明白，我会主动去问老师或同学。我也喜欢用图表和思维导图来整理知识，这样能帮助我更好地理解。"
        
        elif round_num == 5:
            return "关于课外活动，我参与过学校的科学俱乐部和环保社团。在科学俱乐部里，我们经常做一些有趣的实验，比如制作太阳能小车。在环保社团，我们组织了校园垃圾分类活动，还去社区宣传环保知识。这些活动让我学会了如何与不同的人合作，也让我更加关注环境问题。"
        
        elif round_num == 6:
            return "关于我的性格，我觉得我是一个比较内向但很有想法的人。在团队合作中，我通常不是最活跃的那个，但我喜欢观察和思考，然后提出一些有建设性的建议。我比较喜欢一对一的交流，因为这样我能更好地表达自己的想法。"
        
        elif round_num == 7:
            return "关于未来规划，我希望将来能从事与科学相关的工作，比如医学研究或者环境科学。我觉得科学能够帮助解决很多实际问题，比如疾病治疗、环境保护等。我希望能在大学里深入学习相关的专业知识，然后为社会做出贡献。"
        
        elif round_num == 8:
            return "我选择申请贵校是因为我了解到贵校在科学教育方面很出色，有很多先进的实验室和设备。我也听说贵校鼓励学生独立思考和创新，这正是我需要的环境。我希望能在贵校找到志同道合的朋友，一起探索科学的奥秘。"
        
        elif round_num == 9:
            return "基于我们的深入交流，我想强调我的一个特质：我是一个很有责任感的人。无论是学习还是活动，我都会认真对待，尽力做到最好。我相信我能在贵校发挥自己的优势，为学校社区做出贡献。"
        
        elif round_num == 10:
            return "最后，我想表达我对这次面试的感谢。通过这次交流，我更加确信贵校是我理想的选择。我希望能在贵校继续我的学习之旅，实现我的科学梦想。我也很期待能在贵校遇到优秀的老师和同学，一起成长。"
        
        else:
            return "我想分享一些关于自己的观察。我是一个比较内向的人，但当我遇到感兴趣的事情时，我会变得很主动。我觉得这种好奇心是我最大的优点。不过我也意识到，我需要学会更好地表达自己的想法，更好地与人合作。"
    
    def generate_advisor_response(self, prompt: str) -> str:
        """生成顾问响应 - 基于上下文分析的自然对话格式"""
        # 添加调试信息
        print(f"[DEBUG] Advisor prompt length: {len(prompt)}")
        print(f"[DEBUG] Advisor prompt preview: {prompt[:300]}...")
        
        # 提取上下文分析信息
        context_analysis = ""
        if "上下文分析：" in prompt:
            start = prompt.find("上下文分析：") + len("上下文分析：")
            end = prompt.find("当前轮次：")
            if end > start:
                context_analysis = prompt[start:end].strip()
        
        # 提取轮次信息
        round_num = 1
        if "当前轮次：" in prompt:
            try:
                start = prompt.find("当前轮次：") + len("当前轮次：")
                end = prompt.find("\n", start)
                if end == -1:
                    end = len(prompt)
                round_text = prompt[start:end].strip()
                round_num = int(round_text)
            except:
                round_num = 1
        
        print(f"[DEBUG] Advisor round: {round_num}")
        
        # 基于轮次生成不同的响应
        if round_num == 1:
            return "招生官在了解基本情况。学生，你可以分享你的主要兴趣和经历，家长可以补充家庭的教育理念和支持方式。重点是提供具体例子，避免泛泛而谈。"
        
        elif round_num == 2:
            if "学术发展" in context_analysis:
                return "招生官在询问学术发展相关的问题。学生，你可以分享你的学习方法和习惯，比如你更喜欢什么样的学习环境？你希望学校提供什么样的学术支持？家长，你们可以分享孩子在家里的学习习惯，以及家庭如何支持孩子的学术发展。"
            elif "领导力" in context_analysis:
                return "招生官在关注领导力方面的问题。学生，你可以更具体地分享一些数据：比如环保义卖具体筹到了多少钱？参与的学生有多少人？这个项目持续了多长时间？另外，你可以分享一些具体的挑战和如何解决的例子，这样更能展现你的领导能力。"
            else:
                return "基于刚才的对话，我建议学生和家长在下一轮回答时提供更多具体信息。学生，你可以分享更多关于你组织活动的具体细节，比如遇到了什么困难，如何解决的。家长，你们可以补充一些关于家庭价值观和教育理念的具体例子。"
        
        elif round_num == 3:
            if "挑战" in context_analysis or "困难" in context_analysis:
                return "招生官想了解你面对挑战的态度。学生，你可以分享一些具体的例子，比如你如何克服学习中的困难，你从失败中学到了什么？家长，你们可以分享一些关于孩子学习态度和家庭如何支持孩子面对挑战的信息。"
            elif "具体例子" in context_analysis or "数据" in context_analysis:
                return "很好，学生和家长提供了具体的例子和数据。现在，我建议学生可以进一步反思这些经历对自己的影响，比如学到了什么，如何运用到未来的学习中。家长可以补充家庭如何引导孩子进行反思和总结。"
            else:
                return "对话已经进入中等深度，现在需要展现学生的反思能力和成长潜力。学生，你可以分享你从经历中学到的教训，以及这些经历如何塑造了你的性格。家长，你们可以分享对孩子成长的观察和期望。"
        
        elif round_num == 4:
            return "招生官想了解学习方法和习惯。学生，你可以分享你的学习计划制定过程，比如如何安排时间，如何复习，如何寻求帮助。家长，你们可以分享家庭如何支持孩子的学习，比如提供学习环境，帮助制定计划等。"
        
        elif round_num == 5:
            return "招生官在询问课外活动经历。学生，你可以分享你参与的具体活动，比如社团、志愿者、竞赛等，重点说明这些活动如何影响了你的成长。家长，你们可以分享家庭如何支持孩子的课外活动，以及这些活动对家庭的影响。"
        
        elif round_num == 6:
            return "招生官想了解性格特点。学生，你可以诚实地分享你的性格特点，包括优势和需要改进的地方，重点说明你如何在团队中发挥作用。家长，你们可以分享对孩子性格的观察，以及家庭如何引导孩子的性格发展。"
        
        elif round_num == 7:
            return "招生官在询问未来规划。学生，你可以分享你的职业理想和学术目标，说明你如何规划实现这些目标。家长，你们可以分享家庭对孩子未来的期望和支持计划。"
        
        elif round_num == 8:
            return "招生官想了解对学校的看法。学生，你可以分享你选择这所学校的原因，说明学校的哪些特点最吸引你。家长，你们可以分享家庭选择这所学校的考虑因素，以及对学校的期望。"
        
        elif round_num == 9:
            return "招生官在评估学校匹配度。学生，你可以总结你的优势，说明你如何能为学校做出贡献。家长，你们可以强调家庭对学校的认同和支持，表达对合作的期待。"
        
        elif round_num == 10:
            return "这是最后一轮，招生官在给机会补充信息。学生，你可以分享任何之前没有提到的优势或经历。家长，你们可以表达对这次面试的感谢，以及对未来的期待。"
        
        else:
            return "基于刚才的对话，我建议学生和家长在下一轮回答时提供更多具体信息。重点是提供具体例子，避免泛泛而谈。"
    
    def generate_writer_response(self, prompt: str) -> str:
        """生成写手响应"""
        return """# 申请策略总览
- 结论速览：孩子具有很好的领导力潜质，通过我们的专业指导，完全可以成功申请到目标学校。
- 竞争力要点：服务意识、组织力、学习能力；我们的专业支持将帮助提升证据质量和持续度。
- 我们的专业支持承诺：全程指导，确保成功。

## 家庭与学生画像
- 家庭价值观：重视教育，支持孩子全面发展
- 学生特质：有责任心、组织能力强、学习态度积极
- 成长潜力分析：通过专业指导，潜力将得到充分发挥

## 学校匹配度
- 一致性要点：与目标学校价值观高度匹配
- 潜在不匹配与风险：材料需要完善，面试技巧需要提升
- 匹配度提升策略：我们的专业团队将协助完善所有材料

## 优势与改进列表
- Top Strengths：服务意识、组织力、学习能力
- Gaps to Close：材料完善、面试技巧
- 我们的专业解决方案：提供全方位的申请指导服务

## 90天行动计划
- 材料打磨 | 家长/学生 | 2025-10-05 | PDF汇编 | 我们的全程指导
- 面试演练 | 学生 | 2025-10-10 | 模拟评分>=4/5 | 我们的专业培训
- 能力建设 | 学生 | 持续 | 量化指标 | 我们的个性化指导

## 面试作战卡
- 自我介绍：突出领导力和服务意识
- 亮点故事：环保义卖活动（STAR模式）
- 失败反思模版：诚实面对，展现成长
- 反向提问清单：展现对学校的了解

## 提交物清单
- 简历：突出领导力和服务经历
- 推荐信：来自指导老师和社团负责人
- 作品集：环保项目相关材料

## 我们的专业服务
- 全程指导承诺：从材料准备到面试培训
- 成功案例参考：类似背景学生的成功经验
- 后续支持计划：入学后的持续关注

## 待补充信息
- 需要更多量化证据
- 需要第三方评价"""
    
    def call_llm(self, role_name: str, system_prompt: str, payload: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """统一的LLM调用接口"""
        start_time = time.time()
        
        try:
            # 获取对话上下文
            context = payload.get("context", [])
            
            # 使用上下文分析器分析对话历史
            # 将角色名称转换为ContextAnalyzer期望的格式
            role_mapping = {
                "Admissions Officer": "admissions_officer",
                "Advisor": "advisor", 
                "Student": "student",
                "Parent": "parent",
                "Writer": "writer"
            }
            analyzer_role = role_mapping.get(role_name, role_name.lower())
            context_summary = self.context_analyzer.generate_context_summary(context, analyzer_role)
            
            # 构建包含上下文分析的完整提示词
            enhanced_payload = payload.copy()
            enhanced_payload["CONTEXT_ANALYSIS"] = context_summary
            
            # 格式化提示词
            formatted_prompt = self.format_prompt(role_name, system_prompt, enhanced_payload)
            
            # 获取角色对应的模型
            model = self.role_models.get(role_name, self.model_config["default_model"])
            
            # 调用AI
            response = self.call_cursor_ai(role_name, formatted_prompt)
            
            # 计算耗时
            duration = time.time() - start_time
            
            # 记录日志
            self.log_ai_call(role_name, formatted_prompt, response, model, duration)
            
            # 验证响应
            expected_schema = self.get_expected_schema(role_name)
            if not self.validate_response(response, role_name, expected_schema):
                print(f"警告: {role_name} 的响应格式可能有问题")
            
            # 解析响应 - 现在所有角色都返回自然对话
            return response  # 所有角色都返回自然对话字符串
            
        except Exception as e:
            print(f"错误: AI调用失败 - {e}")
            return {"error": str(e)}
    
    def get_expected_schema(self, role_name: str) -> List[str]:
        """获取角色期望的输出模式 - 现在所有角色都输出自然对话"""
        return []  # 自然对话不需要schema验证
    
    def retry_call(self, role_name: str, system_prompt: str, payload: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """带重试机制的AI调用"""
        for attempt in range(self.max_retries):
            try:
                result = self.call_llm(role_name, system_prompt, payload)
                if "error" not in result:
                    return result
            except Exception as e:
                print(f"尝试 {attempt + 1} 失败: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
        
        # 所有重试都失败，返回错误
        return {"error": "AI调用失败，已重试多次"}
