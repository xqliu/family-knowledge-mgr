"""
Comprehensive tests for ai_integration URLs targeting 100% coverage
Converted from test_ai_urls_simple.py to proper pytest format
"""
import pytest
from django.urls import reverse, resolve
from ai_integration.urls import urlpatterns, app_name


class TestAIIntegrationUrls:
    """Comprehensive tests for AI integration URLs"""
    
    def test_app_name(self):
        """Test app_name is correctly set"""
        assert app_name == 'ai_integration'
    
    def test_urlpatterns_exist(self):
        """Test that urlpatterns exist and are not empty"""
        assert urlpatterns is not None
        assert len(urlpatterns) > 0
    
    def test_chat_endpoint_url_pattern(self):
        """Test chat endpoint URL pattern"""
        # Test if the URL pattern exists
        url_found = False
        for pattern in urlpatterns:
            if hasattr(pattern, 'name') and pattern.name == 'chat_endpoint':
                url_found = True
                break
        assert url_found, "chat_endpoint URL pattern not found"
    
    def test_semantic_search_url_pattern(self):
        """Test semantic search URL pattern"""
        # Test if the URL pattern exists
        url_found = False
        for pattern in urlpatterns:
            if hasattr(pattern, 'name') and pattern.name == 'semantic_search':
                url_found = True
                break
        assert url_found, "semantic_search URL pattern not found"
    
    def test_url_pattern_names(self):
        """Test all URL patterns have names"""
        for pattern in urlpatterns:
            if hasattr(pattern, 'name'):
                assert pattern.name is not None
                assert len(pattern.name) > 0
    
    def test_url_pattern_count(self):
        """Test expected number of URL patterns"""
        # Count named patterns
        named_patterns = [p for p in urlpatterns if hasattr(p, 'name') and p.name]
        assert len(named_patterns) >= 2  # Should have at least chat_endpoint and semantic_search
    
    def test_url_reverse_chat_endpoint(self):
        """Test reversing chat endpoint URL"""
        try:
            url = reverse('ai_integration:chat_endpoint')
            assert url is not None
            assert 'chat' in url
        except Exception as e:
            pytest.fail(f"Failed to reverse chat_endpoint URL: {e}")
    
    def test_url_reverse_semantic_search(self):
        """Test reversing semantic search URL"""
        try:
            url = reverse('ai_integration:semantic_search')
            assert url is not None
            assert 'search' in url
        except Exception as e:
            pytest.fail(f"Failed to reverse semantic_search URL: {e}")
    
    def test_url_resolve_patterns(self):
        """Test resolving URL patterns"""
        # Test resolving chat endpoint
        try:
            chat_url = reverse('ai_integration:chat_endpoint')
            resolved = resolve(chat_url)
            assert resolved.view_name == 'ai_integration:chat_endpoint'
        except Exception as e:
            pytest.fail(f"Failed to resolve chat_endpoint: {e}")
        
        # Test resolving semantic search
        try:
            search_url = reverse('ai_integration:semantic_search')
            resolved = resolve(search_url)
            assert resolved.view_name == 'ai_integration:semantic_search'
        except Exception as e:
            pytest.fail(f"Failed to resolve semantic_search: {e}")
    
    def test_url_pattern_structure(self):
        """Test URL pattern structure"""
        pattern_names = []
        for pattern in urlpatterns:
            if hasattr(pattern, 'name') and pattern.name:
                pattern_names.append(pattern.name)
        
        # Verify expected patterns exist
        expected_patterns = ['chat_endpoint', 'semantic_search']
        for expected in expected_patterns:
            assert expected in pattern_names, f"Expected pattern '{expected}' not found"
    
    def test_url_pattern_uniqueness(self):
        """Test that all URL pattern names are unique"""
        pattern_names = []
        for pattern in urlpatterns:
            if hasattr(pattern, 'name') and pattern.name:
                pattern_names.append(pattern.name)
        
        # Check for duplicates
        assert len(pattern_names) == len(set(pattern_names)), "Duplicate URL pattern names found"