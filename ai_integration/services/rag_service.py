"""
RAG (Retrieval-Augmented Generation) service
Combines semantic search with AI response generation
"""
import logging
import time
from typing import List, Dict, Any, Optional
from django.conf import settings
import anthropic
from .search_service import search_service
from .embedding_service import embedding_service

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG-based family knowledge queries"""
    
    def __init__(self):
        self.search_service = search_service
        self.embedding_service = embedding_service
        self.anthropic_client = anthropic.Anthropic(
            api_key=getattr(settings, 'ANTHROPIC_API_KEY', '')
        )
    
    def generate_response(
        self, 
        query: str, 
        max_results: int = 5,
        similarity_threshold: float = 0.6
    ) -> Dict[str, Any]:
        """
        Generate RAG response for family knowledge query
        
        Args:
            query: User's natural language query
            max_results: Maximum search results to include in context
            similarity_threshold: Minimum similarity for search results
            
        Returns:
            Dict with response, sources, and metadata
        """
        start_time = time.time()
        
        try:
            # Step 1: Determine query type
            query_type = self._classify_query(query)
            
            # Step 2: Semantic search for relevant content
            search_results = self.search_service.semantic_search(
                query=query,
                limit=max_results,
                similarity_threshold=similarity_threshold
            )
            
            # Step 3: Generate context from search results
            context = self._build_context(search_results, query_type)
            
            # Step 4: Generate AI response
            if context:
                response_text = self._generate_ai_response(query, context, query_type)
            else:
                response_text = self._generate_fallback_response(query, query_type)
            
            # Step 5: Format response
            processing_time = time.time() - start_time
            
            return {
                'query': query,
                'response': response_text,
                'sources': self._format_sources(search_results),
                'metadata': {
                    'query_type': query_type,
                    'confidence': self._calculate_confidence(search_results),
                    'processing_time': round(processing_time, 2),
                    'sources_count': len(search_results),
                    'language': self._detect_language(query)
                }
            }
            
        except Exception as e:
            logger.error(f"RAG generation failed: {e}")
            return self._generate_error_response(query, str(e))
    
    def _classify_query(self, query: str) -> str:
        """Classify query type based on content"""
        query_lower = query.lower()
        
        # Health-related keywords
        health_keywords = ['health', 'medical', 'illness', 'disease', 'hereditary', 'genetic', '健康', '疾病', '遗传']
        if any(keyword in query_lower for keyword in health_keywords):
            return 'health_pattern'
        
        # Event planning keywords
        event_keywords = ['celebration', 'party', 'reunion', 'birthday', 'wedding', '庆祝', '聚会', '生日']
        if any(keyword in query_lower for keyword in event_keywords):
            return 'event_planning'
        
        # Heritage/tradition keywords
        heritage_keywords = ['tradition', 'heritage', 'recipe', 'values', 'wisdom', '传统', '文化', '智慧']
        if any(keyword in query_lower for keyword in heritage_keywords):
            return 'cultural_heritage'
        
        # Relationship keywords
        relationship_keywords = ['family', 'relative', 'relationship', 'cousin', '亲戚', '家人', '关系']
        if any(keyword in query_lower for keyword in relationship_keywords):
            return 'relationship_discovery'
        
        # Memory/story keywords
        memory_keywords = ['story', 'memory', 'remember', 'childhood', 'past', '故事', '回忆', '童年']
        if any(keyword in query_lower for keyword in memory_keywords):
            return 'memory_discovery'
        
        return 'general'
    
    def _build_context(self, search_results: List[Dict], query_type: str) -> str:
        """Build context string from search results"""
        if not search_results:
            return ""
        
        context_parts = []
        context_parts.append("Based on family records, here is relevant information:\n")
        
        for i, result in enumerate(search_results, 1):
            content_type = result.get('content_type', 'unknown')
            title = result.get('title', 'Untitled')
            content = result.get('content', '')
            similarity = result.get('similarity', 0)
            
            # Format based on content type
            if content_type == 'story':
                context_parts.append(f"{i}. Family Story: \"{title}\"")
                context_parts.append(f"   Content: {content}")
                
                # Add people if available
                people = result.get('people', [])
                if people:
                    context_parts.append(f"   People involved: {', '.join(people[:3])}")
                    
            elif content_type == 'event':
                context_parts.append(f"{i}. Family Event: \"{title}\"")
                context_parts.append(f"   Description: {content}")
                
                # Add event details
                event_type = result.get('event_type', '')
                location = result.get('location', '')
                if event_type:
                    context_parts.append(f"   Type: {event_type}")
                if location:
                    context_parts.append(f"   Location: {location}")
                    
            elif content_type == 'heritage':
                context_parts.append(f"{i}. Family Heritage: \"{title}\"")
                context_parts.append(f"   Description: {content}")
                
                # Add heritage details
                heritage_type = result.get('heritage_type', '')
                importance = result.get('importance', '')
                origin_person = result.get('origin_person', '')
                if heritage_type:
                    context_parts.append(f"   Type: {heritage_type}")
                if origin_person:
                    context_parts.append(f"   Origin: {origin_person}")
                    
            elif content_type == 'health':
                context_parts.append(f"{i}. Health Record: \"{title}\"")
                context_parts.append(f"   Details: {content}")
                
                # Add health details
                person = result.get('person', '')
                is_hereditary = result.get('is_hereditary', False)
                if person:
                    context_parts.append(f"   Person: {person}")
                if is_hereditary:
                    context_parts.append(f"   Hereditary: Yes")
            
            context_parts.append(f"   Relevance: {similarity:.2f}\n")
        
        return "\n".join(context_parts)
    
    def _generate_ai_response(self, query: str, context: str, query_type: str) -> str:
        """Generate AI response using Anthropic Claude"""
        try:
            # Create system prompt based on query type
            system_prompt = self._get_system_prompt(query_type)
            
            # Create user message with context
            user_message = f"""Family Knowledge Query: {query}

