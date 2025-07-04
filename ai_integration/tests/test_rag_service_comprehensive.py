"""
Comprehensive tests for RAG service targeting 90%+ branch coverage
Converted from test_rag_service_runner.py to proper pytest format
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import time
from ai_integration.services.rag_service import RAGService, rag_service


class TestRAGService:
    """Comprehensive tests for RAG service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.rag_service = RAGService()
        
    def test_init(self):
        """Test RAGService initialization"""
        service = RAGService()
        assert service.search_service is not None
        assert service.embedding_service is not None
        assert service.anthropic_client is not None
        
    def test_classify_query_health(self):
        """Test health query classification"""
        health_queries = [
            "What health conditions run in our family?",
            "Are there any genetic diseases?",
            "家族有什么健康问题吗？",
            "hereditary illness patterns"
        ]
        
        for query in health_queries:
            result = self.rag_service._classify_query(query)
            assert result == 'health_pattern'
    
    def test_classify_query_event(self):
        """Test event query classification"""
        event_queries = [
            "How do we celebrate birthdays?",
            "What was the wedding like?",
            "计划家庭聚会",
            "family reunion party"
        ]
        
        for query in event_queries:
            result = self.rag_service._classify_query(query)
            assert result == 'event_planning'
    
    def test_classify_query_heritage(self):
        """Test heritage query classification"""
        heritage_queries = [
            "What are our family traditions?",
            "Tell me about family recipes",
            "家族传统文化",
            "family values and wisdom"
        ]
        
        for query in heritage_queries:
            result = self.rag_service._classify_query(query)
            assert result == 'cultural_heritage'
    
    def test_classify_query_relationship(self):
        """Test relationship query classification"""
        relationship_queries = [
            "Who are my relatives?",
            "How are we related?",
            "家人关系",
            "family relationship tree"
        ]
        
        for query in relationship_queries:
            result = self.rag_service._classify_query(query)
            assert result == 'relationship_discovery'
    
    def test_classify_query_memory(self):
        """Test memory query classification"""
        memory_queries = [
            "Tell me old stories",
            "What do you remember about childhood?",
            "童年回忆",
            "past memories"
        ]
        
        for query in memory_queries:
            result = self.rag_service._classify_query(query)
            assert result == 'memory_discovery'
    
    def test_classify_query_general(self):
        """Test general query classification"""
        general_queries = [
            "How are things going?",
            "What's the weather like?",
            "Random question",
            "Test query"
        ]
        
        for query in general_queries:
            result = self.rag_service._classify_query(query)
            assert result == 'general'
    
    def test_detect_language_chinese(self):
        """Test Chinese language detection"""
        chinese_queries = [
            "你好，家庭助手",
            "这是中文查询",
            "家族传统文化",
            "我想了解健康状况"
        ]
        
        for query in chinese_queries:
            result = self.rag_service._detect_language(query)
            assert result == 'zh-CN'
    
    def test_detect_language_english(self):
        """Test English language detection"""
        english_queries = [
            "Hello family assistant",
            "This is an English query",
            "Family traditions",
            "Tell me about health"
        ]
        
        for query in english_queries:
            result = self.rag_service._detect_language(query)
            assert result == 'en-US'
    
    def test_calculate_confidence_empty(self):
        """Test confidence calculation with empty results"""
        result = self.rag_service._calculate_confidence([])
        assert result == 0.0
    
    def test_calculate_confidence_single_result(self):
        """Test confidence calculation with single result"""
        search_results = [{'similarity': 0.8}]
        result = self.rag_service._calculate_confidence(search_results)
        assert result > 0.8
        assert result <= 1.0
    
    def test_calculate_confidence_multiple_results(self):
        """Test confidence calculation with multiple results"""
        search_results = [
            {'similarity': 0.9},
            {'similarity': 0.8},
            {'similarity': 0.7}
        ]
        result = self.rag_service._calculate_confidence(search_results)
        assert result > 0.8
        assert result <= 1.0
    
    def test_build_context_empty(self):
        """Test context building with empty results"""
        result = self.rag_service._build_context([], 'general')
        assert result == ""
    
    def test_build_context_story(self):
        """Test context building with story results"""
        search_results = [
            {
                'content_type': 'story',
                'title': 'Family Reunion',
                'content': 'We had a great family reunion last year.',
                'similarity': 0.9,
                'people': ['John', 'Mary', 'Bob']
            }
        ]
        
        result = self.rag_service._build_context(search_results, 'memory_discovery')
        assert 'Family Story' in result
        assert 'Family Reunion' in result
        assert 'great family reunion' in result
        assert 'People involved' in result
        assert 'John, Mary, Bob' in result
    
    def test_build_context_event(self):
        """Test context building with event results"""
        search_results = [
            {
                'content_type': 'event',
                'title': 'Birthday Party',
                'content': 'Celebrated 50th birthday',
                'similarity': 0.8,
                'event_type': 'birthday',
                'location': 'Home'
            }
        ]
        
        result = self.rag_service._build_context(search_results, 'event_planning')
        assert 'Family Event' in result
        assert 'Birthday Party' in result
        assert 'Type: birthday' in result
        assert 'Location: Home' in result
    
    def test_build_context_heritage(self):
        """Test context building with heritage results"""
        search_results = [
            {
                'content_type': 'heritage',
                'title': 'Family Recipe',
                'content': 'Traditional dumpling recipe',
                'similarity': 0.85,
                'heritage_type': 'recipe',
                'origin_person': 'Grandma'
            }
        ]
        
        result = self.rag_service._build_context(search_results, 'cultural_heritage')
        assert 'Family Heritage' in result
        assert 'Family Recipe' in result
        assert 'Type: recipe' in result
        assert 'Origin: Grandma' in result
    
    def test_build_context_health(self):
        """Test context building with health results"""
        search_results = [
            {
                'content_type': 'health',
                'title': 'Health Record',
                'content': 'Regular checkup results',
                'similarity': 0.75,
                'person': 'John Doe',
                'is_hereditary': True
            }
        ]
        
        result = self.rag_service._build_context(search_results, 'health_pattern')
        assert 'Health Record' in result
        assert 'Person: John Doe' in result
        assert 'Hereditary: Yes' in result
    
    def test_format_sources_empty(self):
        """Test source formatting with empty results"""
        result = self.rag_service._format_sources([])
        assert result == []
    
    def test_format_sources_story(self):
        """Test source formatting with story results"""
        search_results = [
            {
                'content_type': 'story',
                'id': 1,
                'title': 'Family Story',
                'similarity': 0.9,
                'story_type': 'childhood',
                'people': ['Alice', 'Bob', 'Charlie']
            }
        ]
        
        result = self.rag_service._format_sources(search_results)
        assert len(result) == 1
        assert result[0]['type'] == 'story'
        assert result[0]['id'] == 1
        assert result[0]['title'] == 'Family Story'
        assert result[0]['relevance'] == 0.9
        assert result[0]['story_type'] == 'childhood'
        assert result[0]['people'] == ['Alice', 'Bob']  # Limited to 2
    
    def test_format_sources_event(self):
        """Test source formatting with event results"""
        search_results = [
            {
                'content_type': 'event',
                'id': 2,
                'title': 'Birthday Party',
                'similarity': 0.8,
                'event_type': 'birthday',
                'start_date': '2024-01-01'
            }
        ]
        
        result = self.rag_service._format_sources(search_results)
        assert len(result) == 1
        assert result[0]['type'] == 'event'
        assert result[0]['event_type'] == 'birthday'
        assert result[0]['date'] == '2024-01-01'
    
    def test_get_system_prompt(self):
        """Test system prompt generation"""
        query_types = [
            'memory_discovery',
            'health_pattern',
            'event_planning',
            'cultural_heritage',
            'relationship_discovery',
            'general'
        ]
        
        for query_type in query_types:
            result = self.rag_service._get_system_prompt(query_type)
            assert isinstance(result, str)
            assert 'family knowledge keeper' in result
            assert len(result) > 100
    
    def test_generate_fallback_response_english(self):
        """Test fallback response generation in English"""
        query_types = [
            'memory_discovery',
            'health_pattern',
            'event_planning',
            'cultural_heritage',
            'relationship_discovery',
            'general'
        ]
        
        for query_type in query_types:
            result = self.rag_service._generate_fallback_response('English query', query_type)
            assert isinstance(result, str)
            assert len(result) > 50
            assert '很抱歉' not in result  # Should not contain Chinese
    
    def test_generate_fallback_response_chinese(self):
        """Test fallback response generation in Chinese"""
        query_types = [
            'memory_discovery',
            'health_pattern',
            'event_planning',
            'cultural_heritage',
            'relationship_discovery',
            'general'
        ]
        
        for query_type in query_types:
            result = self.rag_service._generate_fallback_response('中文查询', query_type)
            assert isinstance(result, str)
            assert len(result) > 50
            # Check for Chinese characters instead of specific text
            chinese_chars = sum(1 for char in result if '\u4e00' <= char <= '\u9fff')
            assert chinese_chars > 0  # Should contain Chinese
    
    def test_generate_error_response_english(self):
        """Test error response generation in English"""
        result = self.rag_service._generate_error_response('English query', 'Test error')
        
        assert isinstance(result, dict)
        assert 'query' in result
        assert 'response' in result
        assert 'sources' in result
        assert 'metadata' in result
        assert result['query'] == 'English query'
        assert result['metadata']['query_type'] == 'error'
        assert result['metadata']['confidence'] == 0.0
        assert result['metadata']['language'] == 'en-US'
        assert result['metadata']['error'] == 'Test error'
    
    def test_generate_error_response_chinese(self):
        """Test error response generation in Chinese"""
        result = self.rag_service._generate_error_response('中文查询', 'Test error')
        
        assert isinstance(result, dict)
        assert result['query'] == '中文查询'
        assert result['metadata']['language'] == 'zh-CN'
        assert '技术问题' in result['response']
    
    @patch('ai_integration.services.rag_service.search_service')
    @patch('ai_integration.services.rag_service.time.time')
    def test_generate_response_with_results(self, mock_time, mock_search_service):
        """Test response generation with search results"""
        # Mock time
        mock_time.side_effect = [0.0, 1.5]
        
        # Mock search results
        mock_search_results = [
            {
                'content_type': 'story',
                'title': 'Family Story',
                'content': 'A wonderful family story',
                'similarity': 0.9,
                'people': ['Alice', 'Bob']
            }
        ]
        mock_search_service.semantic_search.return_value = mock_search_results
        
        # Mock AI response
        with patch.object(self.rag_service, '_generate_ai_response', return_value='AI generated response'):
            result = self.rag_service.generate_response('Tell me family stories')
            
            assert isinstance(result, dict)
            assert 'query' in result
            assert 'response' in result
            assert 'sources' in result
            assert 'metadata' in result
            assert result['query'] == 'Tell me family stories'
            assert result['response'] == 'AI generated response'
            assert result['metadata']['query_type'] == 'memory_discovery'
            assert result['metadata']['processing_time'] == 1.5
            assert result['metadata']['sources_count'] == 1
    
    @patch('ai_integration.services.rag_service.search_service')
    def test_generate_response_no_results(self, mock_search_service):
        """Test response generation with no search results"""
        # Mock empty search results
        mock_search_service.semantic_search.return_value = []
        
        result = self.rag_service.generate_response('Random query')
        
        assert isinstance(result, dict)
        assert 'query' in result
        assert 'response' in result
        assert 'sources' in result
        assert 'metadata' in result
        assert result['metadata']['sources_count'] == 0
        assert "couldn't find" in result['response']
    
    @patch('ai_integration.services.rag_service.search_service')
    def test_generate_response_exception(self, mock_search_service):
        """Test response generation with exception"""
        # Mock exception in search
        mock_search_service.semantic_search.side_effect = Exception('Search failed')
        
        result = self.rag_service.generate_response('Test query')
        
        assert isinstance(result, dict)
        assert result['metadata']['query_type'] == 'error'
        assert result['metadata']['confidence'] == 0.0
        assert 'error' in result['metadata']
    
    def test_generate_ai_response_success(self):
        """Test AI response generation success"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = 'AI generated response'
        
        with patch.object(self.rag_service, 'anthropic_client') as mock_anthropic_client:
            mock_anthropic_client.messages.create.return_value = mock_response
            
            result = self.rag_service._generate_ai_response(
                'Test query',
                'Test context',
                'general'
            )
            
            assert result == 'AI generated response'
            mock_anthropic_client.messages.create.assert_called_once()
    
    def test_generate_ai_response_failure(self):
        """Test AI response generation failure"""
        # Mock API failure
        with patch.object(self.rag_service, 'anthropic_client') as mock_anthropic_client:
            mock_anthropic_client.messages.create.side_effect = Exception('API Error')
            
            result = self.rag_service._generate_ai_response(
                'Test query',
                'Test context',
                'general'
            )
            
            # Should return fallback response
            assert isinstance(result, str)
            assert "couldn't find" in result
    
    def test_global_service_instance(self):
        """Test global service instance"""
        from ai_integration.services.rag_service import rag_service
        assert isinstance(rag_service, RAGService)
        assert rag_service.search_service is not None
        assert rag_service.embedding_service is not None
        assert rag_service.anthropic_client is not None