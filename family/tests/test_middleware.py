import pytest
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpResponse
from family.middleware import SimpleAuthMiddleware


@pytest.mark.django_db
class TestSimpleAuthMiddleware:
    
    def setup_method(self):
        self.factory = RequestFactory()
        self.middleware = SimpleAuthMiddleware(get_response=lambda r: HttpResponse('OK'))
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
    
    def test_middleware_allows_non_app_paths(self):
        """Test that non-/app/ paths are allowed through without authentication"""
        request = self.factory.get('/admin/')
        request.user = AnonymousUser()
        
        response = self.middleware(request)
        assert response.status_code == 200
        assert response.content == b'OK'
    
    def test_middleware_allows_api_paths(self):
        """Test that /api/ paths are allowed through (handled by decorators)"""
        request = self.factory.get('/api/health/')
        request.user = AnonymousUser()
        
        response = self.middleware(request)
        assert response.status_code == 200
        assert response.content == b'OK'
    
    def test_middleware_blocks_app_unauthenticated(self):
        """Test that /app/ paths are blocked for unauthenticated users"""
        request = self.factory.get('/app/')
        request.user = AnonymousUser()
        
        response = self.middleware(request)
        assert response.status_code == 302
        assert '/admin/login/?next=/app/' in response.url
    
    def test_middleware_blocks_app_subpaths_unauthenticated(self):
        """Test that /app/subpath/ paths are blocked for unauthenticated users"""
        request = self.factory.get('/app/dashboard/')
        request.user = AnonymousUser()
        
        response = self.middleware(request)
        assert response.status_code == 302
        assert '/admin/login/?next=/app/dashboard/' in response.url
    
    def test_middleware_allows_app_authenticated(self):
        """Test that /app/ paths are allowed for authenticated users"""
        request = self.factory.get('/app/')
        request.user = self.user
        
        response = self.middleware(request)
        assert response.status_code == 200
        assert response.content == b'OK'
    
    def test_middleware_allows_app_subpaths_authenticated(self):
        """Test that /app/subpath/ paths are allowed for authenticated users"""
        request = self.factory.get('/app/dashboard/profile/')
        request.user = self.user
        
        response = self.middleware(request)
        assert response.status_code == 200
        assert response.content == b'OK'
    
    def test_middleware_preserves_original_path_in_redirect(self):
        """Test that the original path is preserved in the redirect URL"""
        request = self.factory.get('/app/complex/path/with/params/')
        request.user = AnonymousUser()
        
        response = self.middleware(request)
        assert response.status_code == 302
        assert '/admin/login/?next=/app/complex/path/with/params/' in response.url
    
    def test_middleware_handles_root_app_path(self):
        """Test middleware handles /app path without trailing slash"""
        request = self.factory.get('/app')  # without trailing slash
        request.user = AnonymousUser()
        
        response = self.middleware(request)
        # /app (without slash) should NOT be blocked, only /app/ paths are blocked
        assert response.status_code == 200
        assert response.content == b'OK'
    
    def test_middleware_does_not_affect_similar_paths(self):
        """Test that paths similar to /app/ but different are not affected"""
        similar_paths = ['/application/', '/append/', '/apps/', '/app-config/']
        
        for path in similar_paths:
            request = self.factory.get(path)
            request.user = AnonymousUser()
            
            response = self.middleware(request)
            assert response.status_code == 200, f"Path {path} should not be blocked"
            assert response.content == b'OK'