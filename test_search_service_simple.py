#!/usr/bin/env python
"""
Simple comprehensive test for search service targeting 90% branch coverage
"""
import os
import sys

# Setup Django BEFORE any imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Start coverage before any imports
try:
    import coverage
    cov = coverage.Coverage(source=['ai_integration.services.search_service'], branch=True)
    cov.start()
    coverage_available = True
except ImportError:
    coverage_available = False

import django
django.setup()

from unittest.mock import Mock, patch, MagicMock
from ai_integration.services.search_service import SearchService, search_service

print("Testing SearchService with comprehensive branch coverage...")

# Test 1: Basic initialization and configuration
print("✅ Test 1: Basic initialization")
service = SearchService()
assert service.embedding_service is not None
assert len(service.SEARCHABLE_MODELS) == 4
assert 'story' in service.SEARCHABLE_MODELS
assert 'event' in service.SEARCHABLE_MODELS
assert 'heritage' in service.SEARCHABLE_MODELS
assert 'health' in service.SEARCHABLE_MODELS

# Test 2: semantic_search empty query branches
print("✅ Test 2: Empty query handling")
assert service.semantic_search('') == []
assert service.semantic_search('   ') == []
assert service.semantic_search(None) == []

# Test 3: semantic_search with embedding failure
print("✅ Test 3: Embedding generation failure")
with patch.object(service, 'embedding_service') as mock_embedding:
    mock_embedding.generate_embedding.return_value = None
    result = service.semantic_search('test query')
    assert result == []
    mock_embedding.generate_embedding.assert_called_once_with('test query')

# Test 4: semantic_search with successful embedding and empty model types
print("✅ Test 4: Successful embedding with default model types")
mock_embedding = [0.1, 0.2, 0.3] * 512
with patch.object(service, 'embedding_service') as mock_emb:
    mock_emb.generate_embedding.return_value = mock_embedding
    with patch.object(service, '_search_model', return_value=[]) as mock_search:
        result = service.semantic_search('test query')
        # Should call _search_model for all 4 default model types
        assert mock_search.call_count == 4

# Test 5: semantic_search with specific model types
print("✅ Test 5: Specific model types")
with patch.object(service, 'embedding_service') as mock_emb:
    mock_emb.generate_embedding.return_value = mock_embedding
    with patch.object(service, '_search_model', return_value=[]) as mock_search:
        result = service.semantic_search('test query', ['story', 'event'])
        assert mock_search.call_count == 2

# Test 6: semantic_search with unknown model type (branch coverage)
print("✅ Test 6: Unknown model type filtering")
with patch.object(service, 'embedding_service') as mock_emb:
    mock_emb.generate_embedding.return_value = mock_embedding
    with patch.object(service, '_search_model', return_value=[]) as mock_search:
        # Mix valid and invalid model types
        result = service.semantic_search('test query', ['story', 'unknown_type', 'event'])
        assert mock_search.call_count == 2  # Only valid types

# Test 7: semantic_search result sorting and limiting
print("✅ Test 7: Result sorting and limiting")
mock_results_1 = [
    {'content_type': 'story', 'similarity': 0.7, 'title': 'Story 1'},
    {'content_type': 'story', 'similarity': 0.6, 'title': 'Story 2'}
]
mock_results_2 = [
    {'content_type': 'event', 'similarity': 0.9, 'title': 'Event 1'},
    {'content_type': 'event', 'similarity': 0.8, 'title': 'Event 2'}
]

with patch.object(service, 'embedding_service') as mock_emb:
    mock_emb.generate_embedding.return_value = mock_embedding
    with patch.object(service, '_search_model', side_effect=[mock_results_1, mock_results_2]):
        result = service.semantic_search('test query', ['story', 'event'], limit=3)
        # Should be sorted by similarity (highest first) and limited to 3
        assert len(result) == 3
        assert result[0]['similarity'] == 0.9
        assert result[1]['similarity'] == 0.8
        assert result[2]['similarity'] == 0.7
        # Check content_type was added correctly
        assert all('content_type' in r for r in result)

# Test 8: _search_model exception handling
print("✅ Test 8: Search model exception handling")
mock_model = Mock()
mock_model.__name__ = 'MockModel'
mock_model.objects.filter.side_effect = Exception('Database error')
result = service._search_model(mock_model, mock_embedding, 10, 0.7)
assert result == []

# Test 9: _format_search_result for different model types
print("✅ Test 9: Format search results for all model types")

