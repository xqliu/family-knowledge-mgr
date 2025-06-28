# Claude Code 开发指令文件

## 项目概述

这是一个基于Django的家族知识管理系统，使用Django Admin作为主界面，集成RAG对话和Text2SQL查询功能。系统旨在帮助家庭保存、组织和传承家族记忆。

## 技术要求

### 核心技术栈
- **后端框架**: Django 4.x
- **数据库**: PostgreSQL + pgvector扩展
- **AI集成**: LangChain + Anthropic Claude API
- **缓存**: Redis
- **部署目标**: Heroku (512MB内存限制)

### Python依赖包
```
Django>=4.2
psycopg2-binary
django-redis
langchain
langchain-anthropic
langchain-postgres
anthropic
python-decouple
gunicorn
whitenoise
Pillow
```

## 开发任务

### 第一阶段：基础架构搭建

1. **Django项目初始化**
   - 创建Django项目结构
   - 配置settings.py（支持Heroku部署）
   - 设置PostgreSQL数据库连接
   - 配置Redis缓存
   - 设置静态文件处理

2. **核心领域模型开发**
   按照设计文档创建以下Django模型：
   - People (人物)
   - Story (故事)
   - Event (事件)
   - Relationship (关系)
   - Multimedia (多媒体)
   - Health (健康医疗)
   - Heritage (传承)
   - Planning (未来规划)
   - Location (地点)
   - Institution (机构)
   - Career (职业履历)
   - Assets (资产文档)
   - Timeline (时间线)

3. **Django Admin配置**
   - 为每个模型创建Admin类
   - 配置list_display, list_filter, search_fields
   - 设置filter_horizontal for多对多关系
   - 创建自定义Admin actions
   - 配置Admin界面的中文显示

### 第二阶段：AI功能集成

4. **RAG系统搭建**
   - 配置pgvector扩展
   - 创建文档embedding功能
   - 实现向量存储和检索
   - 集成LangChain pipeline
   - 配置Anthropic Claude API

5. **Text2SQL功能**
   - 实现Django模型到SQL schema的自动转换
   - 创建自然语言到SQL的转换器
   - 添加SQL查询安全性检查
   - 集成到Django Admin中

6. **智能功能**
   - 文本内容自动分析和标签提取
   - 相关内容推荐算法
   - 自动关系发现功能

### 第三阶段：用户界面优化

7. **Django Admin定制**
   - 创建自定义Admin模板
   - 添加时间线视图
   - 实现关系图谱显示
   - 优化移动端体验

8. **AI交互界面**
   - 在Admin中添加聊天界面
   - 实现自然语言查询输入框
   - 创建查询结果展示页面
   - 添加查询历史记录

### 第四阶段：部署和优化

9. **Heroku部署配置**
   - 创建Procfile和requirements.txt
   - 配置环境变量
   - 设置数据库迁移
   - 配置静态文件服务

10. **性能优化**
    - 数据库查询优化
    - 缓存策略实现
    - 内存使用优化
    - 响应时间优化

## 开发规范

### 代码结构
```
family_knowledge/
├── manage.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── family_knowledge/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/
│   ├── __init__.py
│   ├── models.py
│   ├── admin.py
│   ├── views.py
│   └── apps.py
├── ai_integration/
│   ├── __init__.py
│   ├── rag.py
│   ├── text2sql.py
│   └── utils.py
├── static/
├── templates/
└── media/
```

### Django模型设计原则
1. **字段命名**: 使用清晰的英文字段名，添加verbose_name中文显示
2. **关系设计**: 明确外键和多对多关系，合理设置related_name
3. **Meta类**: 设置proper ordering和verbose_name
4. **方法定义**: 实现__str__方法和get_absolute_url
5. **验证**: 添加必要的字段验证和model validation

### AI集成规范
1. **API密钥**: 使用环境变量存储敏感信息
2. **错误处理**: 完善的异常处理和降级策略
3. **缓存**: 合理使用缓存减少API调用
4. **安全性**: 输入验证和输出过滤

### Admin定制规范
1. **权限控制**: 基于用户角色的权限管理
2. **搜索优化**: 合理配置搜索字段和索引
3. **批量操作**: 提供高效的批量处理功能
4. **用户体验**: 简洁直观的界面设计

## 环境变量配置

创建.env文件，包含以下变量：
```
SECRET_KEY=your-django-secret-key
DEBUG=False
DATABASE_URL=your-postgresql-url
REDIS_URL=your-redis-url
ANTHROPIC_API_KEY=your-anthropic-api-key
ALLOWED_HOSTS=localhost,127.0.0.1,.herokuapp.com
```

## 测试要求

### 单元测试
- 为每个模型编写测试用例
- 测试AI功能的核心逻辑
- 测试Admin功能的正确性

### 集成测试
- 测试RAG系统的端到端流程
- 测试Text2SQL的准确性
- 测试Heroku部署的完整性

## 部署检查清单

### Heroku准备
- [ ] requirements.txt包含所有依赖
- [ ] Procfile配置正确
- [ ] runtime.txt指定Python版本
- [ ] 环境变量设置完成
- [ ] PostgreSQL插件安装
- [ ] Redis插件安装

### 数据库迁移
- [ ] 创建迁移文件
- [ ] 应用迁移到生产环境
- [ ] 创建超级用户
- [ ] 导入初始数据

### 性能验证
- [ ] 内存使用在512MB以内
- [ ] 响应时间合理
- [ ] AI功能正常工作
- [ ] 缓存策略有效

## 开发优先级

1. **高优先级**: 核心模型创建、基础Admin配置、PostgreSQL集成
2. **中优先级**: RAG功能、Text2SQL、AI集成
3. **低优先级**: 界面美化、高级功能、性能优化

## 注意事项

1. **内存限制**: 时刻注意Heroku 512MB内存限制，优化内存使用
2. **API配额**: 合理使用Anthropic API，避免超出配额
3. **数据安全**: 家族数据的隐私保护至关重要
4. **简单至上**: 保持KISS原则，避免过度工程化
5. **中文支持**: 确保系统完全支持中文内容

请按照这个指令文件逐步开发，如果遇到具体问题，可以随时询问详细的实现方案。
