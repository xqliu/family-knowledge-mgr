#!/usr/bin/env python
"""
Comprehensive test for embedding service targeting 90%+ branch coverage
"""
import os
import sys

# Setup Django BEFORE any imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Start coverage before any imports
try:
    import coverage
    cov = coverage.Coverage(source=['ai_integration.services.embedding_service'], branch=True)
    cov.start()
    coverage_available = True
except ImportError:
    coverage_available = False

import django
django.setup()

from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from django.utils import timezone
from ai_integration.services.embedding_service import EmbeddingService, embedding_service

print("Testing EmbeddingService with comprehensive branch coverage...")

# Test 1: Basic initialization
print("✅ Test 1: Basic initialization")
service = EmbeddingService()
assert service.client is not None
assert service.model == "text-embedding-3-small"

# Test 2: generate_embedding empty/None text branches
print("✅ Test 2: Empty text handling")
assert service.generate_embedding('') is None
assert service.generate_embedding('   ') is None
assert service.generate_embedding(None) is None

# Test 3: generate_embedding successful response
print("✅ Test 3: Successful embedding generation")
mock_embedding = [0.1, 0.2, 0.3] * 512  # 1536 dimensions
with patch.object(service, 'client') as mock_client:
    mock_response = Mock()
    mock_response.data = [Mock()]
    mock_response.data[0].embedding = mock_embedding
    mock_client.embeddings.create.return_value = mock_response
    
    result = service.generate_embedding('test text')
    assert result == mock_embedding
    mock_client.embeddings.create.assert_called_once_with(
        model="text-embedding-3-small",
        input="test text"
    )

# Test 4: generate_embedding exception handling
print("✅ Test 4: Embedding generation failure")
with patch.object(service, 'client') as mock_client:
    mock_client.embeddings.create.side_effect = Exception('API Error')
    
    result = service.generate_embedding('test text')
    assert result is None

# Test 5: get_content_hash consistency
print("✅ Test 5: Content hash generation")
hash1 = service.get_content_hash('test content')
hash2 = service.get_content_hash('test content')
hash3 = service.get_content_hash('different content')

assert hash1 == hash2  # Same content = same hash
assert hash1 != hash3  # Different content = different hash
assert len(hash1) == 64  # SHA256 = 64 hex characters

# Test 6: get_or_create_embedding empty text
print("✅ Test 6: get_or_create_embedding empty text")
assert service.get_or_create_embedding('', 'story', 1) is None
assert service.get_or_create_embedding('   ', 'story', 1) is None

# Test 7: get_or_create_embedding with cache hit
print("✅ Test 7: Cache hit scenario")
mock_embedding = [0.1, 0.2, 0.3] * 512
with patch('ai_integration.services.embedding_service.EmbeddingCache') as mock_cache:
    mock_cached = Mock()
    mock_cached.embedding = mock_embedding
    mock_cache.objects.get.return_value = mock_cached
    
    result = service.get_or_create_embedding('test content', 'story', 1)
    assert result == mock_embedding
    mock_cache.objects.get.assert_called_once()

# Test 8: get_or_create_embedding with cache miss and successful generation
print("✅ Test 8: Cache miss with successful generation")
with patch('ai_integration.services.embedding_service.EmbeddingCache') as mock_cache:
    # Mock cache miss
    mock_cache.DoesNotExist = Exception
    mock_cache.objects.get.side_effect = mock_cache.DoesNotExist()
    
    # Mock successful embedding generation
    with patch.object(service, 'generate_embedding', return_value=mock_embedding):
        result = service.get_or_create_embedding('test content', 'story', 1)
        assert result == mock_embedding
        # Should call update_or_create to cache the result
        mock_cache.objects.update_or_create.assert_called_once()

# Test 9: get_or_create_embedding with cache miss and failed generation
print("✅ Test 9: Cache miss with failed generation")
with patch('ai_integration.services.embedding_service.EmbeddingCache') as mock_cache:
    mock_cache.DoesNotExist = Exception
    mock_cache.objects.get.side_effect = mock_cache.DoesNotExist()
    
    # Mock failed embedding generation
    with patch.object(service, 'generate_embedding', return_value=None):
        result = service.get_or_create_embedding('test content', 'story', 1)
        assert result is None
        # Should not call update_or_create since generation failed
        mock_cache.objects.update_or_create.assert_not_called()

# Test 10: update_model_embedding - no content_embedding field
print("✅ Test 10: update_model_embedding without content_embedding field")
mock_instance = Mock()
# Remove content_embedding attribute
if hasattr(mock_instance, 'content_embedding'):
    delattr(mock_instance, 'content_embedding')

result = service.update_model_embedding(mock_instance)
assert result is False

# Test 11: update_model_embedding - no content text
print("✅ Test 11: update_model_embedding with no content text")
mock_instance = Mock()
mock_instance.content_embedding = None
mock_instance.id = 1
with patch.object(service, '_extract_content_text', return_value=''):
    result = service.update_model_embedding(mock_instance)
    assert result is False

