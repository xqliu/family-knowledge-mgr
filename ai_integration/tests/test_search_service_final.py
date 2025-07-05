"""
Comprehensive tests for search service targeting 90%+ branch coverage
Uses unittest.TestCase to avoid database dependencies
"""
import os
import sys
import django
from django.conf import settings

# Configure Django settings if not already configured
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.admin',
            'django.contrib.staticfiles',
            'family',
            'ai_integration',
        ],
        STATIC_URL='/static/',
        SECRET_KEY='test-secret-key',
        USE_TZ=True,
    )
    django.setup()

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import date, datetime
import logging

from ai_integration.services.search_service import SearchService, search_service


class TestSearchService(unittest.TestCase):
    """Comprehensive tests for SearchService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = SearchService()
        
        # Mock embedding service
        self.mock_embedding_service = Mock()
        self.service.embedding_service = self.mock_embedding_service
        
        # Mock logger to prevent output during tests
        logging.disable(logging.CRITICAL)
        
    def tearDown(self):
        """Clean up after tests"""
        logging.disable(logging.NOTSET)
        
    def test_init(self):
        """Test SearchService initialization"""
        service = SearchService()
        self.assertIsNotNone(service.embedding_service)
        self.assertEqual(len(service.SEARCHABLE_MODELS), 4)
        self.assertIn('story', service.SEARCHABLE_MODELS)
        self.assertIn('event', service.SEARCHABLE_MODELS)
        self.assertIn('heritage', service.SEARCHABLE_MODELS)
        self.assertIn('health', service.SEARCHABLE_MODELS)
        
    def test_semantic_search_empty_query(self):
        """Test semantic_search with empty query"""
        results = self.service.semantic_search("")
        self.assertEqual(results, [])
        
        results = self.service.semantic_search("   ")
        self.assertEqual(results, [])
        
        results = self.service.semantic_search(None)
        self.assertEqual(results, [])
        
    def test_semantic_search_embedding_failure(self):
        """Test semantic_search when embedding generation fails"""
        self.mock_embedding_service.generate_embedding.return_value = None
        
        results = self.service.semantic_search("test query")
        self.assertEqual(results, [])
        self.mock_embedding_service.generate_embedding.assert_called_once_with("test query")
        
    def test_semantic_search_success(self):
        """Test successful semantic_search"""
        # Mock embedding generation
        mock_embedding = [0.1, 0.2, 0.3]
        self.mock_embedding_service.generate_embedding.return_value = mock_embedding
        
        # Mock search results
        mock_story_results = [
            {'id': 1, 'title': 'Story 1', 'similarity': 0.9, 'content_type': 'story'},
            {'id': 2, 'title': 'Story 2', 'similarity': 0.8, 'content_type': 'story'},
        ]
        mock_event_results = [
            {'id': 1, 'title': 'Event 1', 'similarity': 0.85, 'content_type': 'event'},
        ]
        
        with patch.object(self.service, '_search_model') as mock_search:
            # Configure mock to return different results for different models
            def side_effect(model_class, *args):
                if model_class.__name__ == 'Story':
                    return mock_story_results
                elif model_class.__name__ == 'Event':
                    return mock_event_results
                else:
                    return []
                    
            mock_search.side_effect = side_effect
            
            results = self.service.semantic_search("test query", limit=5)
            
            # Should be sorted by similarity
            self.assertEqual(len(results), 3)
            self.assertEqual(results[0]['similarity'], 0.9)
            self.assertEqual(results[1]['similarity'], 0.85)
            self.assertEqual(results[2]['similarity'], 0.8)
            
    def test_semantic_search_with_model_types(self):
        """Test semantic_search with specific model types"""
        mock_embedding = [0.1, 0.2, 0.3]
        self.mock_embedding_service.generate_embedding.return_value = mock_embedding
        
        # Mock search results
        mock_results = [{'id': 1, 'title': 'Story 1', 'similarity': 0.9}]
        
        with patch.object(self.service, '_search_model', return_value=mock_results) as mock_search:
            results = self.service.semantic_search("test query", model_types=['story'])
            
            # Should only search story model
            self.assertEqual(mock_search.call_count, 1)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['content_type'], 'story')
            
    def test_semantic_search_unknown_model_type(self):
        """Test semantic_search with unknown model type"""
        mock_embedding = [0.1, 0.2, 0.3]
        self.mock_embedding_service.generate_embedding.return_value = mock_embedding
        
        with patch.object(self.service, '_search_model', return_value=[]) as mock_search:
            results = self.service.semantic_search("test query", model_types=['unknown'])
            
            # Should not call _search_model for unknown type
            mock_search.assert_not_called()
            self.assertEqual(results, [])
            
    def test_search_model_success(self):
        """Test successful _search_model"""
        mock_embedding = [0.1, 0.2, 0.3]
        
        # Create mock model instances
        mock_obj1 = Mock()
        mock_obj1.similarity = 0.9
        mock_obj2 = Mock()
        mock_obj2.similarity = 0.8
        
        # Mock queryset with proper chain
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = [mock_obj1, mock_obj2]
        
        # Mock model class
        mock_model = Mock()
        mock_model.__name__ = 'Story'
        mock_model.objects = mock_queryset
        
        with patch.object(self.service, '_format_search_result') as mock_format:
            mock_format.side_effect = [
                {'id': 1, 'title': 'Result 1', 'similarity': 0.9},
                {'id': 2, 'title': 'Result 2', 'similarity': 0.8},
            ]
            
            results = self.service._search_model(mock_model, mock_embedding, 10, 0.7)
            
            self.assertEqual(len(results), 2)
            mock_queryset.filter.assert_called()
            self.assertEqual(mock_format.call_count, 2)
            
    def test_search_model_exception(self):
        """Test _search_model with exception"""
        mock_embedding = [0.1, 0.2, 0.3]
        
        # Mock model that raises exception
        mock_model = Mock()
        mock_model.__name__ = 'Story'
        mock_model.objects.filter.side_effect = Exception("Database error")
        
        results = self.service._search_model(mock_model, mock_embedding, 10, 0.7)
        
        self.assertEqual(results, [])
        
    def test_format_search_result_story(self):
        """Test _format_search_result for Story model"""
        # Mock story object with proper type
        mock_story = Mock()
        type(mock_story).__name__ = 'Story'
        mock_story.id = 1
        mock_story.title = "Test Story"
        mock_story.content = "This is a test story content that is quite long and should be truncated. " * 5  # Make it longer than 200 chars
        mock_story.story_type = "memory"
        mock_story.date_occurred = date(2023, 1, 1)
        mock_story.similarity = 0.9
        mock_story.created_at = datetime(2023, 1, 1, 12, 0, 0)
        
        # Mock people relationship
        mock_person1 = Mock()
        mock_person1.name = "Person 1"
        mock_person2 = Mock()
        mock_person2.name = "Person 2"
        mock_story.people.all.return_value = [mock_person1, mock_person2]
        
        result = self.service._format_search_result(mock_story)
        
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['title'], "Test Story")
        self.assertTrue(result['content'].endswith('...'))
        self.assertEqual(result['story_type'], "memory")
        self.assertEqual(result['people'], ["Person 1", "Person 2"])
        self.assertEqual(result['similarity'], 0.9)
        
    def test_format_search_result_story_short_content(self):
        """Test _format_search_result for Story with short content"""
        mock_story = Mock()
        type(mock_story).__name__ = 'Story'
        mock_story.id = 1
        mock_story.title = "Test Story"
        mock_story.content = "Short content"
        mock_story.story_type = "memory"
        mock_story.date_occurred = None  # Test None date
        mock_story.similarity = 0.9
        mock_story.created_at = datetime(2023, 1, 1)
        mock_story.people.all.return_value = []
        
        result = self.service._format_search_result(mock_story)
        
        self.assertEqual(result['content'], "Short content")
        self.assertIsNone(result['date_occurred'])
        self.assertEqual(result['people'], [])
        
    def test_format_search_result_event(self):
        """Test _format_search_result for Event model"""
        mock_event = Mock()
        type(mock_event).__name__ = 'Event'
        mock_event.id = 1
        mock_event.name = "Test Event"
        mock_event.description = "A" * 250  # Long description
        mock_event.event_type = "birthday"
        mock_event.start_date = date(2023, 1, 1)
        mock_event.similarity = 0.85
        mock_event.created_at = datetime(2023, 1, 1)
        
        # Mock location
        mock_location = Mock()
        mock_location.name = "Test Location"
        mock_event.location = mock_location
        
        # Mock participants
        mock_person = Mock()
        mock_person.name = "Participant 1"
        mock_event.participants.all.return_value = [mock_person]
        
        result = self.service._format_search_result(mock_event)
        
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['title'], "Test Event")
        self.assertEqual(len(result['content']), 203)  # 200 + '...'
        self.assertEqual(result['location'], "Test Location")
        self.assertEqual(result['participants'], ["Participant 1"])
        
    def test_format_search_result_event_no_description(self):
        """Test _format_search_result for Event with no description"""
        mock_event = Mock()
        type(mock_event).__name__ = 'Event'
        mock_event.id = 1
        mock_event.name = "Test Event"
        mock_event.description = None
        mock_event.event_type = "birthday"
        mock_event.start_date = date(2023, 1, 1)
        mock_event.location = None
        mock_event.similarity = 0.85
        mock_event.created_at = datetime(2023, 1, 1)
        mock_event.participants.all.return_value = []
        
        result = self.service._format_search_result(mock_event)
        
        self.assertIsNone(result['content'])
        self.assertIsNone(result['location'])
        
    def test_format_search_result_heritage(self):
        """Test _format_search_result for Heritage model"""
        mock_heritage = Mock()
        type(mock_heritage).__name__ = 'Heritage'
        mock_heritage.id = 1
        mock_heritage.title = "Family Tradition"
        mock_heritage.description = "Traditional recipe passed down"
        mock_heritage.heritage_type = "tradition"
        mock_heritage.importance = "high"
        mock_heritage.similarity = 0.8
        mock_heritage.created_at = datetime(2023, 1, 1)
        
        # Mock origin person
        mock_person = Mock()
        mock_person.name = "Grandma"
        mock_heritage.origin_person = mock_person
        
        result = self.service._format_search_result(mock_heritage)
        
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['title'], "Family Tradition")
        self.assertEqual(result['heritage_type'], "tradition")
        self.assertEqual(result['importance'], "high")
        self.assertEqual(result['origin_person'], "Grandma")
        
    def test_format_search_result_heritage_no_origin(self):
        """Test _format_search_result for Heritage with no origin person"""
        mock_heritage = Mock()
        type(mock_heritage).__name__ = 'Heritage'
        mock_heritage.id = 1
        mock_heritage.title = "Family Value"
        mock_heritage.description = "A" * 250  # Long description
        mock_heritage.heritage_type = "value"
        mock_heritage.importance = "medium"
        mock_heritage.origin_person = None
        mock_heritage.similarity = 0.8
        mock_heritage.created_at = datetime(2023, 1, 1)
        
        result = self.service._format_search_result(mock_heritage)
        
        self.assertIsNone(result['origin_person'])
        self.assertTrue(result['content'].endswith('...'))
        
    def test_format_search_result_health(self):
        """Test _format_search_result for Health model"""
        mock_health = Mock()
        type(mock_health).__name__ = 'Health'
        mock_health.id = 1
        mock_health.title = "Health Record"
        mock_health.description = "Regular checkup notes"
        mock_health.record_type = "checkup"
        mock_health.date = date(2023, 1, 1)
        mock_health.is_hereditary = True
        mock_health.similarity = 0.75
        mock_health.created_at = datetime(2023, 1, 1)
        
        # Mock person
        mock_person = Mock()
        mock_person.name = "John Doe"
        mock_health.person = mock_person
        
        result = self.service._format_search_result(mock_health)
        
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['title'], "Health Record")
        self.assertEqual(result['record_type'], "checkup")
        self.assertEqual(result['person'], "John Doe")
        self.assertEqual(result['is_hereditary'], True)
        
    def test_format_search_result_unknown_type(self):
        """Test _format_search_result for unknown model type"""
        mock_obj = Mock()
        type(mock_obj).__name__ = 'UnknownModel'
        mock_obj.id = 1
        mock_obj.similarity = 0.7
        mock_obj.created_at = datetime(2023, 1, 1)
        mock_obj.__str__ = Mock(return_value="Unknown Object")
        
        result = self.service._format_search_result(mock_obj)
        
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['title'], "Unknown Object")
        self.assertEqual(result['content'], '')
        self.assertEqual(result['similarity'], 0.7)
        
    def test_format_search_result_unknown_no_created_at(self):
        """Test _format_search_result for object without created_at"""
        mock_obj = Mock(spec=['id', 'similarity'])
        type(mock_obj).__name__ = 'UnknownModel'
        mock_obj.id = 1
        mock_obj.similarity = 0.7
        mock_obj.__str__ = Mock(return_value="Unknown Object")
        
        result = self.service._format_search_result(mock_obj)
        
        self.assertIsNone(result['created_at'])
        
    def test_search_by_category_valid(self):
        """Test search_by_category with valid category"""
        with patch.object(self.service, 'semantic_search') as mock_search:
            mock_search.return_value = [{'id': 1, 'title': 'Result'}]
            
            # Test various category mappings
            result = self.service.search_by_category("test query", "stories", limit=5)
            mock_search.assert_called_with("test query", ['story'], 5)
            
            result = self.service.search_by_category("test query", "events")
            mock_search.assert_called_with("test query", ['event'], 10)
            
            result = self.service.search_by_category("test query", "memories")  # Alias
            mock_search.assert_called_with("test query", ['story'], 10)
            
            result = self.service.search_by_category("test query", "traditions")  # Alias
            mock_search.assert_called_with("test query", ['heritage'], 10)
            
    def test_search_by_category_invalid(self):
        """Test search_by_category with invalid category"""
        result = self.service.search_by_category("test query", "invalid_category")
        self.assertEqual(result, [])
        
    def test_find_related_content_invalid_type(self):
        """Test find_related_content with invalid content type"""
        result = self.service.find_related_content(1, "invalid_type", 5)
        self.assertEqual(result, [])
        
    def test_find_related_content_object_not_found(self):
        """Test find_related_content when object doesn't exist"""
        mock_model = Mock()
        mock_model.objects.get.side_effect = Exception("Not found")
        
        with patch.dict(self.service.SEARCHABLE_MODELS, {'story': mock_model}):
            result = self.service.find_related_content(1, "story", 5)
            self.assertEqual(result, [])
            
    def test_find_related_content_no_embedding(self):
        """Test find_related_content when object has no embedding"""
        mock_obj = Mock()
        mock_obj.content_embedding = None
        
        mock_model = Mock()
        mock_model.objects.get.return_value = mock_obj
        
        with patch.dict(self.service.SEARCHABLE_MODELS, {'story': mock_model}):
            result = self.service.find_related_content(1, "story", 5)
            self.assertEqual(result, [])
            
    def test_find_related_content_success(self):
        """Test successful find_related_content"""
        # Mock reference object
        mock_ref_obj = Mock()
        mock_ref_obj.content_embedding = [0.1, 0.2, 0.3]
        
        # Mock related objects
        mock_related1 = Mock()
        mock_related1.similarity = 0.9
        mock_related2 = Mock()
        mock_related2.similarity = 0.8
        
        # Mock models
        mock_story_model = Mock()
        mock_story_model.__name__ = 'Story'
        mock_story_model.objects.get.return_value = mock_ref_obj
        
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.exclude.return_value = mock_queryset
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = [mock_related1, mock_related2]
        
        mock_story_model.objects.filter.return_value = mock_queryset
        
        with patch.dict(self.service.SEARCHABLE_MODELS, {'story': mock_story_model}):
            with patch.object(self.service, '_format_search_result') as mock_format:
                mock_format.side_effect = [
                    {'id': 2, 'title': 'Related 1', 'similarity': 0.9},
                    {'id': 3, 'title': 'Related 2', 'similarity': 0.8},
                ]
                
                result = self.service.find_related_content(1, "story", 5)
                
                self.assertEqual(len(result), 2)
                self.assertEqual(result[0]['similarity'], 0.9)
                self.assertEqual(result[0]['content_type'], 'story')
                
    def test_keyword_search_all_models(self):
        """Test keyword_search across all models"""
        # Mock search results for each model
        mock_story = Mock()
        mock_event = Mock()
        mock_heritage = Mock()
        mock_health = Mock()
        
        # Mock model classes
        mock_models = {
            'story': Mock(objects=Mock(filter=Mock(return_value=[mock_story]))),
            'event': Mock(objects=Mock(filter=Mock(return_value=[mock_event]))),
            'heritage': Mock(objects=Mock(filter=Mock(return_value=[mock_heritage]))),
            'health': Mock(objects=Mock(filter=Mock(return_value=[mock_health]))),
        }
        
        with patch.dict(self.service.SEARCHABLE_MODELS, mock_models):
            with patch.object(self.service, '_format_search_result') as mock_format:
                mock_format.side_effect = [
                    {'id': 1, 'title': 'Story Result'},
                    {'id': 2, 'title': 'Event Result'},
                    {'id': 3, 'title': 'Heritage Result'},
                    {'id': 4, 'title': 'Health Result'},
                ]
                
                results = self.service.keyword_search("test query")
                
                self.assertEqual(len(results), 4)
                # Check that default similarity is added
                for result in results:
                    self.assertEqual(result['similarity'], 0.5)
                    
    def test_keyword_search_specific_models(self):
        """Test keyword_search with specific model types"""
        mock_story = Mock()
        mock_story_model = Mock(objects=Mock(filter=Mock(return_value=[mock_story])))
        
        with patch.dict(self.service.SEARCHABLE_MODELS, {'story': mock_story_model}):
            with patch.object(self.service, '_format_search_result') as mock_format:
                mock_format.return_value = {'id': 1, 'title': 'Story Result'}
                
                results = self.service.keyword_search("test", model_types=['story'], limit=5)
                
                self.assertEqual(len(results), 1)
                self.assertEqual(results[0]['content_type'], 'story')
                
    def test_keyword_search_unknown_model_type(self):
        """Test keyword_search with unknown model type"""
        results = self.service.keyword_search("test", model_types=['unknown'])
        self.assertEqual(results, [])
        
    def test_global_service_instance(self):
        """Test that global service instance is created"""
        self.assertIsInstance(search_service, SearchService)
        self.assertIsNotNone(search_service.embedding_service)


if __name__ == '__main__':
    unittest.main()