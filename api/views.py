from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .decorators import api_login_required
import json


def health_check(request):
    """健康检查端点"""
    return JsonResponse({
        'status': 'ok',
        'message': 'API运行正常'
    })


@api_login_required
@csrf_exempt
@require_http_methods(["GET", "POST"])
def family_overview(request):
    """家庭概览API"""
    if request.method == 'GET':
        # 返回家庭概览数据
        return JsonResponse({
            'family_members': [
                {'id': 1, 'name': '测试用户', 'relationship': '自己'},
            ],
            'recent_stories': [
                {'id': 1, 'title': '欢迎使用家庭知识管理系统', 'date': '2024-12-28'},
            ],
            'stats': {
                'total_members': 1,
                'total_stories': 1,
                'total_photos': 0
            }
        })
    
    elif request.method == 'POST':
        # 处理新增数据
        try:
            data = json.loads(request.body)
            # 这里后续会集成实际的数据模型
            return JsonResponse({
                'status': 'success',
                'message': 'Data received',
                'data': data
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON'
            }, status=400)


@api_login_required
@csrf_exempt
@require_http_methods(["POST"])
def ai_chat(request):
    """AI助手对话API"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        
        # 简单的AI响应模拟
        response = f"收到您的消息：{message}。这是一个演示响应，后续会集成真正的AI功能。"
        
        return JsonResponse({
            'response': response,
            'timestamp': '2024-12-28T12:00:00Z'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON'
        }, status=400)
