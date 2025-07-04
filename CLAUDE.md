# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django-based family knowledge management system designed to help families preserve, organize, and inherit family memories, relationships, and important information. The system uses Django Admin as the main interface and integrates RAG (Retrieval-Augmented Generation) conversation and Text2SQL query capabilities.

**Key Characteristics:**
- Target deployment: Heroku with 512MB memory limitation
- Target users: 5-10 family members
- Main interface: Django Admin (customized)
- AI integration: LangChain + Anthropic Claude API

## Commands

### Project Initialization
```bash
# Initialize the project (creates virtual environment and Django project)
chmod +x init.sh && ./init.sh
```

### Development Commands
```bash
# Activate virtual environment
source family_venv/bin/activate

# Django development server
python manage.py runserver

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell
```

### Production/Deployment
```bash
# Production server (Heroku)
gunicorn family_knowledge.wsgi:application

# Static files collection
python manage.py collectstatic --noinput
```

## Architecture

### Technology Stack
- **Backend**: Django 5.2.3 (LTS)
- **Database**: PostgreSQL with pgvector extension
- **AI Integration**: LangChain + Anthropic Claude API
- **Caching**: Redis (25MB Heroku limit)
- **Deployment**: Heroku (512MB memory limit)
- **File Storage**: Heroku filesystem + external storage

### Core Domain Models

The system is built around 13 core domain models that represent family knowledge:

**Primary Entities:**
1. **People** - Family members and important individuals
2. **Story** - Family memories, anecdotes, and experiences
3. **Event** - Important milestones and activities
4. **Relationship** - Network of relationships between people
5. **Multimedia** - Photos, videos, documents, audio files
6. **Health** - Personal and family health records
7. **Heritage** - Family values, traditions, and wisdom
8. **Planning** - Future goals and family vision

**Supporting Entities:**
9. **Location** - Geographic information and places
10. **Institution** - External organizations (hospitals, schools, companies)
11. **Career** - Work and education history
12. **Assets** - Important property and documents
13. **Timeline** - Time-based organization of information

### Key Relationships
- Many-to-many relationships between People, Stories, Events, and Multimedia
- Foreign key relationships linking people to health records, career history
- Location and Institution entities support other models
- Timeline provides chronological organization

### AI Integration Architecture

**Text2SQL System:**
- Django model schemas automatically converted to SQL
- Natural language queries converted to safe, read-only SQL
- Support for complex cross-table relationship queries

**RAG Conversation System:**
- Text content vectorized and stored in pgvector
- Hybrid retrieval: structured queries + semantic search
- Context-aware intelligent conversation generation

**Smart Features:**
- Auto-extraction of people, time, location from text
- Content recommendation algorithms
- Automatic relationship discovery

### Django Admin Customization

The system extends Django Admin with:
- Custom Admin classes for each model with proper list_display, filters, search
- filter_horizontal for many-to-many relationships
- Custom Admin actions and Chinese interface
- Timeline views and relationship graph displays
- AI chat interface integration
- Natural language query input boxes

### File Structure
```
knowledge_mgr/
├── init.sh                 # Project initialization script
├── docs/
│   ├── claude_instruction.md    # Detailed development instructions
│   └── domain_design.md         # Complete domain model design
└── [Django project structure created by init.sh]
    ├── family_knowledge/    # Main Django project
    ├── core/               # Core domain models
    ├── ai_integration/     # RAG and Text2SQL functionality
    ├── static/            # Static files (CSS, JS, images)
    ├── templates/         # Custom templates
    ├── media/            # User uploads
    └── requirements.txt   # Python dependencies
```

## Development Guidelines

### Testing and TDD Standards
- **ALWAYS use Test-Driven Development (TDD)** for new features
- Write tests BEFORE implementing functionality
- Focus on data integrity (models 90%+) and core workflows (API/forms 80%+)
- Current coverage targets achieved:
  - Django Backend: 90%+ coverage with pytest + factory-boy
  - React Frontend: 90%+ coverage with Vitest + React Testing Library
  - CI/CD pipeline with GitHub Actions + GitHub Pages coverage reports
- For family-scale projects: Prioritize model and API tests over admin interface tests

### CI/CD and Deployment Standards
- **Add [skip ci] to commit messages** when changes are documentation-only (no FE/BE code changes)
- This prevents unnecessary GitHub Actions runs and Heroku deployments
- Examples of [skip ci] scenarios: README updates, CLAUDE.md changes, documentation files
- Always run CI/CD for code changes that affect functionality or tests

### Model Design Principles
- Use clear English field names with verbose_name for Chinese display
- Define proper relationships with explicit related_name
- Implement __str__ methods and get_absolute_url
- Add field validation and model validation as needed

### AI Integration Standards
- Store API keys in environment variables
- Implement comprehensive error handling and fallback strategies
- Use caching to minimize API calls
- Validate inputs and filter outputs for security

### Memory Optimization (Critical for Heroku)
- Monitor memory usage to stay within 512MB limit
- Optimize database queries and use select_related/prefetch_related
- Implement efficient caching strategies
- Optimize static file serving with whitenoise

## Environment Variables