# Test 12: update_model_embedding - already up to date (no force)
print("✅ Test 12: update_model_embedding already up to date")
mock_instance = Mock()
mock_instance.content_embedding = mock_embedding
mock_instance.embedding_updated = timezone.now()
mock_instance.id = 1

with patch.object(service, '_extract_content_text', return_value='test content'):
    with patch('ai_integration.services.embedding_service.EmbeddingCache') as mock_cache:
        mock_cached = Mock()
        mock_cached.embedding = mock_embedding
        mock_cache.objects.get.return_value = mock_cached
        
        result = service.update_model_embedding(mock_instance, force_update=False)
        assert result is False

# Test 13: update_model_embedding - cache miss (needs update)
print("✅ Test 13: update_model_embedding cache miss")
mock_instance = Mock()
mock_instance.content_embedding = mock_embedding
mock_instance.embedding_updated = timezone.now()
mock_instance.id = 1

with patch.object(service, '_extract_content_text', return_value='test content'):
    with patch('ai_integration.services.embedding_service.EmbeddingCache') as mock_cache:
        mock_cache.DoesNotExist = Exception
        mock_cache.objects.get.side_effect = mock_cache.DoesNotExist()
        
        with patch.object(service, 'get_or_create_embedding', return_value=mock_embedding):
            result = service.update_model_embedding(mock_instance)
            assert result is True
            mock_instance.save.assert_called_once()

# Test 14: update_model_embedding - force update
print("✅ Test 14: update_model_embedding force update")
mock_instance = Mock()
mock_instance.content_embedding = mock_embedding
mock_instance.embedding_updated = timezone.now()
mock_instance.id = 1

with patch.object(service, '_extract_content_text', return_value='test content'):
    with patch.object(service, 'get_or_create_embedding', return_value=mock_embedding):
        result = service.update_model_embedding(mock_instance, force_update=True)
        assert result is True
        mock_instance.save.assert_called_once_with(
            update_fields=['content_embedding', 'embedding_updated']
        )

# Test 15: update_model_embedding - no embedding (no instance.embedding_updated)
print("✅ Test 15: update_model_embedding no existing embedding")
mock_instance = Mock()
mock_instance.content_embedding = None
mock_instance.embedding_updated = None
mock_instance.id = 1

with patch.object(service, '_extract_content_text', return_value='test content'):
    with patch.object(service, 'get_or_create_embedding', return_value=mock_embedding):
        result = service.update_model_embedding(mock_instance)
        assert result is True

# Test 16: update_model_embedding - embedding generation fails
print("✅ Test 16: update_model_embedding embedding generation fails")
mock_instance = Mock()
mock_instance.content_embedding = None
mock_instance.id = 1

with patch.object(service, '_extract_content_text', return_value='test content'):
    with patch.object(service, 'get_or_create_embedding', return_value=None):
        result = service.update_model_embedding(mock_instance)
        assert result is False

# Test 17: _extract_content_text for all model types
print("✅ Test 17: Content text extraction for different model types")

# Story
mock_story = Mock()
mock_story.__class__.__name__ = 'Story'
mock_story.title = 'Story Title'
mock_story.content = 'Story content'
result = service._extract_content_text(mock_story)
assert result == 'Story Title\n\nStory content'

# Event
mock_event = Mock()
mock_event.__class__.__name__ = 'Event'
mock_event.name = 'Event Name'
mock_event.description = 'Event description'
result = service._extract_content_text(mock_event)
assert result == 'Event Name\n\nEvent description'

# Heritage
mock_heritage = Mock()
mock_heritage.__class__.__name__ = 'Heritage'
mock_heritage.title = 'Heritage Title'
mock_heritage.description = 'Heritage description'
result = service._extract_content_text(mock_heritage)
assert result == 'Heritage Title\n\nHeritage description'

# Health
mock_health = Mock()
mock_health.__class__.__name__ = 'Health'
mock_health.title = 'Health Title'
mock_health.description = 'Health description'
result = service._extract_content_text(mock_health)
assert result == 'Health Title\n\nHealth description'

# Person with bio
mock_person = Mock()
mock_person.__class__.__name__ = 'Person'
mock_person.bio = 'Person biography'
mock_person.name = 'Person Name'
result = service._extract_content_text(mock_person)
assert result == 'Person biography'

# Person without bio
mock_person_no_bio = Mock()
mock_person_no_bio.__class__.__name__ = 'Person'
mock_person_no_bio.bio = None
mock_person_no_bio.name = 'Person Name'
result = service._extract_content_text(mock_person_no_bio)
assert result == 'Person Name'

# Unknown model with content field
mock_unknown = Mock()
mock_unknown.__class__.__name__ = 'UnknownModel'
mock_unknown.content = 'Some content'
result = service._extract_content_text(mock_unknown)
assert result == 'Some content'

# Unknown model with description field
mock_unknown2 = Mock()
mock_unknown2.__class__.__name__ = 'UnknownModel'
# Remove content attribute, add description
if hasattr(mock_unknown2, 'content'):
    delattr(mock_unknown2, 'content')
mock_unknown2.description = 'Some description'
result = service._extract_content_text(mock_unknown2)
assert result == 'Some description'

