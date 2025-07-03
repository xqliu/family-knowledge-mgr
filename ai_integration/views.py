from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from .services.rag_service import rag_service
from .services.search_service import search_service
from .models import ChatSession, QueryLog

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def chat_endpoint(request):
    """AI聊天接口 - 使用RAG生成智能回答"""
    try:
        data = json.loads(request.body)
        query = data.get('query', '')
        session_id = data.get('session_id', '')
        
        if not query.strip():
            return JsonResponse({'error': 'Query cannot be empty'}, status=400)
        
        # 使用RAG服务生成回答
        rag_response = rag_service.generate_response(query)
        
        # 记录查询日志
        if session_id:
            try:
                session = ChatSession.objects.get(session_id=session_id)
                QueryLog.objects.create(
                    session=session,
                    query_text=query,
                    response_text=rag_response['response'],
                    query_type=rag_response['metadata']['query_type'],
                    confidence=rag_response['metadata']['confidence'],
                    processing_time=rag_response['metadata']['processing_time']
                )
            except ChatSession.DoesNotExist:
                logger.warning(f"Session not found: {session_id}")
        
        return JsonResponse(rag_response)
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def semantic_search(request):
    """语义搜索接口 - 直接搜索而不生成AI回答"""
    try:
        data = json.loads(request.body)
        query = data.get('query', '')
        limit = data.get('limit', 10)
        threshold = data.get('threshold', 0.6)
        
        if not query.strip():
            return JsonResponse({'error': 'Query cannot be empty'}, status=400)
        
        # 使用搜索服务进行语义搜索
        search_results = search_service.semantic_search(
            query=query,
            limit=limit,
            similarity_threshold=threshold
        )
        
        response = {
            'query': query,
            'results': search_results,
            'count': len(search_results),
            'threshold': threshold
        }
        
        return JsonResponse(response)
    except Exception as e:
        logger.error(f"Search endpoint error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
