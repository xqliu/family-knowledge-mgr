# 🧪 Testing Guide for Family Knowledge Management System

This document explains the testing strategy and how to run different types of tests for both backend and frontend components.

## 📋 Testing Overview

Our testing strategy covers multiple layers:
- **Unit Tests**: Individual component/function testing
- **Integration Tests**: Component interaction testing  
- **AI Infrastructure Tests**: Specialized AI/ML component testing
- **E2E Tests**: Full user workflow testing

## 🐍 Backend Testing (Django + AI)

### Quick Commands

```bash
# Run all backend tests with coverage
pytest --cov=family --cov=api --cov=ai_integration --cov-report=html --cov-report=term-missing

# Run specific app tests
python manage.py test family
python manage.py test ai_integration

# Run only AI integration tests
pytest ai_integration/tests/ -v

# Run production tests with real APIs (requires API keys)
./test_ai.sh
```

### Backend Test Scripts

| Script | Purpose | Requirements | Use Case |
|--------|---------|--------------|----------|
| `pytest` | ✅ Standard Django testing | PostgreSQL + pgvector | Development, CI/CD |
| `test_ai.sh` | Production readiness | Real API keys + Database | Final production testing |

### Test Structure

```
knowledge_mgr/
├── family/tests/              # Core family model tests
├── api/tests/                 # API endpoint tests  
├── ai_integration/tests/      # AI component unit tests
├── test_ai_*.sh              # AI infrastructure test scripts
└── conftest.py               # Global test configuration
```

## ⚛️ Frontend Testing (React + TypeScript)

### Quick Commands

```bash
cd frontend

# Run all tests with coverage
npm run test:coverage

# Run tests in watch mode
npm test

# Run specific test files
npm test ChatInterface
npm test App

# Lint and type check
npm run lint
npm run type-check
```

### Frontend Test Structure

```
frontend/
├── src/
│   ├── __tests__/                    # App-level tests
│   ├── components/chat/__tests__/    # Chat component tests
│   └── test-utils.tsx               # Testing utilities
├── coverage/                        # Coverage reports
└── vitest.config.ts                # Test configuration
```

### Test Types

- **Component Tests**: React Testing Library + Vitest
- **Unit Tests**: Individual function/hook testing
- **Integration Tests**: Component interaction testing
- **Mock Tests**: API interaction with mocked responses

## 🤖 AI Infrastructure Testing

### Testing Levels

1. **Logic Tests** (`test_ai_unit_only.sh`)
   - Content hashing and extraction
   - Query classification algorithms
   - Language detection
   - No external dependencies

2. **Service Tests** (`test_ai_ci.sh`)
   - API endpoint structure
   - Request/response handling
   - Error handling
   - Mocked AI responses

3. **Integration Tests** (`test_ai_mock.sh`)
   - Database operations
   - Embedding caching
   - Search functionality
   - Performance testing

4. **Production Tests** (`test_ai.sh`)
   - Real API integration
   - Actual embedding generation
   - End-to-end RAG pipeline
   - Production environment validation

### AI Test Coverage

| Component | Unit Tests | Integration Tests | Production Tests |
|-----------|------------|------------------|-----------------|
| EmbeddingService | ✅ | ✅ | ✅ |
| SearchService | ✅ | ✅ | ✅ |
| RAGService | ✅ | ✅ | ✅ |
| ChatInterface | ✅ | ✅ | ✅ |
| API Endpoints | ✅ | ✅ | ✅ |

## 🚀 CI/CD Integration

### GitHub Actions Workflow

Our CI/CD pipeline runs:

1. **Backend Tests**
   - AI infrastructure tests (CI optimized)
   - Django unit and integration tests
   - Coverage reporting

2. **Frontend Tests**
   - React component tests
   - TypeScript type checking
   - ESLint code quality checks
   - Coverage reporting

3. **Coverage Reporting**
   - Combined backend + frontend coverage
   - GitHub Pages deployment
   - PR comment with results

### Running Locally Like CI

```bash
# Backend (matches CI environment)
export DJANGO_SETTINGS_MODULE=config.settings
export DATABASE_URL='sqlite:///test.db'
./test_ai_ci.sh
pytest --cov=family --cov=api --cov=ai_integration

# Frontend (matches CI environment)
cd frontend
npm ci
npm run lint
npm run test:coverage
```

## 📊 Coverage Targets

| Component | Target | Current Status |
|-----------|---------|---------------|
| Django Backend | 80%+ | ✅ Achieved |
| React Frontend | 90%+ | ✅ Achieved |
| AI Integration | 85%+ | ✅ Achieved |

## 🔧 Development Workflow

### Before Committing

```bash
# Quick validation (< 30 seconds)
./test_ai_unit_only.sh

# Frontend quick check
cd frontend && npm test -- --run
```

### Before Pull Request

```bash
# Full backend validation
./test_ai_ci.sh
pytest --cov=family --cov=api --cov=ai_integration

# Full frontend validation  
cd frontend
npm run lint
npm run test:coverage
npm run build
```

### Before Deployment

```bash
# Production readiness (requires API keys)
export OPENAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key
./test_ai.sh
```

## 🛠️ Troubleshooting

### Common Issues

**Database Vector Extension Error**
```bash
# Enable pgvector manually
docker-compose exec db psql -U family_user -d family_knowledge -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

**API Key Tests Failing**
```bash
# Use CI-optimized tests instead
./test_ai_ci.sh  # No API keys needed
```

**Frontend Tests Timing Out**
```bash
# Increase timeout in vitest.config.ts
export NODE_OPTIONS="--max_old_space_size=4096"
npm test
```

### Test Data Cleanup

```bash
# Backend test data
python manage.py flush --noinput
python manage.py migrate

# Frontend test cache
cd frontend
rm -rf node_modules/.cache
npm run test:coverage -- --coverage.clean
```

## 📚 Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Vitest Documentation](https://vitest.dev/)
- [Pytest Coverage](https://pytest-cov.readthedocs.io/)

## 🎯 Quick Reference

### Most Common Commands

```bash
# Development testing (fast)
./test_ai_unit_only.sh && cd frontend && npm test -- --run

# CI simulation (complete)
./test_ai_ci.sh && cd frontend && npm run test:coverage

# Production validation (with real APIs)
./test_ai.sh

# Coverage reports
pytest --cov=family --cov=api --cov=ai_integration --cov-report=html
cd frontend && npm run test:coverage
```

### Environment Variables

```bash
# Required for production tests
export OPENAI_API_KEY=your_openai_key
export ANTHROPIC_API_KEY=your_anthropic_key

# Required for all Django tests
export DJANGO_SETTINGS_MODULE=config.settings

# Optional for database tests
export DATABASE_URL=postgresql://user:pass@localhost/db
```