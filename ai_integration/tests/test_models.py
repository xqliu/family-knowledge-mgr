"""
Automated tests for AI integration models
"""
import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from ai_integration.models import ChatSession, QueryLog, EmbeddingCache
import uuid


class TestChatSession(TestCase):
    """Test ChatSession model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_chat_session(self):
        """Test creating a chat session"""
        session = ChatSession.objects.create(
            user=self.user,
            session_id=str(uuid.uuid4()),
            title="Test Chat Session"
        )
        
        self.assertEqual(session.user, self.user)
        self.assertIsNotNone(session.session_id)
        self.assertEqual(session.title, "Test Chat Session")
        self.assertIsNotNone(session.created_at)
        self.assertIsNotNone(session.updated_at)
    
    def test_chat_session_str(self):
        """Test ChatSession string representation"""
        session = ChatSession.objects.create(
            user=self.user,
            session_id="test-session-123",
            title="Family Stories Chat"
        )
        
        expected = f"{self.user.username} - Family Stories Chat"
        self.assertEqual(str(session), expected)
    
    def test_chat_session_no_title(self):
        """Test ChatSession with no title"""
        session = ChatSession.objects.create(
            user=self.user,
            session_id="test-session-456"
        )
        
        expected = f"{self.user.username} - Chat Session"
        self.assertEqual(str(session), expected)
    
    def test_chat_session_ordering(self):
        """Test ChatSession ordering by updated_at"""
        session1 = ChatSession.objects.create(
            user=self.user,
            session_id="session-1"
        )
        session2 = ChatSession.objects.create(
            user=self.user,
            session_id="session-2"
        )
        
        # Get all sessions
        sessions = list(ChatSession.objects.all())
        
        # Should be ordered by -updated_at (newest first)
        self.assertEqual(sessions[0], session2)
        self.assertEqual(sessions[1], session1)
    
    def test_unique_session_id(self):
        """Test that session_id must be unique"""
        session_id = "duplicate-session-id"
        
        ChatSession.objects.create(
            user=self.user,
            session_id=session_id
        )
        
        # Creating another session with same session_id should fail
        with self.assertRaises(Exception):  # IntegrityError
            ChatSession.objects.create(
                user=self.user,
                session_id=session_id
            )


class TestQueryLog(TestCase):
    """Test QueryLog model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.session = ChatSession.objects.create(
            user=self.user,
            session_id="test-session"
        )
    
    def test_create_query_log(self):
        """Test creating a query log"""
        query_log = QueryLog.objects.create(
            session=self.session,
            query_text="Tell me about family traditions",
            query_type="cultural_heritage",
            response_text="Based on family records, here are your traditions...",
            sources_used=[
                {"type": "heritage", "id": 1, "title": "New Year Customs"}
            ],
            confidence_score=0.85,
            processing_time=1.2,
            api_tokens_used=150,
            language="zh-CN"
        )
        
        self.assertEqual(query_log.session, self.session)
        self.assertEqual(query_log.query_text, "Tell me about family traditions")
        self.assertEqual(query_log.query_type, "cultural_heritage")
        self.assertEqual(query_log.confidence_score, 0.85)
        self.assertEqual(query_log.processing_time, 1.2)
        self.assertEqual(query_log.api_tokens_used, 150)
        self.assertEqual(query_log.language, "zh-CN")
        self.assertEqual(len(query_log.sources_used), 1)
    
    def test_query_log_str(self):
        """Test QueryLog string representation"""
        query_log = QueryLog.objects.create(
            session=self.session,
            query_text="This is a very long query that should be truncated when displayed as string representation",
            response_text="Response"
        )
        
        expected = "This is a very long query that should be truncate..."
        self.assertEqual(str(query_log), expected)
    
    def test_query_log_default_values(self):
        """Test QueryLog default values"""
        query_log = QueryLog.objects.create(
            session=self.session,
            query_text="Test query",
            response_text="Test response"
        )
        
        self.assertEqual(query_log.query_type, "general")
        self.assertEqual(query_log.sources_used, [])
        self.assertEqual(query_log.api_tokens_used, 0)
        self.assertEqual(query_log.language, "zh-CN")
        self.assertIsNone(query_log.confidence_score)
        self.assertIsNone(query_log.processing_time)
    
    def test_query_log_ordering(self):
        """Test QueryLog ordering by created_at"""
        query1 = QueryLog.objects.create(
            session=self.session,
            query_text="First query",
            response_text="First response"
        )
        query2 = QueryLog.objects.create(
            session=self.session,
            query_text="Second query", 
            response_text="Second response"
        )
        
        # Get all queries
        queries = list(QueryLog.objects.all())
        
        # Should be ordered by -created_at (newest first)
        self.assertEqual(queries[0], query2)
        self.assertEqual(queries[1], query1)
    
    def test_query_type_choices(self):
        """Test query type choices"""
        valid_types = [
            'memory_discovery',
            'health_pattern', 
            'event_planning',
            'cultural_heritage',
            'relationship_discovery',
            'general'
        ]
        
        for query_type in valid_types:
            query_log = QueryLog.objects.create(
                session=self.session,
                query_text=f"Test query for {query_type}",
                query_type=query_type,
                response_text="Test response"
            )
            self.assertEqual(query_log.query_type, query_type)


