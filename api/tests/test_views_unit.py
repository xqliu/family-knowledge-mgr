"""
Unit tests for API views
"""
import json
from unittest.mock import patch, Mock
from django.test import TestCase, RequestFactory
from django.http import JsonResponse
from django.contrib.auth.models import User

from api.views import health_check, family_overview, ai_chat


class TestHealthCheck(TestCase):
    """Test health check endpoint"""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_health_check_returns_ok_status(self):
        """Test health check returns OK status"""
        request = self.factory.get('/api/health/')
        
        response = health_check(request)
        
        self.assertIsInstance(response, JsonResponse)
        
        # Check response content
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'ok')
        self.assertEqual(response_data['message'], 'API运行正常')
    
    def test_health_check_status_code(self):
        """Test health check returns 200 status code"""
        request = self.factory.get('/api/health/')
        
        response = health_check(request)
        
        self.assertEqual(response.status_code, 200)


class TestFamilyOverview(TestCase):
    """Test family overview endpoint"""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    @patch('api.views.api_login_required')
    def test_family_overview_get_request(self, mock_login_required):
        """Test GET request to family overview"""
        # Mock the decorator to pass through
        mock_login_required.side_effect = lambda func: func
        
        request = self.factory.get('/api/family/overview/')
        
        response = family_overview(request)
        
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        
        # Check response structure
        response_data = json.loads(response.content)
        self.assertIn('family_members', response_data)
        self.assertIn('recent_stories', response_data)
        self.assertIn('stats', response_data)
        
        # Check data content
        self.assertEqual(len(response_data['family_members']), 1)
        self.assertEqual(response_data['family_members'][0]['name'], '测试用户')
        self.assertEqual(len(response_data['recent_stories']), 1)
        self.assertEqual(response_data['stats']['total_members'], 1)
    
    @patch('api.views.api_login_required')
    def test_family_overview_post_valid_json(self, mock_login_required):
        """Test POST request with valid JSON"""
        # Mock the decorator to pass through
        mock_login_required.side_effect = lambda func: func
        
        test_data = {'name': '新成员', 'relationship': '父亲'}
        request = self.factory.post(
            '/api/family/overview/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        response = family_overview(request)
        
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        
        # Check response structure
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['message'], 'Data received')
        self.assertEqual(response_data['data'], test_data)
    
    @patch('api.views.api_login_required')
    def test_family_overview_post_invalid_json(self, mock_login_required):
        """Test POST request with invalid JSON"""
        # Mock the decorator to pass through
        mock_login_required.side_effect = lambda func: func
        
        request = self.factory.post(
            '/api/family/overview/',
            data='invalid json',
            content_type='application/json'
        )
        
        response = family_overview(request)
        
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 400)
        
        # Check error response
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
        self.assertEqual(response_data['message'], 'Invalid JSON')
    
    @patch('api.views.api_login_required')
    def test_family_overview_post_empty_body(self, mock_login_required):
        """Test POST request with empty body"""
        # Mock the decorator to pass through
        mock_login_required.side_effect = lambda func: func
        
        request = self.factory.post(
            '/api/family/overview/',
            data='',
            content_type='application/json'
        )
        
        response = family_overview(request)
        
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 400)
        
        # Check error response
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
        self.assertEqual(response_data['message'], 'Invalid JSON')


