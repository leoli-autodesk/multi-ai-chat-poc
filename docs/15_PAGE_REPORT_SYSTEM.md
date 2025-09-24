# 🎯 15页私校申请报告生成系统

## 📋 项目概述

本项目是一个专业的私校申请策略报告生成系统，能够根据学生和家庭信息自动生成约15页的详细申请报告，包含学校匹配度分析、学术准备建议、申请策略等内容。

## ✨ 新功能特性

### 1. 15页模板系统
- **新增模板**: `config/templates/final_report.md`
- **章节结构**: 6个主要章节，约15页A4内容
- **兼容性**: 完全兼容现有 `strategy_report.md` 模板

### 2. 学校匹配度分析
- **评分系统**: 4维度评分（学术、活动、文化、性格）
- **权重配置**: 可自定义权重，默认学术35%、活动25%、文化20%、性格20%
- **智能排序**: 自动生成top3推荐学校
- **透明理由**: 每所学校提供详细的匹配理由

### 3. 长度控制系统
- **页数控制**: 自动调整内容长度至14-16页
- **章节优化**: 各章节字数限制和优化
- **排版设置**: 11pt正文字号，1.25行距，专业排版

### 4. 多格式导出
- **Markdown**: 源文件格式
- **DOCX**: Word文档格式，继承样式
- **PDF**: 专业PDF格式
- **元数据**: JSON格式的详细元数据

## 🏗️ 系统架构

```
src/
├── enhanced_report_generator.py  # 增强版报告生成器
├── match_analyzer.py             # 匹配度分析器
├── length_controller.py          # 长度控制器
└── ...

config/
├── data/
│   └── schema.json               # 数据Schema
├── templates/
│   ├── final_report.md           # 15页新模板
│   └── strategy_report.md       # 原有模板
└── schools/
    └── school_data.yaml         # 学校数据

testing-scripts/
├── test_compatibility.py        # 兼容性测试
└── test_integration.py          # 集成测试
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行测试

```bash
# 兼容性测试
python testing-scripts/test_compatibility.py

# 集成测试
python testing-scripts/test_integration.py
```

### 3. 生成报告

```python
from src.enhanced_report_generator import EnhancedReportGenerator

# 初始化生成器
generator = EnhancedReportGenerator()

# 准备数据
student_data = {
    "name": "Alex Chen",
    "age": "14岁",
    "grade": "Grade 8",
    # ... 更多数据
}

conversation_log = [
    {"role": "student", "content": "我喜欢学习"},
    {"role": "parent", "content": "我们支持孩子"}
]

# 生成报告
report_result = generator.generate_comprehensive_report(
    conversation_log, student_data
)

# 导出报告
exported_files = generator.export_report(report_result, "all")
```

## 📊 数据Schema

### 学生信息
```json
{
  "student": {
    "name": "{{student_name}}",
    "age": "{{age}}",
    "grade": "{{grade}}",
    "gpa": "{{gpa}}",
    "academic_strengths": "{{academic_strengths}}",
    "competition_achievements": "{{competition_achievements}}",
    "leadership_positions": "{{leadership_positions}}",
    "project_experiences": "{{project_experiences}}",
    "teamwork_examples": "{{teamwork_examples}}",
    "impact_metrics": "{{impact_metrics}}",
    "innovation_examples": "{{innovation_examples}}",
    "responsibility_examples": "{{responsibility_examples}}",
    "learning_ability": "{{learning_ability}}",
    "adaptability": "{{adaptability}}"
  }
}
```

### 学校匹配度
```json
{
  "target_schools": [
    {
      "name": "Upper Canada College",
      "scores": {
        "academic": 4,
        "activities": 4,
        "culture": 5,
        "personality": 4
      },
      "weights": {
        "academic": 0.35,
        "activities": 0.25,
        "culture": 0.2,
        "personality": 0.2
      },
      "match_percentage": "85%",
      "advantages": ["学术卓越", "领导力培养", "国际化程度高"],
      "strategies": ["突出学术成就", "展现领导力", "强调学术追求"],
      "rationale": "在学术能力方面表现突出，学生数学、物理专长与学校特色高度契合"
    }
  ]
}
```

## 🎨 模板结构

### 15页模板章节
1. **家庭与学生背景** (约3页)
   - 家庭教育理念与价值观
   - 学业与学习风格
   - 个性与社交
   - 兴趣与特长

2. **学校申请定位** (约2页)
   - 家长择校标准
   - 学校资源扫描

3. **学生—学校匹配度** (约4页) ⭐ **核心章节**
   - 匹配维度与权重
   - 各学校详细分析
   - 顾问推荐排序

4. **学术与课外准备** (约3页)
   - 学术补强计划
   - 语言提升路径
   - 课外活动规划
   - 义工与社区服务

5. **申请流程与个性化策略** (约2.5页)
   - 流程对比表 + 时间线
   - 测试准备
   - 推荐信与Essay策略
   - 面试辅导

6. **录取后延伸建议** (约0.5页)
   - Offer对比与选择
   - 入学前衔接与心理适应
   - 长远发展规划

## 🔧 配置选项

### 长度控制配置
```python
from src.length_controller import LengthConfig

config = LengthConfig(
    family_background=1000,      # 家庭背景字数
    school_positioning=800,      # 学校定位字数
    matching_analysis=1500,      # 匹配度分析字数
    academic_preparation=1100,   # 学术准备字数
    application_strategy=900,     # 申请策略字数
    post_admission=350,         # 录取后建议字数
    target_pages=15,            # 目标页数
    font_size=11,              # 正文字号
    line_spacing=1.25          # 行距
)
```

### 匹配度权重配置
```python
from src.match_analyzer import MatchAnalyzer

