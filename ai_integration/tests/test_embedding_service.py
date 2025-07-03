"""
Automated tests for embedding service
"""
import pytest
from unittest.mock import patch, Mock
from django.test import TestCase
from django.utils import timezone
from family.models import Story, Person
from ai_integration.services.embedding_service import embedding_service
from ai_integration.models import EmbeddingCache


class TestEmbeddingService(TestCase):
    """Test embedding service functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.person = Person.objects.create(
            name="Test Grandma",
            bio="Loving grandmother who cooks amazing food"
        )
        
        self.story = Story.objects.create(
            title="Grandma's Cooking",
            content="Every Sunday, grandma would make dumplings from scratch. The whole family would gather...",
            story_type="memory"
        )
    
    @patch('ai_integration.services.embedding_service.OpenAI')
    def test_generate_embedding_success(self, mock_openai):
        """Test successful embedding generation"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3] * 512)]  # 1536 dimensions
        mock_openai.return_value.embeddings.create.return_value = mock_response
        
        # Test embedding generation
        embedding = embedding_service.generate_embedding("Test content")
        
        self.assertIsNotNone(embedding)
        self.assertEqual(len(embedding), 1536)
        mock_openai.return_value.embeddings.create.assert_called_once()
    
    @patch('ai_integration.services.embedding_service.OpenAI')
    def test_generate_embedding_failure(self, mock_openai):
        """Test embedding generation failure"""
        # Mock OpenAI exception
        mock_openai.return_value.embeddings.create.side_effect = Exception("API Error")
        
        # Test embedding generation
        embedding = embedding_service.generate_embedding("Test content")
        
        self.assertIsNone(embedding)
    
    def test_generate_embedding_empty_text(self):
        """Test embedding generation with empty text"""
        embedding = embedding_service.generate_embedding("")
        self.assertIsNone(embedding)
        
        embedding = embedding_service.generate_embedding("   ")
        self.assertIsNone(embedding)
    
    def test_get_content_hash(self):
        """Test content hash generation"""
        text1 = "Same content"
        text2 = "Same content"
        text3 = "Different content"
        
        hash1 = embedding_service.get_content_hash(text1)
        hash2 = embedding_service.get_content_hash(text2)
        hash3 = embedding_service.get_content_hash(text3)
        
        self.assertEqual(hash1, hash2)
        self.assertNotEqual(hash1, hash3)
        self.assertEqual(len(hash1), 64)  # SHA256 hex length
    
    @patch('ai_integration.services.embedding_service.OpenAI')
    def test_get_or_create_embedding_cache_hit(self, mock_openai):
        """Test embedding retrieval from cache"""
        # Create cached embedding
        test_embedding = [0.1, 0.2, 0.3] * 512
        content_hash = embedding_service.get_content_hash("Test content")
        EmbeddingCache.objects.create(
            content_hash=content_hash,
            content_type="story",
            content_id=1,
            embedding=test_embedding
        )
        
        # Test cache retrieval
        embedding = embedding_service.get_or_create_embedding("Test content", "story", 1)
        
        self.assertEqual(embedding, test_embedding)
        # Should not call OpenAI API
        mock_openai.return_value.embeddings.create.assert_not_called()
    
    @patch('ai_integration.services.embedding_service.OpenAI')
    def test_get_or_create_embedding_cache_miss(self, mock_openai):
        """Test embedding generation when not in cache"""
        # Mock OpenAI response
        test_embedding = [0.1, 0.2, 0.3] * 512
        mock_response = Mock()
        mock_response.data = [Mock(embedding=test_embedding)]
        mock_openai.return_value.embeddings.create.return_value = mock_response
        
        # Test embedding generation and caching
        embedding = embedding_service.get_or_create_embedding("New content", "story", 1)
        
        self.assertEqual(embedding, test_embedding)
        # Should call OpenAI API
        mock_openai.return_value.embeddings.create.assert_called_once()
        
        # Should create cache entry
        content_hash = embedding_service.get_content_hash("New content")
        cache_entry = EmbeddingCache.objects.get(content_hash=content_hash)
        self.assertEqual(cache_entry.embedding, test_embedding)
    
    def test_extract_content_text_story(self):
        """Test content text extraction from Story model"""
        content_text = embedding_service._extract_content_text(self.story)
        expected = f"{self.story.title}\n\n{self.story.content}"
        self.assertEqual(content_text, expected)
    
    def test_extract_content_text_person(self):
        """Test content text extraction from Person model"""
        content_text = embedding_service._extract_content_text(self.person)
        self.assertEqual(content_text, self.person.bio)
        
        # Test person without bio
        person_no_bio = Person.objects.create(name="Test Person")
        content_text = embedding_service._extract_content_text(person_no_bio)
        self.assertEqual(content_text, person_no_bio.name)
    
    @patch('ai_integration.services.embedding_service.OpenAI')
    def test_update_model_embedding(self, mock_openai):
        """Test updating model instance embedding"""
        # Mock OpenAI response
        test_embedding = [0.1, 0.2, 0.3] * 512
        mock_response = Mock()
        mock_response.data = [Mock(embedding=test_embedding)]
        mock_openai.return_value.embeddings.create.return_value = mock_response
        
        # Test embedding update
        result = embedding_service.update_model_embedding(self.story)
        
        self.assertTrue(result)
        self.story.refresh_from_db()
        self.assertEqual(self.story.content_embedding, test_embedding)
        self.assertIsNotNone(self.story.embedding_updated)
    
    def test_update_model_embedding_no_content(self):
        """Test updating embedding for model with no content"""
        empty_story = Story.objects.create(title="", content="")
        result = embedding_service.update_model_embedding(empty_story)
        self.assertFalse(result)
    
    @patch('ai_integration.services.embedding_service.OpenAI')
    def test_bulk_update_embeddings(self, mock_openai):
        """Test bulk embedding updates"""
        # Create multiple stories
        stories = [
            Story.objects.create(title=f"Story {i}", content=f"Content {i}")
            for i in range(3)
        ]
        
        # Mock OpenAI response
        test_embedding = [0.1, 0.2, 0.3] * 512
        mock_response = Mock()
        mock_response.data = [Mock(embedding=test_embedding)]
        mock_openai.return_value.embeddings.create.return_value = mock_response
        
        # Test bulk update
        stats = embedding_service.bulk_update_embeddings(Story, batch_size=2)
        
        self.assertEqual(stats['updated'], 4)  # 3 new + 1 existing
        self.assertEqual(stats['failed'], 0)
        
        # Verify embeddings were created
        for story in Story.objects.all():
            story.refresh_from_db()
            self.assertIsNotNone(story.content_embedding)