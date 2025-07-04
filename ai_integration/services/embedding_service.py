"""
Embedding generation service for family content
Uses OpenAI text-embedding-3-small (cheaper than Anthropic)
"""
import hashlib
import logging
from typing import List, Optional, Dict, Any
from django.utils import timezone
from django.conf import settings
from django.db import models
from openai import OpenAI
from ..models import EmbeddingCache

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and managing content embeddings"""
    
    def __init__(self):
        self.client = OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', ''))
        self.model = "text-embedding-3-small"  # 1536 dimensions, $0.02/1M tokens
        
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for text content
        
        Args:
            text: Text content to embed
            
        Returns:
            List of embedding vectors or None if failed
        """
        if not text or not text.strip():
            return None
            
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text.strip()
            )
            
            embedding = response.data[0].embedding
            logger.info(f"Generated embedding for text (length: {len(text)})")
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None
    
    def get_content_hash(self, text: str) -> str:
        """Generate SHA256 hash of content for caching"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def get_or_create_embedding(self, text: str, content_type: str, content_id: int) -> Optional[List[float]]:
        """
        Get embedding from cache or generate new one
        
        Args:
            text: Text content to embed
            content_type: Type of content (story, event, heritage, health)
            content_id: ID of the content object
            
        Returns:
            List of embedding vectors or None if failed
        """
        if not text or not text.strip():
            return None
            
        content_hash = self.get_content_hash(text)
        
        # Try to get from cache first
        try:
            cached = EmbeddingCache.objects.get(content_hash=content_hash)
            logger.info(f"Using cached embedding for {content_type}:{content_id}")
            return cached.embedding
        except EmbeddingCache.DoesNotExist:
            pass
        
        # Generate new embedding
        embedding = self.generate_embedding(text)
        if embedding:
            # Cache the embedding
            EmbeddingCache.objects.update_or_create(
                content_hash=content_hash,
                defaults={
                    'content_type': content_type,
                    'content_id': content_id,
                    'embedding': embedding,
                }
            )
            logger.info(f"Cached new embedding for {content_type}:{content_id}")
        
        return embedding
    
    def update_model_embedding(self, instance, force_update: bool = False) -> bool:
        """
        Update embedding for a model instance
        
        Args:
            instance: Model instance with content_embedding field
            force_update: Force regeneration even if embedding exists
            
        Returns:
            True if embedding was updated, False otherwise
        """
        if not hasattr(instance, 'content_embedding'):
            logger.error(f"Model {type(instance).__name__} has no content_embedding field")
            return False
        
        # Determine content field and text
        content_text = self._extract_content_text(instance)
        if not content_text:
            logger.warning(f"No content text found for {type(instance).__name__}:{instance.id}")
            return False
        
        # Check if update needed
        if not force_update and instance.content_embedding and instance.embedding_updated:
            content_hash = self.get_content_hash(content_text)
            try:
                cached = EmbeddingCache.objects.get(content_hash=content_hash)
                if cached.embedding == instance.content_embedding:
                    logger.info(f"Embedding up to date for {type(instance).__name__}:{instance.id}")
                    return False
            except EmbeddingCache.DoesNotExist:
                pass
        
        # Generate/get embedding
        content_type = type(instance).__name__.lower()
        embedding = self.get_or_create_embedding(content_text, content_type, instance.id)
        
        if embedding:
            instance.content_embedding = embedding
            instance.embedding_updated = timezone.now()
            instance.save(update_fields=['content_embedding', 'embedding_updated'])
            logger.info(f"Updated embedding for {content_type}:{instance.id}")
            return True
        
        return False
    
    def _extract_content_text(self, instance) -> str:
        """Extract text content from model instance for embedding"""
        model_name = type(instance).__name__.lower()
        
        if model_name == 'story':
            return f"{instance.title}\n\n{instance.content}"
        elif model_name == 'event':
            return f"{instance.name}\n\n{instance.description}"
        elif model_name == 'heritage':
            return f"{instance.title}\n\n{instance.description}"
        elif model_name == 'health':
            return f"{instance.title}\n\n{instance.description}"
        elif model_name == 'person':
            return instance.bio if instance.bio else instance.name
        else:
            # Try common field names
            for field in ['content', 'description', 'bio', 'title', 'name']:
                if hasattr(instance, field):
                    value = getattr(instance, field)
                    if value:
                        return str(value)
        
        return ""
    
    def bulk_update_embeddings(self, model_class, batch_size: int = 10) -> Dict[str, int]:
        """
        Bulk update embeddings for all instances of a model
        
        Args:
            model_class: Django model class
            batch_size: Number of instances to process at once
            
        Returns:
            Dict with statistics: {'updated': int, 'skipped': int, 'failed': int}
        """
        stats = {'updated': 0, 'skipped': 0, 'failed': 0}
        
        # Get instances that need embedding updates
        instances = model_class.objects.filter(
            models.Q(content_embedding__isnull=True) | 
            models.Q(embedding_updated__isnull=True)
        )
        
        total = instances.count()
        logger.info(f"Bulk updating embeddings for {total} {model_class.__name__} instances")
        
        for i in range(0, total, batch_size):
            batch = instances[i:i + batch_size]
            
            for instance in batch:
                try:
                    if self.update_model_embedding(instance):
                        stats['updated'] += 1
                    else:
                        stats['skipped'] += 1
                except Exception as e:
                    stats['failed'] += 1
                    logger.error(f"Failed to update embedding for {model_class.__name__}:{instance.id}: {e}")
        
        logger.info(f"Bulk update complete: {stats}")
        return stats


# Global service instance
embedding_service = EmbeddingService()