{context}

Please provide a helpful, warm, and family-focused response based on the information above. 
Speak as if you're a knowledgeable family member sharing precious memories and insights.
If the query is in Chinese, please respond in Chinese. Otherwise, respond in English.
"""

            # Generate response with Claude
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return self._generate_fallback_response(query, query_type)
    
    def _get_system_prompt(self, query_type: str) -> str:
        """Get system prompt based on query type"""
        base_prompt = """You are a wise and caring family knowledge keeper. You help family members 
connect with their heritage, stories, and relationships. You speak with warmth, respect for 
elders, and deep appreciation for family bonds."""
        
        type_specific = {
            'memory_discovery': " Focus on bringing family stories to life with vivid details and emotional context.",
            'health_pattern': " Provide thoughtful health insights while emphasizing the importance of professional medical advice.",
            'event_planning': " Suggest meaningful ways to celebrate that honor family traditions and create lasting memories.",
            'cultural_heritage': " Share insights about family traditions and values with deep respect for cultural heritage.",
            'relationship_discovery': " Help family members understand their connections and the importance of family bonds.",
            'general': " Provide helpful and family-focused guidance based on the available information."
        }
        
        return base_prompt + type_specific.get(query_type, type_specific['general'])
    
    def _generate_fallback_response(self, query: str, query_type: str) -> str:
        """Generate fallback response when no relevant content is found"""
        language = self._detect_language(query)
        
        if language == 'zh-CN':
            fallback_responses = {
                'memory_discovery': "很抱歉，我在家庭记录中没有找到与您的问题直接相关的故事。不过，这可能是一个好机会来记录新的家庭记忆。您愿意分享一些相关的故事吗？",
                'health_pattern': "关于您询问的健康问题，我在现有的家庭健康记录中没有找到相关信息。建议您咨询专业医生，并考虑将重要的健康信息添加到家庭记录中。",
                'event_planning': "虽然我没有找到关于类似活动的具体记录，但我建议您可以创造新的家庭传统。考虑一下什么样的庆祝方式最能体现您家庭的价值观和喜好。",
                'cultural_heritage': "这是一个很好的问题！虽然我没有找到相关的传统记录，但这正是开始记录家庭文化传承的好时机。",
                'relationship_discovery': "关于家庭关系的问题，我建议您可以与长辈交流，了解更多家族史。同时，将这些珍贵的关系信息记录下来会很有价值。",
                'general': "很抱歉，我没有找到与您的问题直接相关的家庭信息。不过，我很乐意帮助您思考如何收集和记录相关信息。"
            }
        else:
            fallback_responses = {
                'memory_discovery': "I couldn't find specific family stories related to your question in our records. This might be a wonderful opportunity to capture new family memories. Would you like to share some related stories?",
                'health_pattern': "I don't have specific health information related to your question in our family records. I recommend consulting with healthcare professionals and considering adding important health information to your family records.",
                'event_planning': "While I don't have records of similar events, this could be a chance to create new family traditions. Consider what type of celebration would best reflect your family's values and preferences.",
                'cultural_heritage': "That's a wonderful question! While I don't have specific records about this tradition, this could be a perfect time to start documenting your family's cultural heritage.",
                'relationship_discovery': "For questions about family relationships, I suggest speaking with elder family members to learn more about your family history. Recording these precious connections would be very valuable.",
                'general': "I couldn't find information directly related to your question in our family records. However, I'd be happy to help you think about how to gather and record relevant information."
            }
        
        return fallback_responses.get(query_type, fallback_responses['general'])
    
    def _detect_language(self, query: str) -> str:
        """Simple language detection"""
        # Check for Chinese characters
        chinese_chars = sum(1 for char in query if '\u4e00' <= char <= '\u9fff')
        if chinese_chars > len(query) * 0.3:  # More than 30% Chinese characters
            return 'zh-CN'
        return 'en-US'
    
    def _calculate_confidence(self, search_results: List[Dict]) -> float:
        """Calculate confidence score based on search results"""
        if not search_results:
            return 0.0
        
        # Average similarity of top 3 results
        top_similarities = [r.get('similarity', 0) for r in search_results[:3]]
        avg_similarity = sum(top_similarities) / len(top_similarities)
        
        # Boost confidence if we have multiple good results
        count_boost = min(len(search_results) * 0.1, 0.2)
        
        return min(avg_similarity + count_boost, 1.0)
    
    def _format_sources(self, search_results: List[Dict]) -> List[Dict]:
        """Format search results as sources"""
        sources = []
        
        for result in search_results:
            source = {
                'type': result.get('content_type', 'unknown'),
                'id': result.get('id'),
                'title': result.get('title', 'Untitled'),
                'relevance': round(result.get('similarity', 0), 3)
            }
            
            # Add type-specific fields
            content_type = result.get('content_type')
            if content_type == 'story':
                source['story_type'] = result.get('story_type', '')
                source['people'] = result.get('people', [])[:2]  # Limit to 2 people
            elif content_type == 'event':
                source['event_type'] = result.get('event_type', '')
                source['date'] = result.get('start_date', '')
            elif content_type == 'heritage':
                source['heritage_type'] = result.get('heritage_type', '')
                source['importance'] = result.get('importance', '')
            elif content_type == 'health':
                source['person'] = result.get('person', '')
                source['is_hereditary'] = result.get('is_hereditary', False)
            
            sources.append(source)
        
        return sources
    
    def _generate_error_response(self, query: str, error: str) -> Dict[str, Any]:
        """Generate error response"""
        language = self._detect_language(query)
        
        if language == 'zh-CN':
            error_message = "抱歉，处理您的问题时遇到了技术问题。请稍后再试，或者联系系统管理员。"
        else:
            error_message = "I'm sorry, but I encountered a technical issue while processing your question. Please try again later or contact the system administrator."
        
        return {
            'query': query,
            'response': error_message,
            'sources': [],
            'metadata': {
                'query_type': 'error',
                'confidence': 0.0,
                'processing_time': 0.0,
                'sources_count': 0,
                'language': language,
                'error': error
            }
        }


# Global service instance
rag_service = RAGService()