class TestAIChat(TestCase):
    """Test AI chat endpoint"""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    @patch('api.views.api_login_required')
    def test_ai_chat_valid_message(self, mock_login_required):
        """Test AI chat with valid message"""
        # Mock the decorator to pass through
        mock_login_required.side_effect = lambda func: func
        
        test_data = {'message': '你好，家庭助手'}
        request = self.factory.post(
            '/api/ai/chat/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        response = ai_chat(request)
        
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        
        # Check response structure
        response_data = json.loads(response.content)
        self.assertIn('response', response_data)
        self.assertIn('timestamp', response_data)
        
        # Check response content
        expected_response = "收到您的消息：你好，家庭助手。这是一个演示响应，后续会集成真正的AI功能。"
        self.assertEqual(response_data['response'], expected_response)
        self.assertEqual(response_data['timestamp'], '2024-12-28T12:00:00Z')
    
    @patch('api.views.api_login_required')
    def test_ai_chat_empty_message(self, mock_login_required):
        """Test AI chat with empty message"""
        # Mock the decorator to pass through
        mock_login_required.side_effect = lambda func: func
        
        test_data = {'message': ''}
        request = self.factory.post(
            '/api/ai/chat/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        response = ai_chat(request)
        
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        
        # Check response structure
        response_data = json.loads(response.content)
        expected_response = "收到您的消息：。这是一个演示响应，后续会集成真正的AI功能。"
        self.assertEqual(response_data['response'], expected_response)
    
    @patch('api.views.api_login_required')
    def test_ai_chat_missing_message_key(self, mock_login_required):
        """Test AI chat with missing message key"""
        # Mock the decorator to pass through
        mock_login_required.side_effect = lambda func: func
        
        test_data = {'other_key': 'value'}
        request = self.factory.post(
            '/api/ai/chat/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        response = ai_chat(request)
        
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        
        # Check response structure
        response_data = json.loads(response.content)
        expected_response = "收到您的消息：。这是一个演示响应，后续会集成真正的AI功能。"
        self.assertEqual(response_data['response'], expected_response)
    
    @patch('api.views.api_login_required')
    def test_ai_chat_invalid_json(self, mock_login_required):
        """Test AI chat with invalid JSON"""
        # Mock the decorator to pass through
        mock_login_required.side_effect = lambda func: func
        
        request = self.factory.post(
            '/api/ai/chat/',
            data='invalid json',
            content_type='application/json'
        )
        
        response = ai_chat(request)
        
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 400)
        
        # Check error response
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
        self.assertEqual(response_data['message'], 'Invalid JSON')
    
    @patch('api.views.api_login_required')
    def test_ai_chat_with_special_characters(self, mock_login_required):
        """Test AI chat with special characters in message"""
        # Mock the decorator to pass through
        mock_login_required.side_effect = lambda func: func
        
        test_data = {'message': '测试消息！@#$%^&*()'}
        request = self.factory.post(
            '/api/ai/chat/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        response = ai_chat(request)
        
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        
        # Check response structure
        response_data = json.loads(response.content)
        expected_response = "收到您的消息：测试消息！@#$%^&*()。这是一个演示响应，后续会集成真正的AI功能。"
        self.assertEqual(response_data['response'], expected_response)


class TestViewsIntegration(TestCase):
    """Integration tests for API views"""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_all_views_return_json_response(self):
        """Test that all views return JsonResponse objects"""
        # Health check
        request = self.factory.get('/api/health/')
        response = health_check(request)
        self.assertIsInstance(response, JsonResponse)
        
        # Family overview GET (with mocked decorator)
        with patch('api.views.api_login_required', side_effect=lambda func: func):
            request = self.factory.get('/api/family/overview/')
            response = family_overview(request)
            self.assertIsInstance(response, JsonResponse)
        
        # AI chat (with mocked decorator)
        with patch('api.views.api_login_required', side_effect=lambda func: func):
            test_data = {'message': 'test'}
            request = self.factory.post(
                '/api/ai/chat/',
                data=json.dumps(test_data),
                content_type='application/json'
            )
            response = ai_chat(request)
            self.assertIsInstance(response, JsonResponse)
    
    def test_content_type_consistency(self):
        """Test that all responses have consistent content type"""
        # Health check
        request = self.factory.get('/api/health/')
        response = health_check(request)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Family overview (with mocked decorator)
        with patch('api.views.api_login_required', side_effect=lambda func: func):
            request = self.factory.get('/api/family/overview/')
            response = family_overview(request)
            self.assertEqual(response['Content-Type'], 'application/json')
    
    def test_error_handling_consistency(self):
        """Test that error responses have consistent structure"""
        with patch('api.views.api_login_required', side_effect=lambda func: func):
            # Test family overview with invalid JSON
            request = self.factory.post(
                '/api/family/overview/',
                data='invalid json',
                content_type='application/json'
            )
            response = family_overview(request)
            response_data = json.loads(response.content)
            
            self.assertIn('status', response_data)
            self.assertIn('message', response_data)
            self.assertEqual(response_data['status'], 'error')
            
            # Test AI chat with invalid JSON
            request = self.factory.post(
                '/api/ai/chat/',
                data='invalid json',
                content_type='application/json'
            )
            response = ai_chat(request)
            response_data = json.loads(response.content)
            
            self.assertIn('status', response_data)
            self.assertIn('message', response_data)
            self.assertEqual(response_data['status'], 'error')