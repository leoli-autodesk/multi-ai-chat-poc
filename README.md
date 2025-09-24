# 私校申请顾问AI协作系统

## 项目概述
为私校申请顾问提供专业的多AI协作工具，通过模拟招生官、家长、学生、顾问等多角色对话，生成高质量的申请策略报告。

## 项目结构
```
multi-ai-chat-poc/
├── src/                    # 源代码
│   ├── backend/           # 后端服务
│   ├── frontend/          # 前端界面
│   ├── ai/                # AI相关模块
│   └── utils/             # 工具函数
├── config/                # 配置文件
│   ├── bots/              # Bot配置
│   ├── schools/           # 学校数据
│   └── templates/         # 模板文件
├── docs/                  # 文档
├── scripts/               # 脚本文件
├── tests/                 # 测试结果（保留最近3次）
├── output/                # 输出结果
└── README.md              # 项目说明
```

## 快速开始
1. 运行 `./scripts/run.sh` 启动Web界面
2. 上传输入文件
3. 系统自动处理并生成报告
4. 结果保存在 `output/<timestamp>/` 目录

## 技术栈
- **后端**: Python Flask
- **前端**: React + TypeScript
- **AI**: Cursor内置AI
- **部署**: 简化部署，无需Docker

## 开发状态
- ✅ 核心对话系统完成
- ✅ 多角色协作机制完成
- 🔄 Web界面开发中
- ⏳ 简化部署准备中