"""
Comprehensive tests for api URLs targeting 100% coverage
Converted from test_api_urls_simple.py to proper pytest format
"""
import pytest
from django.urls import reverse, resolve
from api.urls import urlpatterns, app_name


class TestAPIUrls:
    """Comprehensive tests for API URLs"""
    
    def test_app_name(self):
        """Test app_name is correctly set"""
        assert app_name == 'api'
    
    def test_urlpatterns_exist(self):
        """Test that urlpatterns exist and are not empty"""
        assert urlpatterns is not None
        assert len(urlpatterns) > 0
    
    def test_overview_url_pattern(self):
        """Test overview URL pattern"""
        # Test if the URL pattern exists
        url_found = False
        for pattern in urlpatterns:
            if hasattr(pattern, 'name') and pattern.name == 'overview':
                url_found = True
                break
        assert url_found, "overview URL pattern not found"
    
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
        assert len(named_patterns) >= 1  # Should have at least overview
    
    def test_url_reverse_overview(self):
        """Test reversing overview URL"""
        try:
            url = reverse('api:overview')
            assert url is not None
            assert 'overview' in url
        except Exception as e:
            pytest.fail(f"Failed to reverse overview URL: {e}")
    
    def test_url_resolve_patterns(self):
        """Test resolving URL patterns"""
        # Test resolving overview
        try:
            overview_url = reverse('api:overview')
            resolved = resolve(overview_url)
            assert resolved.view_name == 'api:overview'
        except Exception as e:
            pytest.fail(f"Failed to resolve overview: {e}")
    
    def test_url_pattern_structure(self):
        """Test URL pattern structure"""
        pattern_names = []
        for pattern in urlpatterns:
            if hasattr(pattern, 'name') and pattern.name:
                pattern_names.append(pattern.name)
        
        # Verify expected patterns exist
        expected_patterns = ['overview']
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
    
    def test_family_path_inclusion(self):
        """Test that family path is included in URL patterns"""
        # Check if there's a pattern that includes family URLs
        family_pattern_found = False
        for pattern in urlpatterns:
            if hasattr(pattern, 'pattern'):
                pattern_str = str(pattern.pattern)
                if 'family' in pattern_str:
                    family_pattern_found = True
                    break
        assert family_pattern_found, "Family path not found in URL patterns"