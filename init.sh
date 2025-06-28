#!/bin/bash

# 家族知识管理系统初始化脚本
# 使用方法: chmod +x init_project.sh && ./init_project.sh

set -e

PROJECT_NAME="family_knowledge"
DJANGO_PROJECT_NAME="config"
VENV_NAME="family_venv"

echo "🚀 开始初始化家族知识管理系统..."

# 1. 创建虚拟环境
echo "📦 创建Python虚拟环境..."
python3 -m venv $VENV_NAME
source $VENV_NAME/bin/activate

# 2. 升级pip
echo "⬆️ 升级pip..."
pip install --upgrade pip

# 3. 创建项目目录结构
echo "📁 创建项目目录结构..."
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME

# 4. 创建requirements.txt
echo "📝 创建requirements.txt..."
cat > requirements.txt << EOF
# Django 家族知识管理系统依赖包 - MVP 版本（KISS 原则）

# === 核心必需包 ===
Django>=5.2.3,<6.0  # Django LTS 版本
psycopg2-binary>=2.9.10  # PostgreSQL 数据库连接
python-decouple>=3.8  # 环境变量管理
Pillow>=11.2.1  # 图像文件处理（照片上传需要）

# === 部署必需包 ===
gunicorn>=23.0.0  # 生产环境 WSGI 服务器
whitenoise>=6.9.0  # 静态文件服务

# === 开发便利包 ===
django-extensions>=3.2.3  # 开发工具（shell_plus 等）

# ================================
# 第二阶段再添加的包（AI功能）：
# ================================
# langchain>=0.3.26
# langchain-anthropic>=0.3.16
# langchain-postgres>=0.0.6
# anthropic>=0.25.0

# ================================
# 第三阶段可选的包（性能优化）：
# ================================
# django-redis>=5.4.0  # Redis 缓存（当有性能需求时）
# python-dotenv>=1.0.1  # 如果不用 python-decouple
EOF

# 5. 安装依赖
echo "📦 安装Python依赖包..."
pip install -r requirements.txt

# 6. 创建Django项目
echo "🌐 创建Django项目..."
django-admin startproject $DJANGO_PROJECT_NAME .

# 7. 创建核心应用
echo "📱 创建Django应用..."
python manage.py startapp core
python manage.py startapp ai_integration

# 8. 创建基础目录结构
echo "📂 创建目录结构..."
mkdir -p static/css static/js static/images
mkdir -p templates/admin templates/core
mkdir -p media/uploads
mkdir -p logs

# 9. 创建.env模板文件
echo "🔧 创建环境变量模板..."
cat > .env.example << EOF
# Django设置
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库设置
DATABASE_URL=postgresql://username:password@localhost:5432/family
