"""
Semantic search service using pgvector
Searches across family content using vector similarity
"""
import logging
from typing import List, Dict, Any, Union, Optional
from django.db import models
from django.db.models import Q, F
from pgvector.django import CosineDistance, L2Distance
from family.models import Story, Event, Heritage, Health, Person
from .embedding_service import embedding_service

logger = logging.getLogger(__name__)


class SearchService:
    """Service for semantic search across family content"""
    
    # Model mappings for search
    SEARCHABLE_MODELS = {
        'story': Story,
        'event': Event, 
        'heritage': Heritage,
        'health': Health,
    }
    
    def __init__(self):
        self.embedding_service = embedding_service
    
    def semantic_search(
        self, 
        query: str, 
        model_types: Optional[List[str]] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search across family content
        
        Args:
            query: Search query text
            model_types: List of model types to search ('story', 'event', etc.)
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of search results with metadata
        """
        if not query or not query.strip():
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_service.generate_embedding(query)
        if not query_embedding:
            logger.error("Failed to generate query embedding")
            return []
        
        # Default to all searchable models
        if not model_types:
            model_types = list(self.SEARCHABLE_MODELS.keys())
        
        all_results = []
        
        # Search each model type
        for model_type in model_types:
            if model_type not in self.SEARCHABLE_MODELS:
                logger.warning(f"Unknown model type: {model_type}")
                continue
                
            model_class = self.SEARCHABLE_MODELS[model_type]
            results = self._search_model(
                model_class, 
                query_embedding, 
                limit, 
                similarity_threshold
            )
            
            # Add model type to results
            for result in results:
                result['content_type'] = model_type
                
            all_results.extend(results)
        
        # Sort by similarity score and limit
        all_results.sort(key=lambda x: x['similarity'], reverse=True)
        return all_results[:limit]
    
    def _search_model(
        self, 
        model_class: models.Model, 
        query_embedding: List[float],
        limit: int,
        similarity_threshold: float
    ) -> List[Dict[str, Any]]:
        """Search a specific model class using vector similarity"""
        try:
            # Use cosine distance for similarity search
            results = model_class.objects.filter(
                content_embedding__isnull=False
            ).annotate(
                distance=CosineDistance('content_embedding', query_embedding)
            ).annotate(
                similarity=1 - F('distance')  # Convert distance to similarity
            ).filter(
                similarity__gte=similarity_threshold
            ).order_by('-similarity')[:limit]
            
            search_results = []
            for obj in results:
                result = self._format_search_result(obj)
                search_results.append(result)
            
            logger.info(f"Found {len(search_results)} results in {model_class.__name__}")
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed for {model_class.__name__}: {e}")
            return []
    
    def _format_search_result(self, obj) -> Dict[str, Any]:
        """Format model instance as search result"""
        model_name = type(obj).__name__.lower()
        
        # Extract relevant fields based on model type
        if model_name == 'story':
            return {
                'id': obj.id,
                'title': obj.title,
                'content': obj.content[:200] + '...' if len(obj.content) > 200 else obj.content,
                'story_type': obj.story_type,
                'date_occurred': obj.date_occurred.isoformat() if obj.date_occurred else None,
                'people': [p.name for p in obj.people.all()[:3]],  # Limit to first 3
                'similarity': float(obj.similarity),
                'created_at': obj.created_at.isoformat(),
            }
        elif model_name == 'event':
            return {
                'id': obj.id,
                'title': obj.name,
                'content': obj.description[:200] + '...' if obj.description and len(obj.description) > 200 else obj.description,
                'event_type': obj.event_type,
                'start_date': obj.start_date.isoformat(),
                'location': obj.location.name if obj.location else None,
                'participants': [p.name for p in obj.participants.all()[:3]],
                'similarity': float(obj.similarity),
                'created_at': obj.created_at.isoformat(),
            }
        elif model_name == 'heritage':
            return {
                'id': obj.id,
                'title': obj.title,
                'content': obj.description[:200] + '...' if len(obj.description) > 200 else obj.description,
                'heritage_type': obj.heritage_type,
                'importance': obj.importance,
                'origin_person': obj.origin_person.name if obj.origin_person else None,
                'similarity': float(obj.similarity),
                'created_at': obj.created_at.isoformat(),
            }
        elif model_name == 'health':
            return {
                'id': obj.id,
                'title': obj.title,
                'content': obj.description[:200] + '...' if len(obj.description) > 200 else obj.description,
                'record_type': obj.record_type,
                'person': obj.person.name,
                'date': obj.date.isoformat(),
                'is_hereditary': obj.is_hereditary,
                'similarity': float(obj.similarity),
                'created_at': obj.created_at.isoformat(),
            }
        else:
            # Generic format
            return {
                'id': obj.id,
                'title': str(obj),
                'content': '',
                'similarity': float(obj.similarity),
                'created_at': obj.created_at.isoformat() if hasattr(obj, 'created_at') else None,
            }
    
    def search_by_category(
        self, 
        query: str, 
        category: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search within a specific category/model type
        
        Args:
            query: Search query
            category: Category to search ('stories', 'events', 'heritage', 'health')
            limit: Maximum results
        """
        # Map category names to model types
        category_mapping = {
            'stories': 'story',
            'events': 'event',
            'heritage': 'heritage',
            'health': 'health',
            'memories': 'story',  # Alias
            'traditions': 'heritage',  # Alias
        }
        
        model_type = category_mapping.get(category.lower())
        if not model_type:
            logger.warning(f"Unknown category: {category}")
            return []
        
        return self.semantic_search(query, [model_type], limit)
    
    def find_related_content(
        self, 
        content_id: int, 
        content_type: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find content similar to a given piece of content
        
        Args:
            content_id: ID of the reference content
            content_type: Type of reference content
            limit: Maximum results
        """
        if content_type not in self.SEARCHABLE_MODELS:
            return []
        
        try:
            # Get the reference object
            model_class = self.SEARCHABLE_MODELS[content_type]
            ref_obj = model_class.objects.get(id=content_id)
            
            if not ref_obj.content_embedding:
                logger.warning(f"No embedding for {content_type}:{content_id}")
                return []
            
            # Search for similar content (excluding the reference object)
            all_results = []
            for model_type, search_model in self.SEARCHABLE_MODELS.items():
                results = search_model.objects.filter(
                    content_embedding__isnull=False
                ).exclude(
                    id=content_id if model_type == content_type else None
                ).annotate(
                    distance=CosineDistance('content_embedding', ref_obj.content_embedding)
                ).annotate(
                    similarity=1 - F('distance')
                ).order_by('-similarity')[:limit]
                
                for obj in results:
                    result = self._format_search_result(obj)
                    result['content_type'] = model_type
                    all_results.append(result)
            
            # Sort and limit
            all_results.sort(key=lambda x: x['similarity'], reverse=True)
            return all_results[:limit]
            
        except Exception as e:
            logger.error(f"Failed to find related content: {e}")
            return []
    
    def keyword_search(
        self, 
        query: str, 
        model_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fallback keyword search when semantic search fails
        """
        if not model_types:
            model_types = list(self.SEARCHABLE_MODELS.keys())
        
        all_results = []
        
        for model_type in model_types:
            if model_type not in self.SEARCHABLE_MODELS:
                continue
                
            model_class = self.SEARCHABLE_MODELS[model_type]
            
            # Build keyword search query
            search_q = Q()
            
            if model_type == 'story':
                search_q = Q(title__icontains=query) | Q(content__icontains=query)
            elif model_type == 'event':
                search_q = Q(name__icontains=query) | Q(description__icontains=query)
            elif model_type == 'heritage':
                search_q = Q(title__icontains=query) | Q(description__icontains=query)
            elif model_type == 'health':
                search_q = Q(title__icontains=query) | Q(description__icontains=query)
            
            results = model_class.objects.filter(search_q)[:limit]
            
            for obj in results:
                result = self._format_search_result(obj)
                result['content_type'] = model_type
                result['similarity'] = 0.5  # Default similarity for keyword search
                all_results.append(result)
        
        return all_results[:limit]


# Global service instance
search_service = SearchService()