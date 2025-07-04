#!/usr/bin/env python
"""
Comprehensive test for AI integration views targeting 90%+ branch coverage
"""
import os
import sys

# Setup Django BEFORE any imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Start coverage before any imports
try:
    import coverage
    cov = coverage.Coverage(source=['ai_integration.views'], branch=True)
    cov.start()
    coverage_available = True
except ImportError:
    coverage_available = False

import django
django.setup()

from unittest.mock import Mock, patch
from django.test import RequestFactory
from django.http import JsonResponse
import json
from ai_integration.views import chat_endpoint, semantic_search

print("Testing AI integration views with comprehensive branch coverage...")

factory = RequestFactory()

# Test 1: chat_endpoint - valid request with all data
print("✅ Test 1: chat_endpoint valid request with session")

mock_rag_response = {
    'query': 'test query',
    'response': 'test response',
    'sources': [],
    'metadata': {
        'query_type': 'general',
        'confidence': 0.8,
        'processing_time': 1.0
    }
}

with patch('ai_integration.views.rag_service') as mock_rag:
    with patch('ai_integration.views.ChatSession') as mock_chat_session:
        with patch('ai_integration.views.QueryLog') as mock_query_log:
            mock_rag.generate_response.return_value = mock_rag_response
            mock_session = Mock()
            mock_chat_session.objects.get.return_value = mock_session
            
            request_data = {
                'query': 'test query',
                'session_id': 'test-session-123'
            }
            request = factory.post('/chat/', 
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            response = chat_endpoint(request)
            assert isinstance(response, JsonResponse)
            data = json.loads(response.content)
            assert data['query'] == 'test query'
            assert data['response'] == 'test response'
            
            # Verify RAG service was called
            mock_rag.generate_response.assert_called_once_with('test query')
            
            # Verify session lookup and query log creation
            mock_chat_session.objects.get.assert_called_once_with(session_id='test-session-123')
            mock_query_log.objects.create.assert_called_once()

# Test 2: chat_endpoint - valid request without session_id
print("✅ Test 2: chat_endpoint valid request without session")

with patch('ai_integration.views.rag_service') as mock_rag:
    with patch('ai_integration.views.ChatSession') as mock_chat_session:
        with patch('ai_integration.views.QueryLog') as mock_query_log:
            mock_rag.generate_response.return_value = mock_rag_response
            
            request_data = {
                'query': 'test query without session'
            }
            request = factory.post('/chat/', 
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            response = chat_endpoint(request)
            assert isinstance(response, JsonResponse)
            data = json.loads(response.content)
            assert data['query'] == 'test query'
            
            # Verify no session operations
            mock_chat_session.objects.get.assert_not_called()
            mock_query_log.objects.create.assert_not_called()

# Test 3: chat_endpoint - empty query
print("✅ Test 3: chat_endpoint empty query")

request_data = {'query': ''}
request = factory.post('/chat/', 
                     data=json.dumps(request_data),
                     content_type='application/json')

response = chat_endpoint(request)
assert isinstance(response, JsonResponse)
assert response.status_code == 400
data = json.loads(response.content)
assert data['error'] == 'Query cannot be empty'

# Test 4: chat_endpoint - whitespace-only query
print("✅ Test 4: chat_endpoint whitespace-only query")

request_data = {'query': '   \n\t  '}
request = factory.post('/chat/', 
                     data=json.dumps(request_data),
                     content_type='application/json')

response = chat_endpoint(request)
assert response.status_code == 400
data = json.loads(response.content)
assert data['error'] == 'Query cannot be empty'

# Test 5: chat_endpoint - session not found
print("✅ Test 5: chat_endpoint session not found")

with patch('ai_integration.views.rag_service') as mock_rag:
    with patch('ai_integration.views.ChatSession') as mock_chat_session:
        with patch('ai_integration.views.QueryLog') as mock_query_log:
            with patch('ai_integration.views.logger') as mock_logger:
                mock_rag.generate_response.return_value = mock_rag_response
                mock_chat_session.DoesNotExist = Exception
                mock_chat_session.objects.get.side_effect = mock_chat_session.DoesNotExist()
                
                request_data = {
                    'query': 'test query',
                    'session_id': 'non-existent-session'
                }
                request = factory.post('/chat/', 
                                     data=json.dumps(request_data),
                                     content_type='application/json')
                
                response = chat_endpoint(request)
                assert isinstance(response, JsonResponse)
                data = json.loads(response.content)
                assert data['query'] == 'test query'
                
                # Verify warning was logged
                mock_logger.warning.assert_called_once()
                assert 'non-existent-session' in str(mock_logger.warning.call_args)
                
                # Verify no query log was created
                mock_query_log.objects.create.assert_not_called()

# Test 6: chat_endpoint - invalid JSON
print("✅ Test 6: chat_endpoint invalid JSON")

request = factory.post('/chat/', 
                     data='invalid json data',
                     content_type='application/json')

response = chat_endpoint(request)
assert response.status_code == 500
data = json.loads(response.content)
assert 'error' in data

# Test 7: chat_endpoint - RAG service exception
print("✅ Test 7: chat_endpoint RAG service exception")

with patch('ai_integration.views.rag_service') as mock_rag:
    with patch('ai_integration.views.logger') as mock_logger:
        mock_rag.generate_response.side_effect = Exception('RAG service error')
        
        request_data = {'query': 'test query'}
        request = factory.post('/chat/', 
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        response = chat_endpoint(request)
        assert response.status_code == 500
        data = json.loads(response.content)
        assert 'error' in data
        
        # Verify error was logged
        mock_logger.error.assert_called_once()

# Test 8: semantic_search - valid request
print("✅ Test 8: semantic_search valid request")

mock_search_results = [
    {
        'id': 1,
        'title': 'Test Result',
        'content': 'Test content',
        'similarity': 0.9
    },
    {
        'id': 2,
        'title': 'Another Result',
        'content': 'More content',
        'similarity': 0.8
    }
]

with patch('ai_integration.views.search_service') as mock_search:
    mock_search.semantic_search.return_value = mock_search_results
    
    request_data = {
        'query': 'test search query',
        'limit': 5,
        'threshold': 0.7
    }
    request = factory.post('/search/', 
                         data=json.dumps(request_data),
                         content_type='application/json')
    
    response = semantic_search(request)
    assert isinstance(response, JsonResponse)
    data = json.loads(response.content)
    assert data['query'] == 'test search query'
    assert data['count'] == 2
    assert data['threshold'] == 0.7
    assert len(data['results']) == 2
    
    # Verify search service was called with correct parameters
    mock_search.semantic_search.assert_called_once_with(
        query='test search query',
        limit=5,
        similarity_threshold=0.7
    )

# Test 9: semantic_search - valid request with defaults
print("✅ Test 9: semantic_search with default parameters")

with patch('ai_integration.views.search_service') as mock_search:
    mock_search.semantic_search.return_value = []
    
    request_data = {
        'query': 'test search query'
        # No limit or threshold specified
    }
    request = factory.post('/search/', 
                         data=json.dumps(request_data),
                         content_type='application/json')
    
    response = semantic_search(request)
    data = json.loads(response.content)
    assert data['query'] == 'test search query'
    assert data['count'] == 0
    assert data['threshold'] == 0.6  # Default threshold
    
    # Verify default parameters were used
    mock_search.semantic_search.assert_called_once_with(
        query='test search query',
        limit=10,  # Default limit
        similarity_threshold=0.6  # Default threshold
    )

# Test 10: semantic_search - empty query
print("✅ Test 10: semantic_search empty query")

request_data = {'query': ''}
request = factory.post('/search/', 
                     data=json.dumps(request_data),
                     content_type='application/json')

response = semantic_search(request)
assert response.status_code == 400
data = json.loads(response.content)
assert data['error'] == 'Query cannot be empty'

# Test 11: semantic_search - whitespace-only query
print("✅ Test 11: semantic_search whitespace-only query")

request_data = {'query': '   \t\n   '}
request = factory.post('/search/', 
                     data=json.dumps(request_data),
                     content_type='application/json')

response = semantic_search(request)
assert response.status_code == 400
data = json.loads(response.content)
assert data['error'] == 'Query cannot be empty'

# Test 12: semantic_search - invalid JSON
print("✅ Test 12: semantic_search invalid JSON")

request = factory.post('/search/', 
                     data='invalid json data',
                     content_type='application/json')

response = semantic_search(request)
assert response.status_code == 500
data = json.loads(response.content)
assert 'error' in data

# Test 13: semantic_search - search service exception
print("✅ Test 13: semantic_search service exception")

with patch('ai_integration.views.search_service') as mock_search:
    with patch('ai_integration.views.logger') as mock_logger:
        mock_search.semantic_search.side_effect = Exception('Search service error')
        
        request_data = {'query': 'test query'}
        request = factory.post('/search/', 
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        response = semantic_search(request)
        assert response.status_code == 500
        data = json.loads(response.content)
        assert 'error' in data
        
        # Verify error was logged
        mock_logger.error.assert_called_once()

# Test 14: Edge cases - special parameter values
print("✅ Test 14: semantic_search special parameter values")

with patch('ai_integration.views.search_service') as mock_search:
    mock_search.semantic_search.return_value = []
    
    # Test with edge case values
    request_data = {
        'query': 'test',
        'limit': 0,
        'threshold': 1.0
    }
    request = factory.post('/search/', 
                         data=json.dumps(request_data),
                         content_type='application/json')
    
    response = semantic_search(request)
    data = json.loads(response.content)
    assert data['threshold'] == 1.0
    
    mock_search.semantic_search.assert_called_once_with(
        query='test',
        limit=0,
        similarity_threshold=1.0
    )

# Test 15: chat_endpoint - empty session_id string
print("✅ Test 15: chat_endpoint empty session_id")

with patch('ai_integration.views.rag_service') as mock_rag:
    with patch('ai_integration.views.ChatSession') as mock_chat_session:
        mock_rag.generate_response.return_value = mock_rag_response
        
        request_data = {
            'query': 'test query',
            'session_id': ''  # Empty session_id should be treated as no session
        }
        request = factory.post('/chat/', 
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        response = chat_endpoint(request)
        data = json.loads(response.content)
        assert data['query'] == 'test query'
        
        # Should not attempt session lookup with empty session_id
        mock_chat_session.objects.get.assert_not_called()

# Test 16: Request body edge cases
print("✅ Test 16: Request body edge cases")

# Test with missing query field entirely
request_data = {'session_id': 'test'}
request = factory.post('/chat/', 
                     data=json.dumps(request_data),
                     content_type='application/json')

response = chat_endpoint(request)
assert response.status_code == 400
data = json.loads(response.content)
assert data['error'] == 'Query cannot be empty'

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
    analysis = cov.analysis2('ai_integration/views.py')
    print(f"Statements: {len(analysis[1]) + len(analysis[2])}")
    print(f"Missing statements: {len(analysis[2])}")
    print(f"Branches: {len(analysis[3])}")
    print(f"Missing branches: {len(analysis[4])}")
    if analysis[3]:
        branch_coverage = (len(analysis[3]) - len(analysis[4])) / len(analysis[3]) * 100
        print(f"Branch coverage: {branch_coverage:.1f}%")