# Unknown model with bio field
mock_unknown3 = Mock()
mock_unknown3.__class__.__name__ = 'UnknownModel'
if hasattr(mock_unknown3, 'content'):
    delattr(mock_unknown3, 'content')
if hasattr(mock_unknown3, 'description'):
    delattr(mock_unknown3, 'description')
mock_unknown3.bio = 'Some bio'
result = service._extract_content_text(mock_unknown3)
assert result == 'Some bio'

# Unknown model with title field
mock_unknown4 = Mock()
mock_unknown4.__class__.__name__ = 'UnknownModel'
for attr in ['content', 'description', 'bio']:
    if hasattr(mock_unknown4, attr):
        delattr(mock_unknown4, attr)
mock_unknown4.title = 'Some title'
result = service._extract_content_text(mock_unknown4)
assert result == 'Some title'

# Unknown model with name field
mock_unknown5 = Mock()
mock_unknown5.__class__.__name__ = 'UnknownModel'
for attr in ['content', 'description', 'bio', 'title']:
    if hasattr(mock_unknown5, attr):
        delattr(mock_unknown5, attr)
mock_unknown5.name = 'Some name'
result = service._extract_content_text(mock_unknown5)
assert result == 'Some name'

# Unknown model with no recognized fields
mock_unknown6 = Mock()
mock_unknown6.__class__.__name__ = 'UnknownModel'
for attr in ['content', 'description', 'bio', 'title', 'name']:
    if hasattr(mock_unknown6, attr):
        delattr(mock_unknown6, attr)
result = service._extract_content_text(mock_unknown6)
assert result == ''

# Unknown model with empty field values
mock_unknown7 = Mock()
mock_unknown7.__class__.__name__ = 'UnknownModel'
mock_unknown7.content = ''
mock_unknown7.description = None
mock_unknown7.bio = ''
mock_unknown7.title = None
mock_unknown7.name = 'Final Name'
result = service._extract_content_text(mock_unknown7)
assert result == 'Final Name'

# Test 18: bulk_update_embeddings
print("✅ Test 18: Bulk update embeddings")

# Mock model class and instances
mock_model_class = Mock()
mock_model_class.__name__ = 'TestModel'

# Mock queryset
mock_instances = [Mock(id=i) for i in range(5)]
mock_queryset = Mock()
mock_queryset.count.return_value = 5
mock_queryset.__getitem__ = lambda self, key: mock_instances[key]

# Mock the models.Q import
from django.db import models
with patch('django.db.models.Q') as mock_q:
    mock_model_class.objects.filter.return_value = mock_queryset
    
    # Mock successful updates
    with patch.object(service, 'update_model_embedding', return_value=True):
        stats = service.bulk_update_embeddings(mock_model_class, batch_size=2)
        assert stats['updated'] == 5
        assert stats['skipped'] == 0
        assert stats['failed'] == 0

# Test 19: bulk_update_embeddings with mixed results
print("✅ Test 19: Bulk update with mixed results")
with patch('django.db.models.Q') as mock_q:
    mock_model_class.objects.filter.return_value = mock_queryset
    
    # Mock mixed results: success, skip, failure
    results = [True, False, True, False, True]
    with patch.object(service, 'update_model_embedding', side_effect=results):
        stats = service.bulk_update_embeddings(mock_model_class)
        assert stats['updated'] == 3
        assert stats['skipped'] == 2
        assert stats['failed'] == 0

# Test 20: bulk_update_embeddings with exceptions
print("✅ Test 20: Bulk update with exceptions")
with patch('django.db.models.Q') as mock_q:
    mock_model_class.objects.filter.return_value = mock_queryset
    
    # Mock exceptions
    def mock_update(instance):
        if instance.id == 2:
            raise Exception('Update failed')
        return True
    
    with patch.object(service, 'update_model_embedding', side_effect=mock_update):
        stats = service.bulk_update_embeddings(mock_model_class)
        assert stats['updated'] == 4
        assert stats['skipped'] == 0
        assert stats['failed'] == 1

# Test 21: Global service instance
print("✅ Test 21: Global service instance")
from ai_integration.services.embedding_service import embedding_service as global_service
assert isinstance(global_service, EmbeddingService)

print("\n" + "="*50)
print("All branch coverage tests passed!")
print("="*50)

# Stop coverage and report
if coverage_available:
    cov.stop()
    cov.save()
    print("\nCOVERAGE REPORT:")
    print("-" * 30)
    cov.report(show_missing=True)
    print("\nBRANCH COVERAGE DETAILS:")
    print("-" * 30)
    # Get detailed branch coverage
    analysis = cov.analysis2('ai_integration/services/embedding_service.py')
    print(f"Statements: {len(analysis[1]) + len(analysis[2])}")
    print(f"Missing statements: {len(analysis[2])}")
    print(f"Branches: {len(analysis[3])}")
    print(f"Missing branches: {len(analysis[4])}")
    if analysis[3]:
        branch_coverage = (len(analysis[3]) - len(analysis[4])) / len(analysis[3]) * 100
        print(f"Branch coverage: {branch_coverage:.1f}%")