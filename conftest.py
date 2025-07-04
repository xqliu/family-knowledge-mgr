"""
Global pytest configuration for AI integration tests
Sets up pgvector extension for test database
"""
import pytest
from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.test.utils import setup_test_environment, teardown_test_environment


@pytest.fixture(scope='session')
def django_db_setup():
    """
    Custom database setup that enables pgvector extension
    """
    settings.DATABASES['default']['NAME'] = 'test_' + settings.DATABASES['default']['NAME']
    
    # Create test database with pgvector
    with connection.cursor() as cursor:
        try:
            # Enable pgvector extension in test database
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        except Exception as e:
            # If we can't create extension, we'll mock the vector fields
            print(f"Warning: Could not create vector extension: {e}")
    
    # Run migrations
    call_command('migrate', '--run-syncdb', verbosity=0, interactive=False)
    
    yield


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Give all tests access to the database
    """
    pass