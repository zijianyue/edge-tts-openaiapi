#!/bin/bash

# 设置虚拟环境名称
VENV_NAME="edge-tts"

# 检查虚拟环境是否存在
if [ ! -d "$VENV_NAME" ]; then
  echo "创建虚拟环境..."
  python3 -m venv $VENV_NAME
  if [ $? -ne 0 ]; then
    echo "创建虚拟环境失败。请确保已安装 Python 并添加到 PATH。"
    read -p "按任意键继续..."
    exit 1
  fi
fi

# 激活虚拟环境
source $VENV_NAME/bin/activate

# 检查并安装依赖
echo "检查依赖..."
python3 -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
  echo "安装 fastapi..."
  pip install fastapi
fi

python3 -c "import uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
  echo "安装 uvicorn..."
  pip install uvicorn
fi

python3 -c "import edge_tts" 2>/dev/null
if [ $? -ne 0 ]; then
  echo "安装 edge-tts..."
  pip install edge-tts
fi

# 运行主程序
echo "启动程序..."
python3 main.py

# 如果程序异常退出，暂停以查看错误信息
if [ $? -ne 0 ]; then
  echo "程序异常退出。"
  read -p "按任意键继续..."
fi

# 停用虚拟环境
deactivate