# Story formatting
mock_story = Mock()
mock_story.__class__.__name__ = 'Story'
mock_story.id = 1
mock_story.title = 'Test Story'
mock_story.content = 'A' * 250  # Long content for truncation
mock_story.story_type = 'childhood'
mock_story.date_occurred = None
# Mock people with proper name attributes
mock_people = [Mock(name='Alice'), Mock(name='Bob'), Mock(name='Charlie'), Mock(name='David')]
for person in mock_people:
    person.name = person.name  # Set the name attribute directly
mock_story.people.all.return_value = mock_people
mock_story.similarity = 0.85
mock_story.created_at.isoformat.return_value = '2024-01-01T00:00:00Z'

result = service._format_search_result(mock_story)
assert result['id'] == 1
assert result['title'] == 'Test Story'
assert len(result['content']) == 203  # 200 + '...'
assert '...' in result['content']
assert result['story_type'] == 'childhood'
assert result['date_occurred'] is None
assert len(result['people']) == 3  # Limited to 3
assert result['similarity'] == 0.85

# Event formatting with location
mock_event = Mock()
mock_event.__class__.__name__ = 'Event'
mock_event.id = 2
mock_event.name = 'Birthday Party'
mock_event.description = 'Great celebration'
mock_event.event_type = 'birthday'
mock_event.start_date.isoformat.return_value = '2024-01-01'
mock_event.location.name = 'Home'
mock_participants = [Mock(name='Alice'), Mock(name='Bob')]
for person in mock_participants:
    person.name = person.name
mock_event.participants.all.return_value = mock_participants
mock_event.similarity = 0.9
mock_event.created_at.isoformat.return_value = '2024-01-01T00:00:00Z'

result = service._format_search_result(mock_event)
assert result['location'] == 'Home'
assert len(result['participants']) == 2

# Event formatting without location and description (branch coverage)
mock_event_no_loc = Mock()
mock_event_no_loc.__class__.__name__ = 'Event'
mock_event_no_loc.id = 3
mock_event_no_loc.name = 'Simple Event'
mock_event_no_loc.description = None
mock_event_no_loc.event_type = 'meeting'
mock_event_no_loc.start_date.isoformat.return_value = '2024-01-01'
mock_event_no_loc.location = None
mock_event_no_loc.participants.all.return_value = []
mock_event_no_loc.similarity = 0.8
mock_event_no_loc.created_at.isoformat.return_value = '2024-01-01T00:00:00Z'

result = service._format_search_result(mock_event_no_loc)
assert result['location'] is None
assert result['content'] is None
assert result['participants'] == []

# Heritage formatting with origin person
mock_heritage = Mock()
mock_heritage.__class__.__name__ = 'Heritage'
mock_heritage.id = 4
mock_heritage.title = 'Family Recipe'
mock_heritage.description = 'Traditional recipe'
mock_heritage.heritage_type = 'recipe'
mock_heritage.importance = 'high'
mock_heritage.origin_person.name = 'Grandma'
mock_heritage.similarity = 0.75
mock_heritage.created_at.isoformat.return_value = '2024-01-01T00:00:00Z'

result = service._format_search_result(mock_heritage)
assert result['origin_person'] == 'Grandma'

# Heritage formatting without origin person (branch coverage)
mock_heritage_no_origin = Mock()
mock_heritage_no_origin.__class__.__name__ = 'Heritage'
mock_heritage_no_origin.id = 5
mock_heritage_no_origin.title = 'Family Recipe'
mock_heritage_no_origin.description = 'Traditional recipe'
mock_heritage_no_origin.heritage_type = 'recipe'
mock_heritage_no_origin.importance = 'high'
mock_heritage_no_origin.origin_person = None
mock_heritage_no_origin.similarity = 0.75
mock_heritage_no_origin.created_at.isoformat.return_value = '2024-01-01T00:00:00Z'

result = service._format_search_result(mock_heritage_no_origin)
assert result['origin_person'] is None

# Health formatting
mock_health = Mock()
mock_health.__class__.__name__ = 'Health'
mock_health.id = 6
mock_health.title = 'Checkup'
mock_health.description = 'Annual checkup'
mock_health.record_type = 'checkup'
mock_health.person.name = 'John'
mock_health.date.isoformat.return_value = '2024-01-01'
mock_health.is_hereditary = True
mock_health.similarity = 0.65
mock_health.created_at.isoformat.return_value = '2024-01-01T00:00:00Z'