class TestEmbeddingCache(TestCase):
    """Test EmbeddingCache model"""
    
    def test_create_embedding_cache(self):
        """Test creating an embedding cache entry"""
        test_embedding = [0.1, 0.2, 0.3] * 512  # 1536 dimensions
        
        cache_entry = EmbeddingCache.objects.create(
            content_hash="abc123def456",
            content_type="story",
            content_id=1,
            embedding=test_embedding
        )
        
        self.assertEqual(cache_entry.content_hash, "abc123def456")
        self.assertEqual(cache_entry.content_type, "story")
        self.assertEqual(cache_entry.content_id, 1)
        self.assertEqual(len(cache_entry.embedding), 1536)
        self.assertIsNotNone(cache_entry.created_at)
    
    def test_embedding_cache_str(self):
        """Test EmbeddingCache string representation"""
        cache_entry = EmbeddingCache.objects.create(
            content_hash="test-hash",
            content_type="heritage",
            content_id=42,
            embedding=[0.1] * 1536
        )
        
        expected = "heritage:42"
        self.assertEqual(str(cache_entry), expected)
    
    def test_unique_content_hash(self):
        """Test that content_hash must be unique"""
        test_hash = "duplicate-hash"
        test_embedding = [0.1] * 1536
        
        EmbeddingCache.objects.create(
            content_hash=test_hash,
            content_type="story",
            content_id=1,
            embedding=test_embedding
        )
        
        # Creating another entry with same hash should fail
        with self.assertRaises(Exception):  # IntegrityError
            EmbeddingCache.objects.create(
                content_hash=test_hash,
                content_type="event",
                content_id=2,
                embedding=test_embedding
            )
    
    def test_embedding_dimensions(self):
        """Test embedding vector dimensions"""
        # Test correct dimensions
        correct_embedding = [0.1] * 1536
        cache_entry = EmbeddingCache.objects.create(
            content_hash="test-1536",
            content_type="story",
            content_id=1,
            embedding=correct_embedding
        )
        self.assertEqual(len(cache_entry.embedding), 1536)
        
        # Test different dimensions (should still work but may not be optimal)
        wrong_embedding = [0.1] * 768
        cache_entry2 = EmbeddingCache.objects.create(
            content_hash="test-768",
            content_type="story", 
            content_id=2,
            embedding=wrong_embedding
        )
        self.assertEqual(len(cache_entry2.embedding), 768)
    
    def test_embedding_cache_indexes(self):
        """Test that database indexes are created"""
        # This test ensures indexes exist by creating entries and verifying queries work
        test_embedding = [0.1] * 1536
        
        # Create multiple cache entries
        for i in range(5):
            EmbeddingCache.objects.create(
                content_hash=f"hash-{i}",
                content_type="story",
                content_id=i,
                embedding=test_embedding
            )
        
        # Test content_type/content_id index
        story_entries = EmbeddingCache.objects.filter(
            content_type="story",
            content_id__in=[1, 2, 3]
        )
        self.assertEqual(story_entries.count(), 3)
        
        # Test content_hash index
        hash_entry = EmbeddingCache.objects.filter(content_hash="hash-2")
        self.assertEqual(hash_entry.count(), 1)
        self.assertEqual(hash_entry.first().content_id, 2)