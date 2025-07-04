"""
Comprehensive tests for AI integration views targeting 90%+ branch coverage
"""
import pytest
import json
from unittest.mock import Mock, patch
from django.test import RequestFactory
from django.http import JsonResponse
from ai_integration.views import chat_endpoint, semantic_search


class TestChatEndpoint:
    """Comprehensive tests for chat_endpoint view"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.factory = RequestFactory()
        self.mock_rag_response = {
            'query': 'test query',
            'response': 'test response',
            'sources': [],
            'metadata': {
                'query_type': 'general',
                'confidence': 0.8,
                'processing_time': 1.0
            }
        }
    
    @patch('ai_integration.views.rag_service')
    @patch('ai_integration.views.ChatSession')
    @patch('ai_integration.views.QueryLog')
    def test_valid_request_with_session(self, mock_query_log, mock_chat_session, mock_rag):
        """Test chat endpoint with valid request and session ID"""
        mock_rag.generate_response.return_value = self.mock_rag_response
        mock_session = Mock()
        mock_chat_session.objects.get.return_value = mock_session
        
        request_data = {
            'query': 'test query',
            'session_id': 'test-session-123'
        }
        request = self.factory.post('/chat/', 
                                   data=json.dumps(request_data),
                                   content_type='application/json')
        
        response = chat_endpoint(request)
        assert isinstance(response, JsonResponse)
        data = json.loads(response.content)
        assert data['query'] == 'test query'
        assert data['response'] == 'test response'
        
        # Verify service calls
        mock_rag.generate_response.assert_called_once_with('test query')
        mock_chat_session.objects.get.assert_called_once_with(session_id='test-session-123')
        mock_query_log.objects.create.assert_called_once()
    
    @patch('ai_integration.views.rag_service')
    @patch('ai_integration.views.ChatSession')
    @patch('ai_integration.views.QueryLog')
    def test_valid_request_without_session(self, mock_query_log, mock_chat_session, mock_rag):
        """Test chat endpoint with valid request but no session ID"""
        mock_rag.generate_response.return_value = self.mock_rag_response
        
        request_data = {
            'query': 'test query without session'
        }
        request = self.factory.post('/chat/', 
                                   data=json.dumps(request_data),
                                   content_type='application/json')
        
        response = chat_endpoint(request)
        assert isinstance(response, JsonResponse)
        data = json.loads(response.content)
        assert data['query'] == 'test query'
        
        # Verify no session operations
        mock_chat_session.objects.get.assert_not_called()
        mock_query_log.objects.create.assert_not_called()
    
    def test_empty_query(self):
        """Test chat endpoint with empty query"""
        request_data = {'query': ''}
        request = self.factory.post('/chat/', 
                                   data=json.dumps(request_data),
                                   content_type='application/json')
        
        response = chat_endpoint(request)
        assert isinstance(response, JsonResponse)
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['error'] == 'Query cannot be empty'
    
    def test_whitespace_only_query(self):
        """Test chat endpoint with whitespace-only query"""
        request_data = {'query': '   \n\t  '}
        request = self.factory.post('/chat/', 
                                   data=json.dumps(request_data),
                                   content_type='application/json')
        
        response = chat_endpoint(request)
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['error'] == 'Query cannot be empty'
    
    @patch('ai_integration.views.rag_service')
    @patch('ai_integration.views.ChatSession')
    @patch('ai_integration.views.QueryLog')
    @patch('ai_integration.views.logger')
    def test_session_not_found(self, mock_logger, mock_query_log, mock_chat_session, mock_rag):
        """Test chat endpoint when session is not found"""
        mock_rag.generate_response.return_value = self.mock_rag_response
        mock_chat_session.DoesNotExist = Exception
        mock_chat_session.objects.get.side_effect = mock_chat_session.DoesNotExist()
        
        request_data = {
            'query': 'test query',
            'session_id': 'non-existent-session'
        }
        request = self.factory.post('/chat/', 
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
    
    def test_invalid_json(self):
        """Test chat endpoint with invalid JSON"""
        request = self.factory.post('/chat/', 
                                   data='invalid json data',
                                   content_type='application/json')
        
        response = chat_endpoint(request)
        assert response.status_code == 500
        data = json.loads(response.content)
        assert 'error' in data
    
    @patch('ai_integration.views.rag_service')
    @patch('ai_integration.views.logger')
    def test_rag_service_exception(self, mock_logger, mock_rag):
        """Test chat endpoint when RAG service raises exception"""
        mock_rag.generate_response.side_effect = Exception('RAG service error')
        
        request_data = {'query': 'test query'}
        request = self.factory.post('/chat/', 
                                   data=json.dumps(request_data),
                                   content_type='application/json')
        
        response = chat_endpoint(request)
        assert response.status_code == 500
        data = json.loads(response.content)
        assert 'error' in data
        
        # Verify error was logged
        mock_logger.error.assert_called_once()
    
    def test_empty_session_id_string(self):
        """Test chat endpoint with empty session_id string"""
        with patch('ai_integration.views.rag_service') as mock_rag:
            with patch('ai_integration.views.ChatSession') as mock_chat_session:
                mock_rag.generate_response.return_value = self.mock_rag_response
                
                request_data = {
                    'query': 'test query',
                    'session_id': ''  # Empty session_id should be treated as no session
                }
                request = self.factory.post('/chat/', 
                                           data=json.dumps(request_data),
                                           content_type='application/json')
                
                response = chat_endpoint(request)
                data = json.loads(response.content)
                assert data['query'] == 'test query'
                
                # Should not attempt session lookup with empty session_id
                mock_chat_session.objects.get.assert_not_called()
    
    def test_missing_query_field(self):
        """Test chat endpoint with missing query field entirely"""
        request_data = {'session_id': 'test'}
        request = self.factory.post('/chat/', 
                                   data=json.dumps(request_data),
                                   content_type='application/json')
        
        response = chat_endpoint(request)
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['error'] == 'Query cannot be empty'


class TestSemanticSearch:
    """Comprehensive tests for semantic_search view"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.factory = RequestFactory()
        self.mock_search_results = [
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
    
    @patch('ai_integration.views.search_service')
    def test_valid_request_with_all_parameters(self, mock_search):
        """Test semantic search with all parameters specified"""
        mock_search.semantic_search.return_value = self.mock_search_results
        
        request_data = {
            'query': 'test search query',
            'limit': 5,
            'threshold': 0.7
        }
        request = self.factory.post('/search/', 
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
    
    @patch('ai_integration.views.search_service')
    def test_valid_request_with_defaults(self, mock_search):
        """Test semantic search with default parameters"""
        mock_search.semantic_search.return_value = []
        
        request_data = {
            'query': 'test search query'
            # No limit or threshold specified
        }
        request = self.factory.post('/search/', 
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
    
    def test_empty_query(self):
        """Test semantic search with empty query"""
        request_data = {'query': ''}
        request = self.factory.post('/search/', 
                                   data=json.dumps(request_data),
                                   content_type='application/json')
        
        response = semantic_search(request)
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['error'] == 'Query cannot be empty'
    
    def test_whitespace_only_query(self):
        """Test semantic search with whitespace-only query"""
        request_data = {'query': '   \t\n   '}
        request = self.factory.post('/search/', 
                                   data=json.dumps(request_data),
                                   content_type='application/json')
        
        response = semantic_search(request)
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['error'] == 'Query cannot be empty'
    
    def test_invalid_json(self):
        """Test semantic search with invalid JSON"""
        request = self.factory.post('/search/', 
                                   data='invalid json data',
                                   content_type='application/json')
        
        response = semantic_search(request)
        assert response.status_code == 500
        data = json.loads(response.content)
        assert 'error' in data
    
    @patch('ai_integration.views.search_service')
    @patch('ai_integration.views.logger')
    def test_search_service_exception(self, mock_logger, mock_search):
        """Test semantic search when search service raises exception"""
        mock_search.semantic_search.side_effect = Exception('Search service error')
        
        request_data = {'query': 'test query'}
        request = self.factory.post('/search/', 
                                   data=json.dumps(request_data),
                                   content_type='application/json')
        
        response = semantic_search(request)
        assert response.status_code == 500
        data = json.loads(response.content)
        assert 'error' in data
        
        # Verify error was logged
        mock_logger.error.assert_called_once()
    
    @patch('ai_integration.views.search_service')
    def test_edge_case_parameter_values(self, mock_search):
        """Test semantic search with edge case parameter values"""
        mock_search.semantic_search.return_value = []
        
        # Test with edge case values
        request_data = {
            'query': 'test',
            'limit': 0,
            'threshold': 1.0
        }
        request = self.factory.post('/search/', 
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
    
    @patch('ai_integration.views.search_service')
    def test_missing_query_field(self, mock_search):
        """Test semantic search with missing query field"""
        request_data = {'limit': 5}  # No query field
        request = self.factory.post('/search/', 
                                   data=json.dumps(request_data),
                                   content_type='application/json')
        
        response = semantic_search(request)
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['error'] == 'Query cannot be empty'


class TestViewsIntegration:
    """Integration tests for AI views"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.factory = RequestFactory()
    
    @patch('ai_integration.views.rag_service')
    @patch('ai_integration.views.search_service')
    def test_both_endpoints_return_json(self, mock_search, mock_rag):
        """Test that both endpoints return JsonResponse objects"""
        # Setup mocks
        mock_rag.generate_response.return_value = {
            'query': 'test',
            'response': 'response',
            'sources': [],
            'metadata': {}
        }
        mock_search.semantic_search.return_value = []
        
        # Test chat endpoint
        chat_request = self.factory.post('/chat/', 
                                        data=json.dumps({'query': 'test'}),
                                        content_type='application/json')
        chat_response = chat_endpoint(chat_request)
        assert isinstance(chat_response, JsonResponse)
        
        # Test search endpoint
        search_request = self.factory.post('/search/', 
                                          data=json.dumps({'query': 'test'}),
                                          content_type='application/json')
        search_response = semantic_search(search_request)
        assert isinstance(search_response, JsonResponse)
    
    def test_error_response_consistency(self):
        """Test that error responses have consistent structure"""
        # Test chat endpoint error
        chat_request = self.factory.post('/chat/', 
                                        data='invalid json',
                                        content_type='application/json')
        chat_response = chat_endpoint(chat_request)
        chat_data = json.loads(chat_response.content)
        assert 'error' in chat_data
        
        # Test search endpoint error
        search_request = self.factory.post('/search/', 
                                          data='invalid json',
                                          content_type='application/json')
        search_response = semantic_search(search_request)
        search_data = json.loads(search_response.content)
        assert 'error' in search_data