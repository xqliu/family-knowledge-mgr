# 测试指南 - 家庭知识管理系统

## 概述

本项目采用全面的测试策略，包含Django后端和React前端的单元测试、集成测试，以及代码覆盖率监控。目标是达到90%以上的代码覆盖率，确保代码质量和系统稳定性。

## 测试架构

### 后端测试 (Django)
- **测试框架**: pytest + pytest-django
- **覆盖率工具**: pytest-cov
- **测试数据**: factory-boy
- **Mock工具**: pytest-mock
- **并行执行**: pytest-xdist

### 前端测试 (React)
- **测试框架**: Vitest
- **测试工具**: React Testing Library
- **覆盖率工具**: @vitest/coverage-v8
- **测试环境**: jsdom
- **用户交互**: @testing-library/user-event

## 快速开始

### 1. 安装依赖

**后端依赖** (已在requirements.txt中):
```bash
# 激活虚拟环境
source family_venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

**前端依赖**:
```bash
cd frontend
npm install
```

### 2. 运行测试

**后端测试**:
```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest family/tests/test_models.py

# 运行测试并生成覆盖率报告
pytest --cov=family --cov=api --cov-report=html

# 运行测试并要求90%覆盖率
pytest --cov-fail-under=90
```

**前端测试**:
```bash
cd frontend

# 运行所有测试
npm run test

# 运行测试并生成覆盖率报告
npm run test:coverage

# 运行测试的UI界面
npm run test:ui
```

## 测试结构

### 后端测试结构
```
family/tests/
├── __init__.py
├── factories.py           # 测试数据工厂
├── test_models.py         # 模型测试
├── test_views.py          # 视图测试 (如果有)
└── test_admin.py          # Admin测试 (如果有)

api/tests/
├── __init__.py
├── test_views.py          # API端点测试
└── test_integration.py    # 集成测试
```

### 前端测试结构
```
frontend/src/
├── __tests__/             # 测试文件
│   ├── App.test.tsx
│   ├── components/        # 组件测试
│   └── utils/            # 工具函数测试
├── test-setup.ts         # 测试配置
└── test-utils.tsx        # 测试工具函数
```

## 编写测试

### Django后端测试示例

**模型测试**:
```python
import pytest
from family.tests.factories import PersonFactory

@pytest.mark.django_db
class TestPersonModel:
    def test_person_creation(self):
        person = PersonFactory()
        assert person.name
        assert str(person) == person.name
    
    def test_person_relationships(self):
        person = PersonFactory()
        story = StoryFactory()
        person.stories.add(story)
        assert person.stories.count() == 1
```

**API测试**:
```python
import pytest
from django.test import Client

@pytest.mark.django_db
class TestAPIViews:
    def setup_method(self):
        self.client = Client()
    
    def test_health_check(self):
        response = self.client.get('/api/health/')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'
```

### React前端测试示例

**组件测试**:
```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '../test-utils'
import App from '../App'

describe('App Component', () => {
    it('renders main heading', () => {
        render(<App />)
        expect(screen.getByText('🏠 家庭知识库')).toBeInTheDocument()
    })
    
    it('handles API calls', async () => {
        global.fetch = vi.fn().mockResolvedValue({
            ok: true,
            json: async () => ({ message: 'API运行正常' })
        })
        
        render(<App />)
        await waitFor(() => {
            expect(screen.getByText(/API运行正常/)).toBeInTheDocument()
        })
    })
})
```

## 代码覆盖率

### 覆盖率目标
- **总体目标**: 90%
- **模型层**: 95% (核心业务逻辑)
- **API层**: 95% (用户接口)
- **组件层**: 90% (UI组件)

### 查看覆盖率报告

**本地开发**:
```bash
# 后端覆盖率
pytest --cov=family --cov=api --cov-report=html
open htmlcov/index.html

# 前端覆盖率
cd frontend && npm run test:coverage
open coverage/index.html
```

**线上报告**:
- 主要仪表板: `https://your-username.github.io/knowledge_mgr/coverage/`
- 后端详细报告: `https://your-username.github.io/knowledge_mgr/coverage/backend/`
- 前端详细报告: `https://your-username.github.io/knowledge_mgr/coverage/frontend/`

## CI/CD集成

### GitHub Actions工作流

我们的CI/CD流水线包含以下步骤:

1. **并行测试执行**:
   - Django后端测试
   - React前端测试

2. **覆盖率报告生成**:
   - 合并前后端覆盖率
   - 生成统一仪表板

3. **GitHub Pages部署**:
   - 自动部署覆盖率报告
   - 仅在main分支触发

4. **Heroku部署**:
   - 仅在所有测试通过后执行
   - 自动构建前端资源

### 必需的GitHub Secrets

在GitHub仓库设置中添加以下secrets:

```
HEROKU_API_KEY      # Heroku API密钥
HEROKU_APP_NAME     # Heroku应用名称
HEROKU_EMAIL        # Heroku账户邮箱
```

### 分支策略

- **main分支**: 生产环境，需要通过PR且所有测试通过
- **develop分支**: 开发环境，自动运行测试
- **feature分支**: 功能分支，创建PR时运行测试

## 测试最佳实践

### 1. 测试组织
- 使用描述性的测试名称
- 一个测试函数只测试一个功能点
- 使用适当的测试标记 (`@pytest.mark.django_db`, `@pytest.mark.slow`)

### 2. 测试数据
- 使用factory-boy创建测试数据
- 避免硬编码测试数据
- 每个测试使用独立的数据集

### 3. Mock和Stub
- Mock外部API调用
- 避免依赖真实的文件系统
- 使用pytest.fixture管理共享资源

### 4. 断言
- 使用具体的断言而不是泛型断言
- 测试边界条件和错误情况
- 验证副作用（如数据库变更）

## 常见问题

### Q: 测试运行缓慢怎么办？
A: 
- 使用`pytest-xdist`并行运行: `pytest -n auto`
- 使用`--reuse-db`避免重新创建数据库
- 将慢测试标记为`@pytest.mark.slow`并在快速开发时跳过

### Q: 覆盖率达不到90%怎么办？
A:
- 检查哪些代码未被覆盖: `pytest --cov-report=term-missing`
- 添加边界条件测试
- 测试错误处理路径
- 排除不需要测试的代码（如配置文件）

### Q: 前端测试如何处理API调用？
A:
- 使用`vi.fn()`模拟fetch调用
- 测试loading、success、error三种状态
- 使用`waitFor`等待异步操作完成

### Q: 如何测试Django Admin？
A:
- 创建superuser测试用户
- 使用`Client.login()`登录
- 测试列表页、创建页、编辑页的渲染和功能

## 参考资源

- [Django测试文档](https://docs.djangoproject.com/en/5.0/topics/testing/)
- [pytest-django文档](https://pytest-django.readthedocs.io/)
- [React Testing Library文档](https://testing-library.com/docs/react-testing-library/intro/)
- [Vitest文档](https://vitest.dev/)
- [factory-boy文档](https://factoryboy.readthedocs.io/)

## 贡献指南

1. 为新功能编写测试
2. 确保测试覆盖率不下降
3. 运行完整测试套件: `pytest && cd frontend && npm run test`
4. 提交前检查覆盖率: `pytest --cov-fail-under=90`