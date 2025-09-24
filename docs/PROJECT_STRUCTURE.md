# 项目结构说明

## 目录结构

```
multi-ai-chat-poc/
├── src/                    # 源代码目录
│   ├── backend/           # 后端服务代码
│   ├── frontend/          # 前端界面代码
│   ├── ai/                # AI相关模块
│   ├── utils/             # 工具函数
│   └── main.py            # 主程序入口
├── config/                # 配置文件目录
│   ├── bots/              # Bot配置文件
│   ├── schools/           # 学校数据文件
│   └── templates/         # 模板文件
├── docs/                  # 文档目录
├── scripts/               # 脚本文件目录
│   └── run.sh            # 一键启动脚本
├── tests/                 # 测试结果目录（保留最近3次）
├── output/                # 输出结果目录
├── README.md              # 项目说明
└── PROJ_PLAN.md          # 项目规划文档
```

## 目录说明

### src/ - 源代码
- **backend/**: Flask后端服务代码
- **frontend/**: React前端界面代码
- **ai/**: AI角色管理和对话逻辑
- **utils/**: 通用工具函数
- **main.py**: 程序主入口

### config/ - 配置文件
- **bots/**: 各AI角色的配置文件（YAML格式）
- **schools/**: 目标学校的数据文件
- **templates/**: 输入模板和报告模板

### scripts/ - 脚本文件
- **run.sh**: 一键启动脚本，自动检查环境并启动服务

### tests/ - 测试结果
- 自动保留最近的3次测试结果
- 每次测试包含：input.txt, chat.txt, report.txt, summary.txt

### output/ - 输出结果
- 按时间戳创建子目录
- 包含完整的处理结果

## 文件命名规范

### 测试结果目录
- 格式：`YYYYMMDD_HHMMSS`
- 示例：`20250923_195638`

### 配置文件
- Bot配置：`<role_name>.yaml`
- 学校数据：`schools.yaml`
- 模板文件：`<template_name>.md`

### 输出文件
- 输入文件：`input.txt`
- 对话记录：`chat.txt`
- 最终报告：`report.txt`
- 处理总结：`summary.txt`

## 清理策略

### 测试数据清理
- 自动保留最新的3次测试结果
- 更早的测试数据会被自动清理
- 确保磁盘空间不会无限增长

### 输出数据管理
- 输出结果按时间戳组织
- 支持手动清理旧数据
- 重要结果可手动备份

## 部署说明

### 环境要求
- Python 3.7+
- 现代浏览器（Chrome/Firefox/Safari）
- 无需Docker或其他容器技术

### 启动方式
```bash
# 方式1：使用启动脚本
./scripts/run.sh

# 方式2：直接运行Python
python3 src/main.py
```

### 访问地址
- Web界面：http://localhost:5000
- 默认端口：5000（可在配置中修改）