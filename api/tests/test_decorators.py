import pytest
import json
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.http import JsonResponse
from api.decorators import api_login_required


@pytest.mark.django_db
class TestAPILoginRequiredDecorator:
    
    def setup_method(self):
        self.factory = RequestFactory()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        
        # Create a simple test view
        @api_login_required
        def test_view(request):
            return JsonResponse({'success': True, 'user': request.user.username})
        
        self.test_view = test_view
    
    def test_decorator_blocks_anonymous_user(self):
        """Test that the decorator blocks anonymous users"""
        request = self.factory.get('/test/')
        request.user = AnonymousUser()
        
        response = self.test_view(request)
        
        assert response.status_code == 401
        data = json.loads(response.content)
        assert data['error'] == 'Authentication required'
        assert data['message'] == 'You must be logged in to access this API'
    
    def test_decorator_allows_authenticated_user(self):
        """Test that the decorator allows authenticated users"""
        request = self.factory.get('/test/')
        request.user = self.user
        
        response = self.test_view(request)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert data['user'] == 'testuser'
    
    def test_decorator_handles_post_request(self):
        """Test that the decorator works with POST requests"""
        request = self.factory.post('/test/', data='{"test": "data"}', content_type='application/json')
        request.user = self.user
        
        response = self.test_view(request)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
    
    def test_decorator_handles_post_request_unauthenticated(self):
        """Test that the decorator blocks POST requests for unauthenticated users"""
        request = self.factory.post('/test/', data='{"test": "data"}', content_type='application/json')
        request.user = AnonymousUser()
        
        response = self.test_view(request)
        
        assert response.status_code == 401
        data = json.loads(response.content)
        assert data['error'] == 'Authentication required'
    
    def test_decorator_preserves_view_args_kwargs(self):
        """Test that the decorator preserves view arguments and keyword arguments"""
        @api_login_required
        def test_view_with_args(request, arg1, arg2, kwarg1=None):
            return JsonResponse({
                'arg1': arg1,
                'arg2': arg2,
                'kwarg1': kwarg1,
                'user': request.user.username
            })
        
        request = self.factory.get('/test/')
        request.user = self.user
        
        response = test_view_with_args(request, 'value1', 'value2', kwarg1='kwvalue')
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['arg1'] == 'value1'
        assert data['arg2'] == 'value2'
        assert data['kwarg1'] == 'kwvalue'
        assert data['user'] == 'testuser'
    
    def test_decorator_preserves_function_metadata(self):
        """Test that the decorator preserves the original function's metadata"""
        @api_login_required
        def documented_view(request):
            """This is a test view with documentation."""
            return JsonResponse({'test': True})
        
        assert documented_view.__name__ == 'documented_view'
        assert documented_view.__doc__ == 'This is a test view with documentation.'
    
    def test_decorator_returns_proper_json_content_type(self):
        """Test that the decorator returns proper JSON content type"""
        request = self.factory.get('/test/')
        request.user = AnonymousUser()
        
        response = self.test_view(request)
        
        assert response.status_code == 401
        assert response['Content-Type'] == 'application/json'
    
    def test_decorator_works_with_different_http_methods(self):
        """Test that the decorator works with different HTTP methods"""
        methods = ['get', 'post', 'put', 'patch', 'delete']
        
        for method in methods:
            request = getattr(self.factory, method)('/test/')
            request.user = self.user
            
            response = self.test_view(request)
            assert response.status_code == 200, f"Method {method.upper()} should work"
            
            # Test unauthenticated
            request = getattr(self.factory, method)('/test/')
            request.user = AnonymousUser()
            
            response = self.test_view(request)
            assert response.status_code == 401, f"Method {method.upper()} should be blocked when unauthenticated"
    
    def test_decorator_handles_inactive_user(self):
        """Test that the decorator allows inactive users (Django default behavior)"""
        # Create inactive user
        inactive_user = User.objects.create_user(
            username='inactive',
            password='testpass123',
            is_active=False
        )
        
        request = self.factory.get('/test/')
        request.user = inactive_user
        
        response = self.test_view(request)
        
        # Django's is_authenticated returns True for inactive users by default
        # This is the expected behavior unless we add custom logic
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert data['user'] == 'inactive'