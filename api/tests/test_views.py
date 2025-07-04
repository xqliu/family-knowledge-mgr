import pytest
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestAPIViews:
    
    def setup_method(self):
        self.client = Client()
        # Create test user for authenticated tests
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
    
    def test_health_check(self):
        response = self.client.get('/api/health/')
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'
        assert data['message'] == 'API运行正常'
    
    def test_family_overview_get_unauthenticated(self):
        """Test that unauthenticated requests are blocked"""
        response = self.client.get('/api/family/overview/')
        
        assert response.status_code == 401
        data = response.json()
        assert data['error'] == 'Authentication required'
        assert data['message'] == 'You must be logged in to access this API'
    
    def test_family_overview_get_authenticated(self):
        """Test authenticated access to family overview"""
        self.client.force_login(self.user)
        response = self.client.get('/api/family/overview/')
        
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert 'family_members' in data
        assert 'recent_stories' in data
        assert 'stats' in data
        
        # Check family_members structure
        assert isinstance(data['family_members'], list)
        if data['family_members']:
            member = data['family_members'][0]
            assert 'id' in member
            assert 'name' in member
            assert 'relationship' in member
        
        # Check recent_stories structure
        assert isinstance(data['recent_stories'], list)
        if data['recent_stories']:
            story = data['recent_stories'][0]
            assert 'id' in story
            assert 'title' in story
            assert 'date' in story
        
        # Check stats structure
        stats = data['stats']
        assert 'total_members' in stats
        assert 'total_stories' in stats
        assert 'total_photos' in stats
        assert isinstance(stats['total_members'], int)
        assert isinstance(stats['total_stories'], int)
        assert isinstance(stats['total_photos'], int)
    
    def test_family_overview_post_unauthenticated(self):
        """Test that unauthenticated POST requests are blocked"""
        test_data = {'name': '测试用户'}
        
        response = self.client.post(
            '/api/family/overview/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data['error'] == 'Authentication required'
    
    def test_family_overview_post_valid_json(self):
        """Test authenticated POST with valid JSON"""
        self.client.force_login(self.user)
        test_data = {
            'name': '测试用户',
            'relationship': '父亲',
            'message': '这是一个测试'
        }
        
        response = self.client.post(
            '/api/family/overview/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['message'] == 'Data received'
        assert data['data'] == test_data
    
    def test_family_overview_post_invalid_json(self):
        """Test authenticated POST with invalid JSON"""
        self.client.force_login(self.user)
        response = self.client.post(
            '/api/family/overview/',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data['status'] == 'error'
        assert data['message'] == 'Invalid JSON'
    
    def test_family_overview_method_not_allowed(self):
        """Test that unsupported methods return 405"""
        self.client.force_login(self.user)
        response = self.client.put('/api/family/overview/')
        assert response.status_code == 405
        
        response = self.client.delete('/api/family/overview/')
        assert response.status_code == 405
    
    def test_ai_chat_unauthenticated(self):
        """Test that unauthenticated AI chat requests are blocked"""
        test_data = {'message': 'test'}
        
        response = self.client.post(
            '/api/ai/chat/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data['error'] == 'Authentication required'
    
    def test_ai_chat_valid_message(self):
        """Test authenticated AI chat with valid message"""
        self.client.force_login(self.user)
        test_message = '你好，我想了解我的家庭历史'
        test_data = {'message': test_message}
        
        response = self.client.post(
            '/api/ai/chat/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'response' in data
        assert 'timestamp' in data
        assert test_message in data['response']
        assert '演示响应' in data['response']
        
        # Check timestamp format (should be ISO format)
        timestamp = data['timestamp']
        assert 'T' in timestamp
        assert 'Z' in timestamp
    
    def test_ai_chat_empty_message(self):
        """Test authenticated AI chat with empty message"""
        self.client.force_login(self.user)
        test_data = {'message': ''}
        
        response = self.client.post(
            '/api/ai/chat/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'response' in data
        assert '' in data['response']  # Empty message should be included
    
    def test_ai_chat_missing_message(self):
        """Test authenticated AI chat with missing message"""
        self.client.force_login(self.user)
        test_data = {}
        
        response = self.client.post(
            '/api/ai/chat/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'response' in data
        # Should handle missing message gracefully
    
    def test_ai_chat_invalid_json(self):
        """Test authenticated AI chat with invalid JSON"""
        self.client.force_login(self.user)
        response = self.client.post(
            '/api/ai/chat/',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data['status'] == 'error'
        assert data['message'] == 'Invalid JSON'
    
    def test_ai_chat_method_not_allowed(self):
        """Test that unsupported methods return 405"""
        self.client.force_login(self.user)
        response = self.client.get('/api/ai/chat/')
        assert response.status_code == 405
        
        response = self.client.put('/api/ai/chat/')
        assert response.status_code == 405
        
        response = self.client.delete('/api/ai/chat/')
        assert response.status_code == 405
    
    def test_ai_chat_csrf_exempt(self):
        """Test that CSRF protection is properly exempted"""
        self.client.force_login(self.user)
        test_data = {'message': 'test'}
        
        # This should work without CSRF token
        response = self.client.post(
            '/api/ai/chat/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
    
    def test_family_overview_csrf_exempt(self):
        """Test that CSRF protection is properly exempted"""
        self.client.force_login(self.user)
        test_data = {'test': 'data'}
        
        # This should work without CSRF token
        response = self.client.post(
            '/api/family/overview/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.django_db
class TestAPIIntegration:
    
    def setup_method(self):
        self.client = Client()
        # Create test user for authenticated tests
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
    
    def test_api_workflow(self):
        """Test a complete authenticated API workflow"""
        self.client.force_login(self.user)
        
        # 1. Check health (no auth required)
        health_response = self.client.get('/api/health/')
        assert health_response.status_code == 200
        
        # 2. Get family overview (auth required)
        overview_response = self.client.get('/api/family/overview/')
        assert overview_response.status_code == 200
        
        # 3. Post new data (auth required)
        test_data = {'name': '新成员', 'relationship': '兄弟'}
        post_response = self.client.post(
            '/api/family/overview/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        assert post_response.status_code == 200
        
        # 4. Test AI chat (auth required)
        chat_response = self.client.post(
            '/api/ai/chat/',
            data=json.dumps({'message': '告诉我关于这个新成员'}),
            content_type='application/json'
        )
        assert chat_response.status_code == 200
    
    def test_error_handling_chain(self):
        """Test error handling across multiple API calls"""
        self.client.force_login(self.user)
        
        # Invalid JSON in family overview
        response1 = self.client.post(
            '/api/family/overview/',
            data='invalid',
            content_type='application/json'
        )
        assert response1.status_code == 400
        
        # Invalid JSON in AI chat
        response2 = self.client.post(
            '/api/ai/chat/',
            data='invalid',
            content_type='application/json'
        )
        assert response2.status_code == 400
        
        # Health check should still work
        response3 = self.client.get('/api/health/')
        assert response3.status_code == 200