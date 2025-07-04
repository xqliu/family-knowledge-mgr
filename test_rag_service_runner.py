#!/usr/bin/env python
"""
Unit tests for RAG service
"""
import os
import sys
import django
from unittest.mock import Mock, patch, MagicMock
import unittest
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ai_integration.services.rag_service import RAGService, rag_service


class TestRAGService(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.rag_service = RAGService()
        
    def test_init(self):
        """Test RAGService initialization"""
        service = RAGService()
        self.assertIsNotNone(service.search_service)
        self.assertIsNotNone(service.embedding_service)
        self.assertIsNotNone(service.anthropic_client)
        
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
            self.assertEqual(result, 'health_pattern')
    
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
            self.assertEqual(result, 'event_planning')
    
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
            self.assertEqual(result, 'cultural_heritage')
    
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
            self.assertEqual(result, 'relationship_discovery')
    
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
            self.assertEqual(result, 'memory_discovery')
    
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
            self.assertEqual(result, 'general')
    
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
            self.assertEqual(result, 'zh-CN')
    
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
            self.assertEqual(result, 'en-US')
    
    def test_calculate_confidence_empty(self):
        """Test confidence calculation with empty results"""
        result = self.rag_service._calculate_confidence([])
        self.assertEqual(result, 0.0)
    
    def test_calculate_confidence_single_result(self):
        """Test confidence calculation with single result"""
        search_results = [{'similarity': 0.8}]
        result = self.rag_service._calculate_confidence(search_results)
        self.assertGreater(result, 0.8)
        self.assertLessEqual(result, 1.0)
    
    def test_calculate_confidence_multiple_results(self):
        """Test confidence calculation with multiple results"""
        search_results = [
            {'similarity': 0.9},
            {'similarity': 0.8},
            {'similarity': 0.7}
        ]
        result = self.rag_service._calculate_confidence(search_results)
        self.assertGreater(result, 0.8)
        self.assertLessEqual(result, 1.0)
    
    def test_build_context_empty(self):
        """Test context building with empty results"""
        result = self.rag_service._build_context([], 'general')
        self.assertEqual(result, "")
    
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
        self.assertIn('Family Story', result)
        self.assertIn('Family Reunion', result)
        self.assertIn('great family reunion', result)
        self.assertIn('People involved', result)
        self.assertIn('John, Mary, Bob', result)
    
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
        self.assertIn('Family Event', result)
        self.assertIn('Birthday Party', result)
        self.assertIn('Type: birthday', result)
        self.assertIn('Location: Home', result)
    
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
        self.assertIn('Family Heritage', result)
        self.assertIn('Family Recipe', result)
        self.assertIn('Type: recipe', result)
        self.assertIn('Origin: Grandma', result)
    
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
        self.assertIn('Health Record', result)
        self.assertIn('Person: John Doe', result)
        self.assertIn('Hereditary: Yes', result)
    
    def test_format_sources_empty(self):
        """Test source formatting with empty results"""
        result = self.rag_service._format_sources([])
        self.assertEqual(result, [])
    
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
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['type'], 'story')
        self.assertEqual(result[0]['id'], 1)
        self.assertEqual(result[0]['title'], 'Family Story')
        self.assertEqual(result[0]['relevance'], 0.9)
        self.assertEqual(result[0]['story_type'], 'childhood')
        self.assertEqual(result[0]['people'], ['Alice', 'Bob'])  # Limited to 2
    
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
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['type'], 'event')
        self.assertEqual(result[0]['event_type'], 'birthday')
        self.assertEqual(result[0]['date'], '2024-01-01')
    
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
            self.assertIsInstance(result, str)
            self.assertIn('family knowledge keeper', result)
            self.assertGreater(len(result), 100)
    
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
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 50)
            self.assertNotIn('很抱歉', result)  # Should not contain Chinese
    
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
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 50)
            # Check for Chinese characters instead of specific text
            chinese_chars = sum(1 for char in result if '\u4e00' <= char <= '\u9fff')
            self.assertGreater(chinese_chars, 0)  # Should contain Chinese
    
    def test_generate_error_response_english(self):
        """Test error response generation in English"""
        result = self.rag_service._generate_error_response('English query', 'Test error')
        
        self.assertIsInstance(result, dict)
        self.assertIn('query', result)
        self.assertIn('response', result)
        self.assertIn('sources', result)
        self.assertIn('metadata', result)
        self.assertEqual(result['query'], 'English query')
        self.assertEqual(result['metadata']['query_type'], 'error')
        self.assertEqual(result['metadata']['confidence'], 0.0)
        self.assertEqual(result['metadata']['language'], 'en-US')
        self.assertEqual(result['metadata']['error'], 'Test error')
    
    def test_generate_error_response_chinese(self):
        """Test error response generation in Chinese"""
        result = self.rag_service._generate_error_response('中文查询', 'Test error')
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['query'], '中文查询')
        self.assertEqual(result['metadata']['language'], 'zh-CN')
        self.assertIn('技术问题', result['response'])
    
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
            
            self.assertIsInstance(result, dict)
            self.assertIn('query', result)
            self.assertIn('response', result)
            self.assertIn('sources', result)
            self.assertIn('metadata', result)
            self.assertEqual(result['query'], 'Tell me family stories')
            self.assertEqual(result['response'], 'AI generated response')
            self.assertEqual(result['metadata']['query_type'], 'memory_discovery')
            self.assertEqual(result['metadata']['processing_time'], 1.5)
            self.assertEqual(result['metadata']['sources_count'], 1)
    
    @patch('ai_integration.services.rag_service.search_service')
    def test_generate_response_no_results(self, mock_search_service):
        """Test response generation with no search results"""
        # Mock empty search results
        mock_search_service.semantic_search.return_value = []
        
        result = self.rag_service.generate_response('Random query')
        
        self.assertIsInstance(result, dict)
        self.assertIn('query', result)
        self.assertIn('response', result)
        self.assertIn('sources', result)
        self.assertIn('metadata', result)
        self.assertEqual(result['metadata']['sources_count'], 0)
        self.assertIn('couldn\'t find', result['response'])
    
    @patch('ai_integration.services.rag_service.search_service')
    def test_generate_response_exception(self, mock_search_service):
        """Test response generation with exception"""
        # Mock exception in search
        mock_search_service.semantic_search.side_effect = Exception('Search failed')
        
        result = self.rag_service.generate_response('Test query')
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['metadata']['query_type'], 'error')
        self.assertEqual(result['metadata']['confidence'], 0.0)
        self.assertIn('error', result['metadata'])
    
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
            
            self.assertEqual(result, 'AI generated response')
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
            self.assertIsInstance(result, str)
            self.assertIn('couldn\'t find', result)
    
    def test_global_service_instance(self):
        """Test global service instance"""
        from ai_integration.services.rag_service import rag_service
        self.assertIsInstance(rag_service, RAGService)
        self.assertIsNotNone(rag_service.search_service)
        self.assertIsNotNone(rag_service.embedding_service)
        self.assertIsNotNone(rag_service.anthropic_client)


if __name__ == '__main__':
    # Run coverage analysis
    try:
        import coverage
        cov = coverage.Coverage(source=['ai_integration.services.rag_service'])
        cov.start()
        
        # Run tests
        unittest.main(verbosity=2, exit=False)
        
        cov.stop()
        cov.save()
        
        print("\n" + "="*50)
        print("COVERAGE REPORT")
        print("="*50)
        cov.report()
        
    except ImportError:
        print("Coverage not available, running tests only")
        unittest.main(verbosity=2)