Required environment variables (create .env file):
```
SECRET_KEY=your-django-secret-key
DEBUG=False
DATABASE_URL=your-postgresql-url
REDIS_URL=your-redis-url
ANTHROPIC_API_KEY=your-anthropic-api-key
ALLOWED_HOSTS=localhost,127.0.0.1,.herokuapp.com
```

## Development Phases

1. **Phase 1**: Basic Django setup, core models, Django Admin configuration
2. **Phase 2**: AI integration (RAG system, Text2SQL, LangChain pipeline)
3. **Phase 3**: UI optimization (custom Admin templates, AI interfaces)
4. **Phase 4**: Heroku deployment and performance optimization

## Important Constraints

- **Database**: ALWAYS use PostgreSQL - this system requires PostgreSQL with pgvector extension for AI/RAG functionality. **NEVER USE SQLITE UNDER ANY CIRCUMSTANCES** - even for testing. Always use PostgreSQL with pgvector for all environments including CI/CD testing.
- **Memory Limit**: Must operate within Heroku's 512MB memory constraint
- **Chinese Support**: Full Chinese language support required
- **Security**: Family data privacy is critical - implement proper access controls
- **Simplicity**: Follow KISS principle - avoid over-engineering
- **API Usage**: Manage Anthropic API quota carefully with caching and fallbacks

## CRITICAL DATABASE RULE
**SQLITE IS ABSOLUTELY FORBIDDEN** - This system MUST use PostgreSQL with pgvector extension in ALL environments:
- Development: PostgreSQL + pgvector
- Testing: PostgreSQL + pgvector  
- CI/CD: PostgreSQL + pgvector
- Production: PostgreSQL + pgvector

The vector fields and AI functionality require pgvector. SQLite cannot be used even for testing. If tests fail due to pgvector, use mocking instead of changing the database.

## Production Deployment Information

### Heroku Configuration
- **App Name**: `family-knowledge-mgr`
- **Production URL**: `https://llbrother.org`
- **Log Access**: `heroku logs --tail --app=family-knowledge-mgr`
- **Dyno Management**: 
  - Scale down when sleeping: `heroku ps:scale web=0 --app=family-knowledge-mgr`
  - Scale up when needed: `heroku ps:scale web=1 --app=family-knowledge-mgr`

### URL Structure
- `/app/` - React frontend (requires authentication)
- `/api/` - Django REST API (requires authentication)
- `/admin/` - Django admin interface

### Authentication Architecture
- **Method**: Django admin login system
- **React App Protection**: Custom `protected_react_serve` view with `@login_required` decorator (`family/views.py:8`)
- **API Protection**: Custom `@api_login_required` decorator (`api/decorators.py`)
- **Login Flow**: Unauthenticated users redirected to `/admin/login/?next=/app/`

### Key Technical Notes
- **Middleware Order**: Authentication middleware must come before custom middleware in settings
- **Static Serving**: React app served through protected Django view (not direct serve)
- **Virtual Environment**: Always activate `family_venv/bin/activate` for local development

### Authentication Test Commands
```bash
# API should return 401 when not authenticated
curl https://llbrother.org/api/family/overview/

# App route should return 302 redirect to login
curl -I https://llbrother.org/app/
```

## Session Management

### Auto-Sleep Behavior
When the user indicates session end with phrases like "bye", "good bye", "going to rest", etc., automatically scale down the Heroku dyno to save resources:
```bash
heroku ps:scale web=0 --app=family-knowledge-mgr
```

### React Frontend Architecture

#### Current Frontend Stack
- **Framework**: React 19.1.0 with TypeScript and Vite build system
- **Testing**: Vitest + React Testing Library with 99.18% code coverage
- **Styling**: CSS modules with KISS design principles
- **Build**: Optimized for Heroku's 512MB memory constraint

#### Key Frontend Components
- **App.tsx**: Main application layout with floating chat interface
- **ChatInterface.tsx**: AI conversation component with RAG integration  
- **BottomChat.tsx**: Floating chat bubble positioned bottom-right (350px width on desktop)
- **Mobile Responsive**: Full-width minus margins on mobile devices

#### Frontend Development Standards
- **Code Coverage**: Maintain 99%+ test coverage with comprehensive unit tests
- **CSS Architecture**: Use KISS principles, avoid redundant styles, fix root causes not symptoms
- **CSS Fix Principle**: ALWAYS fix CSS issues at the root cause, not by adding more specific selectors
  - **❌ Wrong**: Using `button.send-button` with `padding: 0 !important` to override global styles
  - **✅ Correct**: Fix global button styles to use conditional defaults (`button:not([class])`) 
  - **Avoid**: CSS specificity wars, stacked overrides, and `!important` for standard styling
  - **Prefer**: Neutral CSS resets + semantic component styles without conflicts
- **Mobile-First**: Responsive design with proper viewport handling for iOS devices
- **Build Optimization**: Bundle size monitoring, tree shaking, code splitting
- **Pre-Commit Checklist**: Before committing any code changes, ALWAYS run:
  - `npm run lint` - Check code style and catch common errors
  - `npm test -- --run` - Run all unit tests and ensure nothing is broken
  - Only commit if both lint and tests pass successfully