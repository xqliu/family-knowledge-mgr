"""
Comprehensive tests for API decorators targeting 90%+ branch coverage
"""
import pytest
import json
from unittest.mock import Mock
from django.test import RequestFactory
from django.http import JsonResponse, HttpResponse
from api.decorators import api_login_required


class TestAPILoginRequiredDecorator:
    """Comprehensive tests for api_login_required decorator"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.factory = RequestFactory()
        
        # Create test users
        self.mock_user = Mock()
        self.mock_user.is_authenticated = True
        self.mock_user.__str__ = lambda self: 'test_user'
        
        self.mock_unauth_user = Mock()
        self.mock_unauth_user.is_authenticated = False
    
    def test_decorator_with_authenticated_user(self):
        """Test decorator allows authenticated user"""
        @api_login_required
        def test_view(request):
            return JsonResponse({'message': 'Success', 'user': str(request.user)})
        
        request = self.factory.get('/test/')
        request.user = self.mock_user
        
        response = test_view(request)
        assert isinstance(response, JsonResponse)
        data = json.loads(response.content)
        assert data['message'] == 'Success'
        assert data['user'] == 'test_user'
    
    def test_decorator_with_unauthenticated_user(self):
        """Test decorator blocks unauthenticated user"""
        @api_login_required
        def test_view(request):
            return JsonResponse({'message': 'Success'})
        
        request = self.factory.get('/test/')
        request.user = self.mock_unauth_user
        
        response = test_view(request)
        assert isinstance(response, JsonResponse)
        assert response.status_code == 401
        data = json.loads(response.content)
        assert data['error'] == 'Authentication required'
        assert data['message'] == 'You must be logged in to access this API'
    
    def test_decorator_preserves_function_metadata(self):
        """Test decorator preserves function metadata with functools.wraps"""
        def original_function(request):
            """Original function docstring"""
            return HttpResponse('test')
        
        decorated_function = api_login_required(original_function)
        
        # Check that functools.wraps preserved metadata
        assert decorated_function.__name__ == original_function.__name__
        assert decorated_function.__doc__ == original_function.__doc__
    
    def test_decorator_with_positional_args(self):
        """Test decorator with view functions that take positional arguments"""
        @api_login_required
        def view_with_args(request, arg1, arg2):
            return JsonResponse({'args': [arg1, arg2]})
        
        # Test with authenticated user
        request = self.factory.get('/test/')
        request.user = self.mock_user
        
        response = view_with_args(request, 'test1', 'test2')
        data = json.loads(response.content)
        assert data['args'] == ['test1', 'test2']
        
        # Test with unauthenticated user
        request.user = self.mock_unauth_user
        response = view_with_args(request, 'test1', 'test2')
        assert response.status_code == 401
    
    def test_decorator_with_keyword_args(self):
        """Test decorator with view functions that take keyword arguments"""
        @api_login_required
        def view_with_kwargs(request, **kwargs):
            return JsonResponse({'kwargs': kwargs})
        
        # Test with authenticated user
        request = self.factory.get('/test/')
        request.user = self.mock_user
        
        response = view_with_kwargs(request, key1='value1', key2='value2')
        data = json.loads(response.content)
        assert data['kwargs'] == {'key1': 'value1', 'key2': 'value2'}
        
        # Test with unauthenticated user
        request.user = self.mock_unauth_user
        response = view_with_kwargs(request, key1='value1')
        assert response.status_code == 401
    
    def test_decorator_with_mixed_arguments(self):
        """Test decorator with view functions that take mixed arguments"""
        @api_login_required
        def view_with_mixed(request, arg1, *args, **kwargs):
            return JsonResponse({
                'arg1': arg1,
                'args': list(args),
                'kwargs': kwargs
            })
        
        # Test with authenticated user
        request = self.factory.get('/test/')
        request.user = self.mock_user
        
        response = view_with_mixed(request, 'first', 'second', 'third', key='value')
        data = json.loads(response.content)
        assert data['arg1'] == 'first'
        assert data['args'] == ['second', 'third']
        assert data['kwargs'] == {'key': 'value'}
        
        # Test with unauthenticated user
        request.user = self.mock_unauth_user
        response = view_with_mixed(request, 'first', 'second', key='value')
        assert response.status_code == 401
    
    @pytest.mark.parametrize("view_func_name", ['view_with_args', 'view_with_kwargs', 'view_with_mixed'])
    def test_unauthenticated_user_blocked_for_all_signatures(self, view_func_name):
        """Test that unauthenticated users are blocked regardless of function signature"""
        @api_login_required
        def view_with_args(request, arg):
            return JsonResponse({'success': True})
        
        @api_login_required  
        def view_with_kwargs(request, **kwargs):
            return JsonResponse({'success': True})
        
        @api_login_required
        def view_with_mixed(request, arg, *args, **kwargs):
            return JsonResponse({'success': True})
        
        view_funcs = {
            'view_with_args': view_with_args,
            'view_with_kwargs': view_with_kwargs,
            'view_with_mixed': view_with_mixed
        }
        
        request = self.factory.get('/test/')
        request.user = self.mock_unauth_user
        
        response = view_funcs[view_func_name](request, 'test')
        assert response.status_code == 401
        data = json.loads(response.content)
        assert data['error'] == 'Authentication required'
    
    def test_decorator_with_http_response(self):
        """Test decorator with view that returns HttpResponse"""
        @api_login_required
        def view_returns_http_response(request):
            return HttpResponse('Plain HTTP response')
        
        # Test with authenticated user
        request = self.factory.get('/test/')
        request.user = self.mock_user
        
        response = view_returns_http_response(request)
        assert isinstance(response, HttpResponse)
        assert response.content.decode() == 'Plain HTTP response'
        
        # Test with unauthenticated user
        request.user = self.mock_unauth_user
        response = view_returns_http_response(request)
        assert response.status_code == 401
    
    def test_decorator_with_json_response(self):
        """Test decorator with view that returns JsonResponse"""
        @api_login_required
        def view_returns_json_response(request):
            return JsonResponse({'type': 'json'})
        
        # Test with authenticated user
        request = self.factory.get('/test/')
        request.user = self.mock_user
        
        response = view_returns_json_response(request)
        assert isinstance(response, JsonResponse)
        data = json.loads(response.content)
        assert data['type'] == 'json'
        
        # Test with unauthenticated user
        request.user = self.mock_unauth_user
        response = view_returns_json_response(request)
        assert response.status_code == 401
    
    def test_decorator_with_custom_response(self):
        """Test decorator with view that returns custom response"""
        @api_login_required
        def view_returns_custom_response(request):
            response = HttpResponse('Custom response')
            response['Custom-Header'] = 'test'
            return response
        
        # Test with authenticated user
        request = self.factory.get('/test/')
        request.user = self.mock_user
        
        response = view_returns_custom_response(request)
        assert isinstance(response, HttpResponse)
        assert response['Custom-Header'] == 'test'
        
        # Test with unauthenticated user
        request.user = self.mock_unauth_user
        response = view_returns_custom_response(request)
        assert response.status_code == 401
    
    def test_decorator_with_view_that_raises_exception(self):
        """Test decorator with view that raises exception"""
        @api_login_required
        def view_that_raises_exception(request):
            raise ValueError("Test exception")
        
        # Test with authenticated user - exception should propagate
        request = self.factory.get('/test/')
        request.user = self.mock_user
        
        with pytest.raises(ValueError, match="Test exception"):
            view_that_raises_exception(request)
        
        # Test with unauthenticated user - should return 401 before reaching exception
        request.user = self.mock_unauth_user
        response = view_that_raises_exception(request)
        assert response.status_code == 401
    
    def test_user_with_property_authentication(self):
        """Test with user that has is_authenticated as a property"""
        class UserWithProperty:
            @property
            def is_authenticated(self):
                return True
        
        @api_login_required
        def simple_view(request):
            return JsonResponse({'status': 'ok'})
        
        request = self.factory.get('/test/')
        request.user = UserWithProperty()
        
        response = simple_view(request)
        assert isinstance(response, JsonResponse)
        data = json.loads(response.content)
        assert data['status'] == 'ok'
    
    def test_user_with_property_unauthenticated(self):
        """Test with user that has is_authenticated property returning False"""
        class UnauthenticatedUserWithProperty:
            @property 
            def is_authenticated(self):
                return False
        
        @api_login_required
        def simple_view(request):
            return JsonResponse({'status': 'ok'})
        
        request = self.factory.get('/test/')
        request.user = UnauthenticatedUserWithProperty()
        
        response = simple_view(request)
        assert response.status_code == 401
    
    def test_decorator_stacking(self):
        """Test decorator works with other decorators"""
        from functools import wraps
        
        def another_decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                response = func(*args, **kwargs)
                if isinstance(response, JsonResponse):
                    # Add extra data to JSON response
                    data = json.loads(response.content)
                    data['decorated'] = True
                    return JsonResponse(data)
                return response
            return wrapper
        
        @another_decorator
        @api_login_required
        def double_decorated_view(request):
            return JsonResponse({'original': True})
        
        # Test with authenticated user
        request = self.factory.get('/test/')
        request.user = self.mock_user
        
        response = double_decorated_view(request)
        data = json.loads(response.content)
        assert data['original'] is True
        assert data['decorated'] is True
        
        # Test with unauthenticated user
        request.user = self.mock_unauth_user
        response = double_decorated_view(request)
        # The outer decorator processes the 401 response
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['error'] == 'Authentication required'
        assert data['decorated'] is True
    
    def test_performance_multiple_calls(self):
        """Test decorator performance with multiple calls"""
        @api_login_required
        def performance_view(request):
            return JsonResponse({'iteration': getattr(request, 'iteration', 0)})
        
        request = self.factory.get('/test/')
        request.user = self.mock_user
        
        # Test multiple calls to ensure decorator doesn't have state issues
        for i in range(10):
            request.iteration = i
            response = performance_view(request)
            data = json.loads(response.content)
            assert data['iteration'] == i
    
    def test_request_methods_coverage(self):
        """Test decorator works with different HTTP methods"""
        @api_login_required
        def multi_method_view(request):
            return JsonResponse({'method': request.method})
        
        request_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        
        for method in request_methods:
            # Test with authenticated user
            request = getattr(self.factory, method.lower())('/test/')
            request.user = self.mock_user
            
            response = multi_method_view(request)
            assert response.status_code == 200
            data = json.loads(response.content)
            assert data['method'] == method
            
            # Test with unauthenticated user
            request.user = self.mock_unauth_user
            response = multi_method_view(request)
            assert response.status_code == 401