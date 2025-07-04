#!/usr/bin/env python
"""
Simple test for ai_integration URLs with coverage
"""
import os
import sys

# Setup Django BEFORE any imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Start coverage before any imports
try:
    import coverage
    cov = coverage.Coverage(source=['ai_integration.urls'])
    cov.start()
    coverage_available = True
except ImportError:
    coverage_available = False

import django
django.setup()

# Now import the module under test
from ai_integration.urls import urlpatterns, app_name

print("Testing ai_integration.urls module...")

# Test app_name
print(f"✅ app_name: {app_name}")
assert app_name == 'ai_integration'

# Test urlpatterns
print(f"✅ urlpatterns length: {len(urlpatterns)}")
assert len(urlpatterns) == 2

# Test pattern names
names = [pattern.name for pattern in urlpatterns]
print(f"✅ URL names: {names}")
assert 'chat' in names
assert 'search' in names

# Test pattern paths
chat_pattern = None
search_pattern = None
for pattern in urlpatterns:
    if pattern.name == 'chat':
        chat_pattern = pattern
    elif pattern.name == 'search':
        search_pattern = pattern

print(f"✅ Chat pattern found: {chat_pattern is not None}")
print(f"✅ Search pattern found: {search_pattern is not None}")
assert chat_pattern is not None
assert search_pattern is not None

# Test view imports
from ai_integration import views
print(f"✅ Views module imported successfully")
assert hasattr(views, 'chat_endpoint')
assert hasattr(views, 'semantic_search')
assert callable(views.chat_endpoint)
assert callable(views.semantic_search)

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