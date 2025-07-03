"""
Automated tests for AI integration signals
"""
from unittest.mock import patch, Mock
from django.test import TestCase
from django.utils import timezone
from family.models import Story, Event, Heritage, Health, Person


class TestEmbeddingSignals(TestCase):
    """Test automatic embedding generation via Django signals"""
    
    def setUp(self):
        """Set up test data"""
        self.person = Person.objects.create(
            name="Test Person",
            bio="Test biography"
        )
    
    @patch('ai_integration.services.embedding_service.embedding_service')
    def test_story_embedding_signal(self, mock_embedding_service):
        """Test that Story creation triggers embedding update"""
        mock_embedding_service.update_model_embedding.return_value = True
        
        # Create story
        story = Story.objects.create(
            title="Test Story",
            content="This is a test story content",
            story_type="memory"
        )
        
        # Verify embedding service was called
        mock_embedding_service.update_model_embedding.assert_called_once_with(
            story, force_update=True
        )
    
    @patch('ai_integration.services.embedding_service.embedding_service')
    def test_story_update_signal(self, mock_embedding_service):
        """Test that Story update triggers embedding update"""
        mock_embedding_service.update_model_embedding.return_value = True
        
        # Create story first
        story = Story.objects.create(
            title="Test Story",
            content="Original content",
            story_type="memory"
        )
        
        # Reset mock to clear creation call
        mock_embedding_service.reset_mock()
        
        # Update story
        story.content = "Updated content"
        story.save()
        
        # Verify embedding service was called for update
        mock_embedding_service.update_model_embedding.assert_called_once_with(
            story, force_update=False
        )
    
    @patch('ai_integration.services.embedding_service.embedding_service')
    def test_event_embedding_signal(self, mock_embedding_service):
        """Test that Event creation triggers embedding update"""
        mock_embedding_service.update_model_embedding.return_value = True
        
        # Create event
        event = Event.objects.create(
            name="Test Event",
            description="This is a test event",
            event_type="birthday",
            start_date=timezone.now()
        )
        
        # Verify embedding service was called
        mock_embedding_service.update_model_embedding.assert_called_once_with(
            event, force_update=True
        )
    
    @patch('ai_integration.services.embedding_service.embedding_service')
    def test_heritage_embedding_signal(self, mock_embedding_service):
        """Test that Heritage creation triggers embedding update"""
        mock_embedding_service.update_model_embedding.return_value = True
        
        # Create heritage
        heritage = Heritage.objects.create(
            title="Test Heritage",
            description="This is a test heritage item",
            heritage_type="tradition",
            importance=3
        )
        
        # Verify embedding service was called
        mock_embedding_service.update_model_embedding.assert_called_once_with(
            heritage, force_update=True
        )
    
    @patch('ai_integration.services.embedding_service.embedding_service')
    def test_health_embedding_signal(self, mock_embedding_service):
        """Test that Health record creation triggers embedding update"""
        mock_embedding_service.update_model_embedding.return_value = True
        
        # Create health record
        health = Health.objects.create(
            person=self.person,
            title="Test Health Record",
            description="This is a test health record",
            record_type="checkup",
            date=timezone.now().date()
        )
        
        # Verify embedding service was called
        mock_embedding_service.update_model_embedding.assert_called_once_with(
            health, force_update=True
        )
    
    @patch('ai_integration.services.embedding_service.embedding_service')
    def test_signal_error_handling(self, mock_embedding_service):
        """Test that signal errors don't break model creation"""
        # Mock service to raise exception
        mock_embedding_service.update_model_embedding.side_effect = Exception("API Error")
        
        # Story creation should still succeed despite embedding error
        story = Story.objects.create(
            title="Test Story",
            content="Test content",
            story_type="memory"
        )
        
        # Verify story was created
        self.assertEqual(story.title, "Test Story")
        self.assertTrue(Story.objects.filter(id=story.id).exists())
        
        # Verify embedding service was called (but failed)
        mock_embedding_service.update_model_embedding.assert_called_once()
    
    @patch('ai_integration.services.embedding_service.embedding_service')
    def test_bulk_create_signals(self, mock_embedding_service):
        """Test signals work with bulk_create operations"""
        mock_embedding_service.update_model_embedding.return_value = True
        
        # Create multiple stories
        stories = [
            Story(title=f"Story {i}", content=f"Content {i}", story_type="memory")
            for i in range(3)
        ]
        
        # Note: bulk_create doesn't trigger signals by default in Django
        # This test documents the current behavior
        Story.objects.bulk_create(stories)
        
        # Signals should NOT be called for bulk_create
        mock_embedding_service.update_model_embedding.assert_not_called()
    
    @patch('ai_integration.services.embedding_service.embedding_service')
    def test_signal_with_empty_content(self, mock_embedding_service):
        """Test signal behavior with empty content"""
        mock_embedding_service.update_model_embedding.return_value = False
        
        # Create story with empty content
        story = Story.objects.create(
            title="",
            content="",
            story_type="memory"
        )
        
        # Verify embedding service was called (even with empty content)
        mock_embedding_service.update_model_embedding.assert_called_once_with(
            story, force_update=True
        )
    
    @patch('ai_integration.services.embedding_service.embedding_service')
    def test_signal_preserves_existing_embeddings(self, mock_embedding_service):
        """Test that signals preserve existing embeddings correctly"""
        mock_embedding_service.update_model_embedding.return_value = True
        
        # Create story with existing embedding
        existing_embedding = [0.1, 0.2, 0.3] * 512
        story = Story.objects.create(
            title="Test Story",
            content="Test content",
            story_type="memory",
            content_embedding=existing_embedding,
            embedding_updated=timezone.now()
        )
        
        # Verify embedding service was called for new creation
        mock_embedding_service.update_model_embedding.assert_called_once_with(
            story, force_update=True
        )
    
    @patch('ai_integration.services.embedding_service.embedding_service')
    def test_multiple_model_signals(self, mock_embedding_service):
        """Test that signals work for multiple model types simultaneously"""
        mock_embedding_service.update_model_embedding.return_value = True
        
        # Create instances of different models
        story = Story.objects.create(
            title="Test Story",
            content="Story content",
            story_type="memory"
        )
        
        event = Event.objects.create(
            name="Test Event",
            description="Event description",
            event_type="birthday",
            start_date=timezone.now()
        )
        
        heritage = Heritage.objects.create(
            title="Test Heritage",
            description="Heritage description",
            heritage_type="tradition",
            importance=2
        )
        
        health = Health.objects.create(
            person=self.person,
            title="Test Health",
            description="Health description",
            record_type="checkup",
            date=timezone.now().date()
        )
        
        # Verify embedding service was called for each model
        self.assertEqual(mock_embedding_service.update_model_embedding.call_count, 4)
        
        # Verify each model was called with force_update=True (creation)
        calls = mock_embedding_service.update_model_embedding.call_args_list
        for call in calls:
            args, kwargs = call
            self.assertTrue(kwargs['force_update'])  # Should be True for creation