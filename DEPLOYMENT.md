# Heroku 部署指南

## 🚀 一键部署说明

此项目已配置为Heroku单dyno部署，包含Django后端和React前端。

### 部署前检查清单

✅ **后端路由配置**
- `/admin/*` → Django Admin (已配置)
- `/api/*` → Django REST API (已配置)

✅ **前端路由配置** 
- `/` → 自动重定向到 `/app/`
- `/app/*` → React SPA (已配置)
- `/app/assets/*` → React静态资源 (已配置)

✅ **构建脚本配置**
- Node.js buildpack: 自动构建React前端
- Python buildpack: 安装Django依赖
- 内存优化: `--max_old_space_size=460` (适配512MB限制)

✅ **启动脚本配置**
- Gunicorn优化配置适配内存限制
- 静态文件通过WhiteNoise + Django views服务
- 数据库自动配置 (DATABASE_URL)

## 🔧 环境变量设置

在Heroku中设置以下环境变量：

```bash
SECRET_KEY=your-production-secret-key
DEBUG=False
DATABASE_URL=postgresql://... (自动设置)
ALLOWED_HOSTS=.herokuapp.com
```

## 📦 文件结构说明

```
knowledge_mgr/
├── .buildpacks          # 多buildpack配置 (Node.js + Python)
├── Procfile            # Gunicorn启动配置 (内存优化)
├── runtime.txt         # Python 3.11.10
├── package.json        # Node.js构建编排
├── requirements.txt    # Python依赖
├── config/             # Django设置和路由
├── frontend/           # React源码 (Vite + TypeScript)
├── static/react/       # React构建输出
├── templates/          # Django模板 (服务React)
└── staticfiles/        # Django收集的静态文件
```

## 🛠️ 本地开发

1. **启动后端**:
   ```bash
   docker-compose up -d db
   source family_venv/bin/activate
   python manage.py runserver
   ```

2. **启动前端**:
   ```bash
   cd frontend
   npm run dev
   ```

## 🎯 部署流程

Heroku自动执行以下步骤：

1. **检测buildpacks**: Node.js → Python
2. **构建前端**: `npm run heroku-postbuild` 
3. **安装Python依赖**: `pip install -r requirements.txt`
4. **收集静态文件**: `python manage.py collectstatic`
5. **启动应用**: `gunicorn config.wsgi:application`

## ✅ 验证部署

部署后访问以下URL验证：

- `https://your-app.herokuapp.com/` → 重定向到应用
- `https://your-app.herokuapp.com/app/` → React前端
- `https://your-app.herokuapp.com/admin/` → Django Admin
- `https://your-app.herokuapp.com/api/health/` → API健康检查

## 🐛 故障排除

**内存不足**:
```bash
heroku logs --tail
# 查看是否有内存相关错误
```

**静态文件404**:
```bash
heroku run python manage.py collectstatic --noinput
```

**数据库问题**:
```bash
heroku run python manage.py migrate
```