analyzer = MatchAnalyzer({
    "academic": 0.35,      # 学术权重
    "activities": 0.25,   # 活动权重
    "culture": 0.20,      # 文化权重
    "personality": 0.20   # 性格权重
})
```

## 📈 使用示例

### 基本使用
```python
# 1. 创建生成器
generator = EnhancedReportGenerator()

# 2. 准备学生数据
student_data = {
    "name": "Alex Chen",
    "age": "14岁",
    "grade": "Grade 8",
    "gpa": "3.8/4.0",
    "academic_strengths": "数学、物理、计算机科学",
    "competition_achievements": "机器人竞赛省级二等奖",
    "leadership_positions": "科技部副部长",
    "target_schools": [
        {
            "name": "Upper Canada College",
            "scores": {"academic": 4, "activities": 4, "culture": 5, "personality": 4},
            "weights": {"academic": 0.35, "activities": 0.25, "culture": 0.2, "personality": 0.2}
        }
    ]
}

# 3. 准备对话记录
conversation_log = [
    {"role": "student", "content": "我喜欢组织活动和做科学实验"},
    {"role": "parent", "content": "孩子在学生会组织过环保义卖"}
]

# 4. 生成报告
report_result = generator.generate_comprehensive_report(conversation_log, student_data)

# 5. 导出报告
exported_files = generator.export_report(report_result, "all")

print(f"报告已生成: {exported_files}")
```

### 高级配置
```python
# 自定义长度控制
from src.length_controller import LengthController, LengthConfig

config = LengthConfig(
    target_pages=16,           # 目标16页
    font_size=12,             # 12pt字号
    line_spacing=1.3          # 1.3行距
)

controller = LengthController(config)

# 自定义匹配度权重
from src.match_analyzer import MatchAnalyzer

custom_weights = {
    "academic": 0.4,      # 提高学术权重
    "activities": 0.3,   # 提高活动权重
    "culture": 0.15,     # 降低文化权重
    "personality": 0.15  # 降低性格权重
}

analyzer = MatchAnalyzer(custom_weights)
```

## 🧪 测试

### 运行所有测试
```bash
# 兼容性测试
python testing-scripts/test_compatibility.py

# 集成测试
python testing-scripts/test_integration.py
```

### 测试覆盖
- ✅ Schema兼容性测试
- ✅ 模板兼容性测试
- ✅ 匹配度逻辑测试
- ✅ 长度控制测试
- ✅ 导出功能测试
- ✅ 回归兼容性测试

## 📁 输出文件

### 文件结构
```
output/
└── 20240101_120000/           # 时间戳目录
    ├── Alex Chen_学校申请报告_20240101_120000.md      # Markdown源文件
    ├── Alex Chen_学校申请报告_20240101_120000.docx    # Word文档
    ├── Alex Chen_学校申请报告_20240101_120000.pdf     # PDF文档
    ├── Alex Chen_报告元数据_20240101_120000.json      # 元数据
    └── Alex Chen_长度分析_20240101_120000.md         # 长度分析报告
```

### 文件说明
- **Markdown**: 源文件格式，便于编辑和版本控制
- **DOCX**: Word文档格式，继承专业样式
- **PDF**: 专业PDF格式，适合打印和分享
- **JSON**: 详细元数据，包含页数、字数等统计信息
- **长度分析**: 详细的长度控制分析报告

## 🔄 兼容性

### 向后兼容
- ✅ 完全兼容现有 `strategy_report.md` 模板
- ✅ 保持所有现有占位符不变
- ✅ 现有数据格式无需修改
- ✅ 现有API接口保持不变

### 升级路径
1. **立即可用**: 新功能可立即使用，不影响现有功能
2. **渐进升级**: 可以逐步迁移到新模板
3. **并行运行**: 新旧系统可以并行运行

## 🛠️ 故障排除

### 常见问题

#### 1. 模板变量未替换
**问题**: 报告中出现 `{{variable_name}}` 占位符
**解决**: 检查数据中是否包含对应字段，或使用默认值

#### 2. 页数超出范围
**问题**: 报告页数不在14-16页范围内
**解决**: 调整长度控制配置或检查内容长度

#### 3. 匹配度计算错误
**问题**: 学校匹配度分数异常
**解决**: 检查分数范围(1-5)和权重总和(1.0)

#### 4. 导出失败
**问题**: DOCX或PDF导出失败
**解决**: 检查依赖库安装 `pip install python-docx weasyprint`

### 调试模式
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 启用详细日志
generator = EnhancedReportGenerator()
```

## 📞 支持

### 技术支持
- 查看测试报告了解系统状态
- 检查日志文件定位问题
- 运行兼容性测试验证功能

### 功能扩展
- 自定义模板: 修改 `config/templates/final_report.md`
- 添加学校: 更新 `config/schools/school_data.yaml`
- 调整权重: 修改匹配度分析器配置

## 📝 更新日志

### v2.0.0 (2024-01-01)
- ✨ 新增15页模板系统
- ✨ 新增学校匹配度分析
- ✨ 新增长度控制系统
- ✨ 新增多格式导出功能
- ✨ 完全向后兼容
- 🧪 新增完整测试套件

### v1.0.0 (2023-12-01)
- 🎉 初始版本发布
- 📄 基础报告生成功能
- 📊 简单模板系统

---

**让您的孩子看到希望，让我们的专业成就您的梦想！** 🎯
