#!/usr/bin/env python
"""
Simple test for api URLs with coverage
"""
import os
import sys

# Setup Django BEFORE any imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Start coverage before any imports
try:
    import coverage
    cov = coverage.Coverage(source=['api.urls'])
    cov.start()
    coverage_available = True
except ImportError:
    coverage_available = False

import django
django.setup()

# Now import the module under test
from api.urls import urlpatterns, app_name

print("Testing api.urls module...")

# Test app_name
print(f"✅ app_name: {app_name}")
assert app_name == 'api'

# Test urlpatterns
print(f"✅ urlpatterns length: {len(urlpatterns)}")
assert len(urlpatterns) == 3

# Test pattern names
names = [pattern.name for pattern in urlpatterns]
print(f"✅ URL names: {names}")
assert 'health_check' in names
assert 'family_overview' in names
assert 'ai_chat' in names

# Test pattern paths
health_pattern = None
family_pattern = None
chat_pattern = None
for pattern in urlpatterns:
    if pattern.name == 'health_check':
        health_pattern = pattern
    elif pattern.name == 'family_overview':
        family_pattern = pattern
    elif pattern.name == 'ai_chat':
        chat_pattern = pattern

print(f"✅ Health pattern found: {health_pattern is not None}")
print(f"✅ Family pattern found: {family_pattern is not None}")
print(f"✅ Chat pattern found: {chat_pattern is not None}")
assert health_pattern is not None
assert family_pattern is not None
assert chat_pattern is not None

# Test pattern matching
print("✅ Testing pattern matching...")
assert health_pattern.pattern.regex.match('health/')
assert family_pattern.pattern.regex.match('family/overview/')
assert chat_pattern.pattern.regex.match('ai/chat/')

# Test view imports
from api import views
print(f"✅ Views module imported successfully")
assert hasattr(views, 'health_check')
assert hasattr(views, 'family_overview')
assert hasattr(views, 'ai_chat')
assert callable(views.health_check)
assert callable(views.family_overview)
assert callable(views.ai_chat)

# Test URL names are unique
assert len(names) == len(set(names)), "URL names should be unique"

print("\n" + "="*50)
print("All tests passed!")
print("="*50)

# Stop coverage and report
if coverage_available:
    cov.stop()
    cov.save()
    print("\nCOVERAGE REPORT:")
    print("-" * 30)
    cov.report()