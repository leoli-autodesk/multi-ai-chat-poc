#!/bin/bash
# 私校申请顾问AI协作系统 - 启动脚本

echo "🎯 私校申请顾问AI协作系统"
echo "================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 需要Python 3.7+"
    exit 1
fi

# 检查必要文件
if [ ! -f "src/main.py" ]; then
    echo "❌ 错误: 找不到主程序文件"
    exit 1
fi

# 创建必要目录
mkdir -p output config/bots config/schools config/templates tests

echo "✅ 环境检查完成"
echo ""
echo "使用方法:"
echo "  ./scripts/run.sh <输入文件路径>"
echo "  ./scripts/run.sh <输入文件路径> -o <输出目录>"
echo ""
echo "示例:"
echo "  ./scripts/run.sh input.txt"
echo "  ./scripts/run.sh input.txt -o output/my_result"
echo ""

# 检查是否有输入文件参数
if [ $# -eq 0 ]; then
    echo "❌ 错误: 请提供输入文件路径"
    echo ""
    echo "使用方法:"
    echo "  ./scripts/run.sh <输入文件路径>"
    echo "  ./scripts/run.sh <输入文件路径> -o <输出目录>"
    exit 1
fi

echo "🚀 启动处理程序..."
echo "📁 输入文件: $1"
echo ""

# 启动Python程序
python3 src/main.py "$@"