result = service._format_search_result(mock_health)
assert result['person'] == 'John'
assert result['is_hereditary'] is True

# Generic formatting (unknown model type)
mock_unknown = Mock()
mock_unknown.__class__.__name__ = 'UnknownModel'
mock_unknown.id = 7
mock_unknown.similarity = 0.5
mock_unknown.created_at.isoformat.return_value = '2024-01-01T00:00:00Z'

# Mock str method properly
with patch.object(mock_unknown, '__str__', return_value='Unknown Object'):
    result = service._format_search_result(mock_unknown)
    assert result['title'] == 'Unknown Object'
    assert result['content'] == ''

# Generic formatting without created_at (branch coverage)
mock_no_created = Mock()
mock_no_created.__class__.__name__ = 'UnknownModel'
mock_no_created.id = 8
mock_no_created.similarity = 0.5
# Remove created_at attribute
if hasattr(mock_no_created, 'created_at'):
    delattr(mock_no_created, 'created_at')

with patch.object(mock_no_created, '__str__', return_value='No Created At'):
    result = service._format_search_result(mock_no_created)
    assert result['created_at'] is None

# Test 10: search_by_category with all valid categories
print("✅ Test 10: Search by category")
categories = [
    ('stories', 'story'),
    ('events', 'event'),
    ('heritage', 'heritage'),
    ('health', 'health'),
    ('memories', 'story'),  # Alias
    ('traditions', 'heritage'),  # Alias
    ('STORIES', 'story'),  # Case insensitive
]

for category, expected_type in categories:
    with patch.object(service, 'semantic_search', return_value=[]) as mock_search:
        result = service.search_by_category('test', category)
        mock_search.assert_called_once_with('test', [expected_type], 10)

# Search by category with invalid category
result = service.search_by_category('test', 'invalid_category')
assert result == []

# Test 11: find_related_content branches
print("✅ Test 11: Find related content")

# Invalid content type
result = service.find_related_content(1, 'invalid_type')
assert result == []

# Valid content type but object not found
with patch('ai_integration.services.search_service.Story') as mock_story_class:
    mock_story_class.objects.get.side_effect = Exception('Not found')
    result = service.find_related_content(1, 'story')
    assert result == []

# Valid object but no embedding
mock_ref_obj = Mock()
mock_ref_obj.content_embedding = None
with patch('ai_integration.services.search_service.Story') as mock_story_class:
    mock_story_class.objects.get.return_value = mock_ref_obj
    result = service.find_related_content(1, 'story')
    assert result == []

# Test 12: keyword_search branches
print("✅ Test 12: Keyword search")

# Test with all default model types
with patch.object(service.SEARCHABLE_MODELS['story'].objects, 'filter', return_value=[]):
    with patch.object(service.SEARCHABLE_MODELS['event'].objects, 'filter', return_value=[]):
        with patch.object(service.SEARCHABLE_MODELS['heritage'].objects, 'filter', return_value=[]):
            with patch.object(service.SEARCHABLE_MODELS['health'].objects, 'filter', return_value=[]):
                result = service.keyword_search('test')
                assert isinstance(result, list)

# Test with specific model types
with patch.object(service.SEARCHABLE_MODELS['story'].objects, 'filter', return_value=[]):
    result = service.keyword_search('test', ['story'])
    assert isinstance(result, list)

# Test with unknown model type (should be skipped)
result = service.keyword_search('test', ['unknown_type'])
assert result == []

# Test query building for each model type
for model_type in ['story', 'event', 'heritage', 'health']:
    with patch.object(service.SEARCHABLE_MODELS[model_type].objects, 'filter', return_value=[]):
        service.keyword_search('test', [model_type])

# Test 13: Global service instance
print("✅ Test 13: Global service instance")
from ai_integration.services.search_service import search_service as global_service
assert isinstance(global_service, SearchService)

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
    analysis = cov.analysis2('ai_integration/services/search_service.py')
    print(f"Statements: {len(analysis[1]) + len(analysis[2])}")
    print(f"Missing statements: {len(analysis[2])}")
    print(f"Branches: {len(analysis[3])}")
    print(f"Missing branches: {len(analysis[4])}")
    if analysis[3]:
        branch_coverage = (len(analysis[3]) - len(analysis[4])) / len(analysis[3]) * 100
        print(f"Branch coverage: {branch_coverage:.1f}%")