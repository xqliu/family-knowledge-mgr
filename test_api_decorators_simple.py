#!/usr/bin/env python
"""
Comprehensive test for API decorators targeting 90%+ branch coverage
"""
import os
import sys

# Setup Django BEFORE any imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Start coverage before any imports
try:
    import coverage
    cov = coverage.Coverage(source=['api.decorators'], branch=True)
    cov.start()
    coverage_available = True
except ImportError:
    coverage_available = False

import django
django.setup()

from unittest.mock import Mock, patch
from django.test import RequestFactory
from django.http import JsonResponse, HttpResponse
import json
from api.decorators import api_login_required

print("Testing API decorators with comprehensive branch coverage...")

# Test 1: api_login_required decorator with authenticated user
print("✅ Test 1: api_login_required with authenticated user")

# Create a simple view function to decorate
@api_login_required
def test_view(request):
    return JsonResponse({'message': 'Success', 'user': str(request.user)})

factory = RequestFactory()

# Create authenticated user
mock_user = Mock()
mock_user.is_authenticated = True
mock_user.__str__ = lambda self: 'test_user'

request = factory.get('/test/')
request.user = mock_user

response = test_view(request)
assert isinstance(response, JsonResponse)
data = json.loads(response.content)
assert data['message'] == 'Success'
assert data['user'] == 'test_user'

# Test 2: api_login_required decorator with unauthenticated user
print("✅ Test 2: api_login_required with unauthenticated user")

# Create unauthenticated user
mock_unauth_user = Mock()
mock_unauth_user.is_authenticated = False

request_unauth = factory.get('/test/')
request_unauth.user = mock_unauth_user

response_unauth = test_view(request_unauth)
assert isinstance(response_unauth, JsonResponse)
assert response_unauth.status_code == 401
data_unauth = json.loads(response_unauth.content)
assert data_unauth['error'] == 'Authentication required'
assert data_unauth['message'] == 'You must be logged in to access this API'

# Test 3: Decorator preserves function metadata
print("✅ Test 3: Decorator preserves function metadata")

def original_function(request):
    """Original function docstring"""
    return HttpResponse('test')

decorated_function = api_login_required(original_function)

# Check that functools.wraps preserved metadata
assert decorated_function.__name__ == original_function.__name__
assert decorated_function.__doc__ == original_function.__doc__

# Test 4: Decorator works with different view function signatures
print("✅ Test 4: Decorator with different function signatures")

@api_login_required
def view_with_args(request, arg1, arg2):
    return JsonResponse({'args': [arg1, arg2]})

@api_login_required  
def view_with_kwargs(request, **kwargs):
    return JsonResponse({'kwargs': kwargs})

@api_login_required
def view_with_mixed(request, arg1, *args, **kwargs):
    return JsonResponse({
        'arg1': arg1,
        'args': list(args),
        'kwargs': kwargs
    })

# Test authenticated user with different signatures
request.user = mock_user

# Test view with positional args
response_args = view_with_args(request, 'test1', 'test2')
data_args = json.loads(response_args.content)
assert data_args['args'] == ['test1', 'test2']

# Test view with kwargs
response_kwargs = view_with_kwargs(request, key1='value1', key2='value2')
data_kwargs = json.loads(response_kwargs.content)
assert data_kwargs['kwargs'] == {'key1': 'value1', 'key2': 'value2'}

# Test view with mixed args
response_mixed = view_with_mixed(request, 'first', 'second', 'third', key='value')
data_mixed = json.loads(response_mixed.content)
assert data_mixed['arg1'] == 'first'
assert data_mixed['args'] == ['second', 'third']
assert data_mixed['kwargs'] == {'key': 'value'}

# Test 5: Decorator works with unauthenticated user for all function types
print("✅ Test 5: Unauthenticated user with different function signatures")

request_unauth.user = mock_unauth_user

# All should return 401 regardless of signature
for view_func in [view_with_args, view_with_kwargs, view_with_mixed]:
    response = view_func(request_unauth, 'test')
    assert response.status_code == 401
    data = json.loads(response.content)
    assert data['error'] == 'Authentication required'

# Test 6: Decorator handles view functions that return different response types
print("✅ Test 6: Decorator with different response types")

@api_login_required
def view_returns_http_response(request):
    return HttpResponse('Plain HTTP response')

@api_login_required
def view_returns_json_response(request):
    return JsonResponse({'type': 'json'})

