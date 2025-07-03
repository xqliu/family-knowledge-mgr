"""
Automated tests for search service
"""
import pytest
from unittest.mock import patch, Mock
from django.test import TestCase
from family.models import Story, Event, Heritage, Health, Person, Location
from ai_integration.services.search_service import search_service
from ai_integration.models import EmbeddingCache


class TestSearchService(TestCase):
    """Test search service functionality"""
    
    def setUp(self):
        """Set up test data with embeddings"""
        # Create test people
        self.grandma = Person.objects.create(
            name="Liu Grandma",
            bio="Traditional cook, storyteller"
        )
        
        self.grandpa = Person.objects.create(
            name="Liu Grandpa", 
            bio="War veteran, loves family"
        )
        
        # Create test location
        self.home = Location.objects.create(
            name="Family Home",
            location_type="home"
        )
        
        # Create test stories with mock embeddings
        self.cooking_story = Story.objects.create(
            title="Grandma's Dumplings",
            content="Every Chinese New Year, grandma makes traditional dumplings...",
            story_type="tradition",
            content_embedding=[0.1, 0.2, 0.3] * 512,  # Mock embedding
        )
        self.cooking_story.people.add(self.grandma)
        
        self.war_story = Story.objects.create(
            title="Grandpa's War Stories", 
            content="During the war, grandpa served as a communications officer...",
            story_type="memory",
            content_embedding=[0.9, 0.8, 0.7] * 512,  # Different embedding
        )
        self.war_story.people.add(self.grandpa)
        
        # Create test events
        self.reunion = Event.objects.create(
            name="Family Reunion 2023",
            description="Annual gathering with all relatives, lots of traditional food",
            event_type="reunion",
            start_date="2023-12-25T10:00:00Z",
            location=self.home,
            content_embedding=[0.2, 0.3, 0.4] * 512,
        )
        self.reunion.participants.add(self.grandma, self.grandpa)
        
        # Create test heritage
        self.recipe = Heritage.objects.create(
            title="Secret Dumpling Recipe",
            description="Traditional family recipe passed down for generations...",
            heritage_type="recipe",
            origin_person=self.grandma,
            importance=4,
            content_embedding=[0.15, 0.25, 0.35] * 512,
        )
        
        # Create test health record
        self.health_record = Health.objects.create(
            person=self.grandpa,
            title="Heart Condition",
            description="Family history of heart disease, requires monitoring",
            record_type="genetic",
            date="2023-01-01",
            is_hereditary=True,
            content_embedding=[0.7, 0.6, 0.5] * 512,
        )
    
    @patch('ai_integration.services.search_service.embedding_service')
    def test_semantic_search_success(self, mock_embedding_service):
        """Test successful semantic search"""
        # Mock query embedding similar to cooking content
        query_embedding = [0.12, 0.22, 0.32] * 512
        mock_embedding_service.generate_embedding.return_value = query_embedding
        
        # Test search
        results = search_service.semantic_search("traditional cooking recipes", limit=5)
        
        self.assertGreater(len(results), 0)
        
        # Should find cooking-related content first
        result_titles = [r['title'] for r in results]
        self.assertIn("Grandma's Dumplings", result_titles)
        
        # Check result format
        first_result = results[0]
        self.assertIn('id', first_result)
        self.assertIn('title', first_result)
        self.assertIn('content_type', first_result)
        self.assertIn('similarity', first_result)
    
    @patch('ai_integration.services.search_service.embedding_service')
    def test_semantic_search_empty_query(self, mock_embedding_service):
        """Test search with empty query"""
        results = search_service.semantic_search("")
        self.assertEqual(len(results), 0)
        
        results = search_service.semantic_search("   ")
        self.assertEqual(len(results), 0)
    
    @patch('ai_integration.services.search_service.embedding_service')
    def test_semantic_search_no_embedding(self, mock_embedding_service):
        """Test search when query embedding fails"""
        mock_embedding_service.generate_embedding.return_value = None
        
        results = search_service.semantic_search("test query")
        self.assertEqual(len(results), 0)
    
    @patch('ai_integration.services.search_service.embedding_service')
    def test_semantic_search_specific_models(self, mock_embedding_service):
        """Test search limited to specific model types"""
        query_embedding = [0.5, 0.5, 0.5] * 512
        mock_embedding_service.generate_embedding.return_value = query_embedding
        
        # Search only stories
        results = search_service.semantic_search("family", model_types=['story'])
        
        for result in results:
            self.assertEqual(result['content_type'], 'story')
    
    def test_format_search_result_story(self):
        """Test search result formatting for Story model"""
        # Add similarity attribute (normally added by search query)
        self.cooking_story.similarity = 0.85
        
        result = search_service._format_search_result(self.cooking_story)
        
        expected_fields = ['id', 'title', 'content', 'story_type', 'people', 'similarity', 'created_at']
        for field in expected_fields:
            self.assertIn(field, result)
        
        self.assertEqual(result['id'], self.cooking_story.id)
        self.assertEqual(result['title'], self.cooking_story.title)
        self.assertEqual(result['story_type'], self.cooking_story.story_type)
        self.assertEqual(result['similarity'], 0.85)
        self.assertIn(self.grandma.name, result['people'])
    
    def test_format_search_result_event(self):
        """Test search result formatting for Event model"""
        self.reunion.similarity = 0.75
        
        result = search_service._format_search_result(self.reunion)
        
        expected_fields = ['id', 'title', 'content', 'event_type', 'start_date', 'location', 'participants', 'similarity']
        for field in expected_fields:
            self.assertIn(field, result)
        
        self.assertEqual(result['event_type'], self.reunion.event_type)
        self.assertEqual(result['location'], self.home.name)
        self.assertIn(self.grandma.name, result['participants'])
    
    def test_format_search_result_heritage(self):
        """Test search result formatting for Heritage model"""
        self.recipe.similarity = 0.90
        
        result = search_service._format_search_result(self.recipe)
        
        expected_fields = ['id', 'title', 'content', 'heritage_type', 'importance', 'origin_person', 'similarity']
        for field in expected_fields:
            self.assertIn(field, result)
        
        self.assertEqual(result['heritage_type'], self.recipe.heritage_type)
        self.assertEqual(result['importance'], self.recipe.importance)
        self.assertEqual(result['origin_person'], self.grandma.name)
    
    def test_format_search_result_health(self):
        """Test search result formatting for Health model"""
        self.health_record.similarity = 0.80
        
        result = search_service._format_search_result(self.health_record)
        
        expected_fields = ['id', 'title', 'content', 'record_type', 'person', 'date', 'is_hereditary', 'similarity']
        for field in expected_fields:
            self.assertIn(field, result)
        
        self.assertEqual(result['record_type'], self.health_record.record_type)
        self.assertEqual(result['person'], self.grandpa.name)
        self.assertEqual(result['is_hereditary'], True)
    
    @patch('ai_integration.services.search_service.embedding_service')
    def test_search_by_category(self, mock_embedding_service):
        """Test category-specific search"""
        query_embedding = [0.3, 0.3, 0.3] * 512
        mock_embedding_service.generate_embedding.return_value = query_embedding
        
        # Test stories category
        results = search_service.search_by_category("family", "stories")
        for result in results:
            self.assertEqual(result['content_type'], 'story')
        
        # Test heritage category
        results = search_service.search_by_category("traditions", "heritage")
        for result in results:
            self.assertEqual(result['content_type'], 'heritage')
        
        # Test invalid category
        results = search_service.search_by_category("test", "invalid_category")
        self.assertEqual(len(results), 0)
    
    def test_find_related_content(self):
        """Test finding content related to a specific item"""
        # Find content related to cooking story
        results = search_service.find_related_content(
            self.cooking_story.id, 
            'story', 
            limit=3
        )
        
        # Should not include the reference story itself
        result_ids = [r['id'] for r in results if r['content_type'] == 'story']
        self.assertNotIn(self.cooking_story.id, result_ids)
        
        # Should find related content (recipe, reunion with food)
        result_titles = [r['title'] for r in results]
        self.assertIn("Secret Dumpling Recipe", result_titles)
    
    def test_find_related_content_invalid(self):
        """Test finding related content with invalid parameters"""
        # Invalid content type
        results = search_service.find_related_content(1, 'invalid_type')
        self.assertEqual(len(results), 0)
        
        # Non-existent content ID
        results = search_service.find_related_content(99999, 'story')
        self.assertEqual(len(results), 0)
    
    def test_keyword_search(self):
        """Test fallback keyword search"""
        results = search_service.keyword_search("dumplings")
        
        # Should find cooking story
        result_titles = [r['title'] for r in results]
        self.assertIn("Grandma's Dumplings", result_titles)
        
        # Should have default similarity score
        for result in results:
            self.assertEqual(result['similarity'], 0.5)
    
    def test_keyword_search_specific_models(self):
        """Test keyword search limited to specific models"""
        results = search_service.keyword_search("family", model_types=['event'])
        
        for result in results:
            self.assertEqual(result['content_type'], 'event')
    
    def test_content_truncation(self):
        """Test that long content is properly truncated"""
        long_content = "A" * 300  # Content longer than 200 chars
        long_story = Story.objects.create(
            title="Long Story",
            content=long_content,
            content_embedding=[0.4, 0.4, 0.4] * 512,
        )
        long_story.similarity = 0.7
        
        result = search_service._format_search_result(long_story)
        
        # Content should be truncated to 200 chars + "..."
        self.assertEqual(len(result['content']), 203)
        self.assertTrue(result['content'].endswith('...'))
    
    def test_people_list_limit(self):
        """Test that people/participants lists are limited to 3"""
        # Add more people to story
        extra_people = [
            Person.objects.create(name=f"Person {i}")
            for i in range(5)
        ]
        for person in extra_people:
            self.cooking_story.people.add(person)
        
        self.cooking_story.similarity = 0.8
        result = search_service._format_search_result(self.cooking_story)
        
        # Should limit to 3 people
        self.assertLessEqual(len(result['people']), 3)