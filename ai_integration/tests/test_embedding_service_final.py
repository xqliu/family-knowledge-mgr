"""
Comprehensive tests for embedding service targeting 90%+ branch coverage
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
        OPENAI_API_KEY='test-api-key',
    )
    django.setup()

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
import hashlib
import logging

from ai_integration.services.embedding_service import EmbeddingService, embedding_service


class TestEmbeddingService(unittest.TestCase):
    """Comprehensive tests for EmbeddingService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = EmbeddingService()
        
        # Mock logger to prevent output during tests
        logging.disable(logging.CRITICAL)
        
    def tearDown(self):
        """Clean up after tests"""
        logging.disable(logging.NOTSET)
        
    def test_init(self):
        """Test EmbeddingService initialization"""
        with patch('ai_integration.services.embedding_service.OpenAI') as mock_openai:
            service = EmbeddingService()
            
            mock_openai.assert_called_once_with(api_key='test-api-key')
            self.assertEqual(service.model, "text-embedding-3-small")
            
    def test_init_no_api_key(self):
        """Test initialization when API key is not set"""
        with patch('ai_integration.services.embedding_service.getattr', return_value=''):
            with patch('ai_integration.services.embedding_service.OpenAI') as mock_openai:
                service = EmbeddingService()
                
                mock_openai.assert_called_once_with(api_key='')
                
    def test_generate_embedding_success(self):
        """Test successful embedding generation"""
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        
        self.service.client.embeddings.create = Mock(return_value=mock_response)
        
        result = self.service.generate_embedding("test text")
        
        self.assertEqual(result, [0.1, 0.2, 0.3])
        self.service.client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-small",
            input="test text"
        )
        
    def test_generate_embedding_empty_text(self):
        """Test generate_embedding with empty text"""
        result = self.service.generate_embedding("")
        self.assertIsNone(result)
        
        result = self.service.generate_embedding("   ")
        self.assertIsNone(result)
        
        result = self.service.generate_embedding(None)
        self.assertIsNone(result)
        
    def test_generate_embedding_exception(self):
        """Test generate_embedding when API call fails"""
        self.service.client.embeddings.create = Mock(side_effect=Exception("API error"))
        
        result = self.service.generate_embedding("test text")
        
        self.assertIsNone(result)
        
    def test_get_content_hash(self):
        """Test content hash generation"""
        text = "Hello, family!"
        expected_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        
        result = self.service.get_content_hash(text)
        
        self.assertEqual(result, expected_hash)
        
    def test_get_or_create_embedding_empty_text(self):
        """Test get_or_create_embedding with empty text"""
        result = self.service.get_or_create_embedding("", "story", 1)
        self.assertIsNone(result)
        
        result = self.service.get_or_create_embedding("   ", "story", 1)
        self.assertIsNone(result)
        
    def test_get_or_create_embedding_from_cache(self):
        """Test getting embedding from cache"""
        mock_cached = Mock()
        mock_cached.embedding = [0.1, 0.2, 0.3]
        
        with patch('ai_integration.services.embedding_service.EmbeddingCache') as mock_cache:
            mock_cache.objects.get.return_value = mock_cached
            
            result = self.service.get_or_create_embedding("test text", "story", 1)
            
            self.assertEqual(result, [0.1, 0.2, 0.3])
            mock_cache.objects.get.assert_called_once()
            
    def test_get_or_create_embedding_generate_new(self):
        """Test generating new embedding when not in cache"""
        with patch('ai_integration.services.embedding_service.EmbeddingCache') as mock_cache:
            # Create a proper exception class
            class DoesNotExist(Exception):
                pass
            mock_cache.DoesNotExist = DoesNotExist
            mock_cache.objects.get.side_effect = DoesNotExist
            
            with patch.object(self.service, 'generate_embedding') as mock_generate:
                mock_generate.return_value = [0.4, 0.5, 0.6]
                
                result = self.service.get_or_create_embedding("test text", "story", 1)
                
                self.assertEqual(result, [0.4, 0.5, 0.6])
                mock_generate.assert_called_once_with("test text")
                mock_cache.objects.update_or_create.assert_called_once()
                
    def test_get_or_create_embedding_generate_failed(self):
        """Test when embedding generation fails"""
        with patch('ai_integration.services.embedding_service.EmbeddingCache') as mock_cache:
            # Create a proper exception class
            class DoesNotExist(Exception):
                pass
            mock_cache.DoesNotExist = DoesNotExist
            mock_cache.objects.get.side_effect = DoesNotExist
            
            with patch.object(self.service, 'generate_embedding') as mock_generate:
                mock_generate.return_value = None
                
                result = self.service.get_or_create_embedding("test text", "story", 1)
                
                self.assertIsNone(result)
                mock_cache.objects.update_or_create.assert_not_called()
                
    def test_update_model_embedding_no_field(self):
        """Test update_model_embedding with model lacking content_embedding field"""
        mock_instance = Mock(spec=['id'])
        mock_instance.id = 1
        
        result = self.service.update_model_embedding(mock_instance)
        
        self.assertFalse(result)
        
    def test_update_model_embedding_no_content(self):
        """Test update_model_embedding when content extraction returns empty"""
        mock_instance = Mock()
        mock_instance.content_embedding = None
        mock_instance.id = 1
        
        with patch.object(self.service, '_extract_content_text') as mock_extract:
            mock_extract.return_value = ""
            
            result = self.service.update_model_embedding(mock_instance)
            
            self.assertFalse(result)
            
    def test_update_model_embedding_already_up_to_date(self):
        """Test update_model_embedding when embedding is already current"""
        mock_instance = Mock()
        mock_instance.content_embedding = [0.1, 0.2, 0.3]
        mock_instance.embedding_updated = datetime.now()
        mock_instance.id = 1
        
        mock_cached = Mock()
        mock_cached.embedding = [0.1, 0.2, 0.3]
        
        with patch.object(self.service, '_extract_content_text') as mock_extract:
            mock_extract.return_value = "test content"
            
            with patch('ai_integration.services.embedding_service.EmbeddingCache') as mock_cache:
                mock_cache.objects.get.return_value = mock_cached
                
                result = self.service.update_model_embedding(mock_instance, force_update=False)
                
                self.assertFalse(result)
                
    def test_update_model_embedding_force_update(self):
        """Test update_model_embedding with force_update=True"""
        mock_instance = Mock()
        mock_instance.content_embedding = [0.1, 0.2, 0.3]
        mock_instance.embedding_updated = datetime.now()
        mock_instance.id = 1
        type(mock_instance).__name__ = 'Story'
        
        with patch.object(self.service, '_extract_content_text') as mock_extract:
            mock_extract.return_value = "test content"
            
            with patch.object(self.service, 'get_or_create_embedding') as mock_get_embedding:
                mock_get_embedding.return_value = [0.4, 0.5, 0.6]
                
                with patch('django.utils.timezone.now') as mock_now:
                    mock_now.return_value = datetime(2023, 1, 1)
                    
                    result = self.service.update_model_embedding(mock_instance, force_update=True)
                    
                    self.assertTrue(result)
                    self.assertEqual(mock_instance.content_embedding, [0.4, 0.5, 0.6])
                    self.assertEqual(mock_instance.embedding_updated, datetime(2023, 1, 1))
                    mock_instance.save.assert_called_once_with(
                        update_fields=['content_embedding', 'embedding_updated']
                    )
                    
    def test_update_model_embedding_cache_miss(self):
        """Test update_model_embedding when cache check fails"""
        mock_instance = Mock()
        mock_instance.content_embedding = [0.1, 0.2, 0.3]
        mock_instance.embedding_updated = datetime.now()
        mock_instance.id = 1
        type(mock_instance).__name__ = 'Event'
        
        with patch.object(self.service, '_extract_content_text') as mock_extract:
            mock_extract.return_value = "test content"
            
            with patch('ai_integration.services.embedding_service.EmbeddingCache') as mock_cache:
                # Create a proper exception class
                class DoesNotExist(Exception):
                    pass
                mock_cache.DoesNotExist = DoesNotExist
                mock_cache.objects.get.side_effect = DoesNotExist
                
                with patch.object(self.service, 'get_or_create_embedding') as mock_get_embedding:
                    mock_get_embedding.return_value = [0.7, 0.8, 0.9]
                    
                    result = self.service.update_model_embedding(mock_instance)
                    
                    self.assertTrue(result)
                    self.assertEqual(mock_instance.content_embedding, [0.7, 0.8, 0.9])
                    
    def test_update_model_embedding_generation_failed(self):
        """Test update_model_embedding when embedding generation fails"""
        mock_instance = Mock()
        mock_instance.content_embedding = None
        mock_instance.id = 1
        type(mock_instance).__name__ = 'Heritage'
        
        with patch.object(self.service, '_extract_content_text') as mock_extract:
            mock_extract.return_value = "test content"
            
            with patch.object(self.service, 'get_or_create_embedding') as mock_get_embedding:
                mock_get_embedding.return_value = None
                
                result = self.service.update_model_embedding(mock_instance)
                
                self.assertFalse(result)
                mock_instance.save.assert_not_called()
                
    def test_extract_content_text_story(self):
        """Test _extract_content_text for Story model"""
        mock_story = Mock()
        type(mock_story).__name__ = 'Story'
        mock_story.title = "Family Gathering"
        mock_story.content = "It was a warm summer day..."
        
        result = self.service._extract_content_text(mock_story)
        
        self.assertEqual(result, "Family Gathering\n\nIt was a warm summer day...")
        
    def test_extract_content_text_event(self):
        """Test _extract_content_text for Event model"""
        mock_event = Mock()
        type(mock_event).__name__ = 'Event'
        mock_event.name = "Birthday Party"
        mock_event.description = "Celebrated grandpa's 80th birthday"
        
        result = self.service._extract_content_text(mock_event)
        
        self.assertEqual(result, "Birthday Party\n\nCelebrated grandpa's 80th birthday")
        
    def test_extract_content_text_heritage(self):
        """Test _extract_content_text for Heritage model"""
        mock_heritage = Mock()
        type(mock_heritage).__name__ = 'Heritage'
        mock_heritage.title = "Family Recipe"
        mock_heritage.description = "Grandma's secret dumpling recipe"
        
        result = self.service._extract_content_text(mock_heritage)
        
        self.assertEqual(result, "Family Recipe\n\nGrandma's secret dumpling recipe")
        
    def test_extract_content_text_health(self):
        """Test _extract_content_text for Health model"""
        mock_health = Mock()
        type(mock_health).__name__ = 'Health'
        mock_health.title = "Annual Checkup"
        mock_health.description = "All results normal"
        
        result = self.service._extract_content_text(mock_health)
        
        self.assertEqual(result, "Annual Checkup\n\nAll results normal")
        
    def test_extract_content_text_person_with_bio(self):
        """Test _extract_content_text for Person model with bio"""
        mock_person = Mock()
        type(mock_person).__name__ = 'Person'
        mock_person.bio = "A loving father and grandfather"
        mock_person.name = "John Doe"
        
        result = self.service._extract_content_text(mock_person)
        
        self.assertEqual(result, "A loving father and grandfather")
        
    def test_extract_content_text_person_no_bio(self):
        """Test _extract_content_text for Person model without bio"""
        mock_person = Mock()
        type(mock_person).__name__ = 'Person'
        mock_person.bio = None
        mock_person.name = "Jane Doe"
        
        result = self.service._extract_content_text(mock_person)
        
        self.assertEqual(result, "Jane Doe")
        
    def test_extract_content_text_unknown_model(self):
        """Test _extract_content_text for unknown model type"""
        # Model with content field
        mock_obj = Mock()
        type(mock_obj).__name__ = 'CustomModel'
        mock_obj.content = "Some content"
        
        result = self.service._extract_content_text(mock_obj)
        self.assertEqual(result, "Some content")
        
        # Model with description field
        mock_obj2 = Mock(spec=['description'])
        type(mock_obj2).__name__ = 'AnotherModel'
        mock_obj2.description = "Some description"
        
        result = self.service._extract_content_text(mock_obj2)
        self.assertEqual(result, "Some description")
        
        # Model with no matching fields
        mock_obj3 = Mock(spec=['id'])
        type(mock_obj3).__name__ = 'EmptyModel'
        
        result = self.service._extract_content_text(mock_obj3)
        self.assertEqual(result, "")
        
    def test_extract_content_text_fallback_fields(self):
        """Test _extract_content_text fallback field checking"""
        # Test bio field
        mock_obj = Mock(spec=['bio'])
        type(mock_obj).__name__ = 'UnknownModel'
        mock_obj.bio = "Biography text"
        
        result = self.service._extract_content_text(mock_obj)
        self.assertEqual(result, "Biography text")
        
        # Test title field
        mock_obj = Mock(spec=['title'])
        type(mock_obj).__name__ = 'UnknownModel'
        mock_obj.title = "Title text"
        
        result = self.service._extract_content_text(mock_obj)
        self.assertEqual(result, "Title text")
        
        # Test name field
        mock_obj = Mock(spec=['name'])
        type(mock_obj).__name__ = 'UnknownModel'
        mock_obj.name = "Name text"
        
        result = self.service._extract_content_text(mock_obj)
        self.assertEqual(result, "Name text")
        
    def test_bulk_update_embeddings_no_instances(self):
        """Test bulk_update_embeddings when no instances need updates"""
        mock_model = Mock()
        mock_model.__name__ = 'TestModel'
        mock_queryset = Mock()
        mock_queryset.count.return_value = 0
        mock_model.objects.filter.return_value = mock_queryset
        
        result = self.service.bulk_update_embeddings(mock_model)
        
        self.assertEqual(result, {'updated': 0, 'skipped': 0, 'failed': 0})
        
    def test_bulk_update_embeddings_success(self):
        """Test successful bulk_update_embeddings"""
        mock_model = Mock()
        mock_model.__name__ = 'TestModel'
        
        mock_instance1 = Mock()
        mock_instance1.id = 1
        mock_instance2 = Mock()
        mock_instance2.id = 2
        mock_instance3 = Mock()
        mock_instance3.id = 3
        
        mock_queryset = Mock()
        mock_queryset.count.return_value = 3
        mock_queryset.__getitem__ = Mock(side_effect=lambda s: [mock_instance1, mock_instance2, mock_instance3][s])
        mock_model.objects.filter.return_value = mock_queryset
        
        with patch.object(self.service, 'update_model_embedding') as mock_update:
            # First succeeds, second skipped, third succeeds
            mock_update.side_effect = [True, False, True]
            
            result = self.service.bulk_update_embeddings(mock_model, batch_size=2)
            
            self.assertEqual(result, {'updated': 2, 'skipped': 1, 'failed': 0})
            self.assertEqual(mock_update.call_count, 3)
            
    def test_bulk_update_embeddings_with_failures(self):
        """Test bulk_update_embeddings with some failures"""
        mock_model = Mock()
        mock_model.__name__ = 'TestModel'
        
        mock_instance1 = Mock()
        mock_instance1.id = 1
        mock_instance2 = Mock()
        mock_instance2.id = 2
        
        mock_queryset = Mock()
        mock_queryset.count.return_value = 2
        mock_queryset.__getitem__ = Mock(side_effect=lambda s: [mock_instance1, mock_instance2][s])
        mock_model.objects.filter.return_value = mock_queryset
        
        with patch.object(self.service, 'update_model_embedding') as mock_update:
            # First succeeds, second raises exception
            mock_update.side_effect = [True, Exception("Update failed")]
            
            result = self.service.bulk_update_embeddings(mock_model, batch_size=10)
            
            self.assertEqual(result, {'updated': 1, 'skipped': 0, 'failed': 1})
            
    def test_global_service_instance(self):
        """Test that global service instance is created"""
        self.assertIsInstance(embedding_service, EmbeddingService)
        self.assertIsNotNone(embedding_service.client)


if __name__ == '__main__':
    unittest.main()