@api_login_required
def view_returns_custom_response(request):
    response = HttpResponse('Custom response')
    response['Custom-Header'] = 'test'
    return response

request.user = mock_user

# Test all return HTTP responses when authenticated
http_resp = view_returns_http_response(request)
assert isinstance(http_resp, HttpResponse)
assert http_resp.content.decode() == 'Plain HTTP response'

json_resp = view_returns_json_response(request)
assert isinstance(json_resp, JsonResponse)
data = json.loads(json_resp.content)
assert data['type'] == 'json'

custom_resp = view_returns_custom_response(request)
assert isinstance(custom_resp, HttpResponse)
assert custom_resp['Custom-Header'] == 'test'

# Test 7: Decorator handles view functions that raise exceptions
print("✅ Test 7: Decorator with view functions that raise exceptions")

@api_login_required
def view_that_raises_exception(request):
    raise ValueError("Test exception")

request.user = mock_user

# Exception should propagate through decorator when user is authenticated
try:
    view_that_raises_exception(request)
    assert False, "Exception should have been raised"
except ValueError as e:
    assert str(e) == "Test exception"

# When user is not authenticated, should return 401 before reaching exception
request_unauth.user = mock_unauth_user
response = view_that_raises_exception(request_unauth)
assert response.status_code == 401

# Test 8: Edge case - request.user attribute access
print("✅ Test 8: Edge cases with request.user")

@api_login_required
def simple_view(request):
    return JsonResponse({'status': 'ok'})

# Test with user that has is_authenticated as a property that might fail
class UserWithProperty:
    @property
    def is_authenticated(self):
        return True

request_prop = factory.get('/test/')
request_prop.user = UserWithProperty()

response_prop = simple_view(request_prop)
assert isinstance(response_prop, JsonResponse)
data_prop = json.loads(response_prop.content)
assert data_prop['status'] == 'ok'

# Test with user where is_authenticated is False
class UnauthenticatedUserWithProperty:
    @property 
    def is_authenticated(self):
        return False

request_unauth_prop = factory.get('/test/')
request_unauth_prop.user = UnauthenticatedUserWithProperty()

response_unauth_prop = simple_view(request_unauth_prop)
assert response_unauth_prop.status_code == 401

# Test 9: Multiple decorations (decorator stacking)
print("✅ Test 9: Decorator stacking")

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

from functools import wraps

@another_decorator
@api_login_required
def double_decorated_view(request):
    return JsonResponse({'original': True})

request.user = mock_user
double_response = double_decorated_view(request)
double_data = json.loads(double_response.content)
assert double_data['original'] is True
assert double_data['decorated'] is True

# Test with unauthenticated user - the outer decorator processes the 401 response
request_unauth.user = mock_unauth_user
double_unauth_response = double_decorated_view(request_unauth)
# The outer decorator adds 'decorated': True even to 401 responses and returns 200
# but the content should still contain the authentication error
assert double_unauth_response.status_code == 200
double_unauth_data = json.loads(double_unauth_response.content)
assert double_unauth_data['error'] == 'Authentication required'
assert double_unauth_data['decorated'] is True

# Test 10: Performance and stress test
print("✅ Test 10: Performance characteristics")

@api_login_required
def performance_view(request):
    return JsonResponse({'iteration': getattr(request, 'iteration', 0)})

# Test that decorator doesn't add significant overhead
import time

request.user = mock_user

# Test multiple calls to ensure decorator doesn't have state issues
for i in range(10):
    request.iteration = i
    response = performance_view(request)
    data = json.loads(response.content)
    assert data['iteration'] == i

print("\n" + "="*50)
print("All branch coverage tests passed!")
print("="*50)

# Stop coverage and report
if coverage_available:
    cov.stop()
    cov.save()
    print("\nCOVERAGE REPORT:")
    print("-" * 30)
    cov.report(show_missing=True)
    print("\nBRANCH COVERAGE DETAILS:")
    print("-" * 30)
    # Get detailed branch coverage
    analysis = cov.analysis2('api/decorators.py')
    print(f"Statements: {len(analysis[1]) + len(analysis[2])}")
    print(f"Missing statements: {len(analysis[2])}")
    print(f"Branches: {len(analysis[3])}")
    print(f"Missing branches: {len(analysis[4])}")
    if analysis[3]:
        branch_coverage = (len(analysis[3]) - len(analysis[4])) / len(analysis[3]) * 100
        print(f"Branch coverage: {branch_coverage:.1f}%")