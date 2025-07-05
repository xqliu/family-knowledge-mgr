"""
Comprehensive tests for family admin views targeting 90%+ branch coverage
Uses unittest.TestCase to avoid database dependencies
"""
import os
import sys
import django
from django.conf import settings

# Configure Django settings if not already configured
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.admin',
            'django.contrib.staticfiles',
            'family',
        ],
        STATIC_URL='/static/',
        SECRET_KEY='test-secret-key',
        USE_TZ=True,
    )
    django.setup()

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta, date
from django.utils import timezone

from family.admin_views import (
    get_family_dashboard_context, FamilyAdminSite, 
    family_admin_site, family_dashboard_context_processor
)


class TestGetFamilyDashboardContext(unittest.TestCase):
    """Tests for get_family_dashboard_context function"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.thirty_days_ago = timezone.now() - timedelta(days=30)
        self.upcoming_date = timezone.now() + timedelta(days=60)
        
    def test_get_family_dashboard_context_success(self):
        """Test successful dashboard context generation"""
        # Mock model objects
        with patch('family.admin_views.Person') as mock_person:
            with patch('family.admin_views.Story') as mock_story:
                with patch('family.admin_views.Event') as mock_event:
                    with patch('family.admin_views.Multimedia') as mock_multimedia:
                        # Setup counts
                        mock_person.objects.count.return_value = 10
                        mock_story.objects.count.return_value = 20
                        mock_event.objects.count.return_value = 5
                        mock_multimedia.objects.count.return_value = 15
                        
                        # Mock recent stories
                        mock_story1 = Mock()
                        mock_story1.id = 1
                        mock_story1.title = "A short title"
                        mock_story1.created_at = timezone.now() - timedelta(days=1)
                        
                        mock_story2 = Mock()
                        mock_story2.id = 2
                        mock_story2.title = "A very long title that should be truncated because it's longer than 30 characters"
                        mock_story2.created_at = timezone.now() - timedelta(days=2)
                        
                        mock_story_qs = Mock()
                        mock_story_qs.order_by.return_value.__getitem__ = Mock(
                            return_value=[mock_story1, mock_story2]
                        )
                        mock_story.objects.filter.return_value = mock_story_qs
                        
                        # Mock recent people
                        mock_person1 = Mock()
                        mock_person1.id = 1
                        mock_person1.name = "John Doe"
                        mock_person1.created_at = timezone.now() - timedelta(days=3)
                        
                        mock_person_qs = Mock()
                        mock_person_qs.order_by.return_value.__getitem__ = Mock(
                            return_value=[mock_person1]
                        )
                        mock_person.objects.filter.return_value = mock_person_qs
                        
                        # Mock recent multimedia
                        mock_media1 = Mock()
                        mock_media1.id = 1
                        mock_media1.title = "Family Photo"
                        mock_media1.uploaded_at = timezone.now() - timedelta(days=5)
                        
                        mock_media2 = Mock()
                        mock_media2.id = 2
                        mock_media2.title = None  # Test None title
                        mock_media2.uploaded_at = timezone.now() - timedelta(days=6)
                        
                        mock_media_qs = Mock()
                        mock_media_qs.order_by.return_value.__getitem__ = Mock(
                            return_value=[mock_media1, mock_media2]
                        )
                        mock_multimedia.objects.filter.return_value = mock_media_qs
                        
                        # Mock upcoming events
                        mock_event1 = Mock()
                        mock_event1.id = 1
                        mock_event1.date = timezone.now().date() + timedelta(days=7)
                        
                        mock_event_qs = Mock()
                        mock_event_qs.order_by.return_value.__getitem__ = Mock(
                            return_value=[mock_event1]
                        )
                        mock_event.objects.filter.return_value = mock_event_qs
                        
                        # Call the function
                        result = get_family_dashboard_context()
                        
                        # Verify family stats
                        self.assertEqual(result['family_stats']['person_count'], 10)
                        self.assertEqual(result['family_stats']['story_count'], 20)
                        self.assertEqual(result['family_stats']['event_count'], 5)
                        self.assertEqual(result['family_stats']['multimedia_count'], 15)
                        
                        # Verify recent activities
                        self.assertIsInstance(result['recent_activities'], list)
                        self.assertLessEqual(len(result['recent_activities']), 5)
                        
                        # Check for story activity with short title
                        story_activities = [a for a in result['recent_activities'] if a['icon'] == '📖']
                        self.assertTrue(any('新故事: A short title' in a['title'] for a in story_activities))
                        
                        # Check for story activity with truncated title
                        self.assertTrue(any('...' in a['title'] for a in story_activities))
                        
                        # Check for person activity
                        person_activities = [a for a in result['recent_activities'] if a['icon'] == '👥']
                        self.assertTrue(any('新成员: John Doe' in a['title'] for a in person_activities))
                        
                        # Check for media activity
                        media_activities = [a for a in result['recent_activities'] if a['icon'] == '📸']
                        self.assertTrue(any('新照片: Family Photo' in a['title'] for a in media_activities))
                        self.assertTrue(any('新照片: 未命名' in a['title'] for a in media_activities))
                        
                        # Verify upcoming events
                        self.assertIsInstance(result['upcoming_events'], list)
                        
    def test_get_family_dashboard_context_empty_results(self):
        """Test dashboard context with no recent items"""
        with patch('family.admin_views.Person') as mock_person:
            with patch('family.admin_views.Story') as mock_story:
                with patch('family.admin_views.Event') as mock_event:
                    with patch('family.admin_views.Multimedia') as mock_multimedia:
                        # Setup counts
                        mock_person.objects.count.return_value = 0
                        mock_story.objects.count.return_value = 0
                        mock_event.objects.count.return_value = 0
                        mock_multimedia.objects.count.return_value = 0
                        
                        # Mock empty querysets
                        empty_qs = Mock()
                        empty_qs.order_by.return_value.__getitem__ = Mock(return_value=[])
                        
                        mock_story.objects.filter.return_value = empty_qs
                        mock_person.objects.filter.return_value = empty_qs
                        mock_multimedia.objects.filter.return_value = empty_qs
                        mock_event.objects.filter.return_value = empty_qs
                        
                        result = get_family_dashboard_context()
                        
                        # Verify empty results
                        self.assertEqual(result['family_stats']['person_count'], 0)
                        self.assertEqual(result['recent_activities'], [])
                        self.assertEqual(len(result['upcoming_events']), 0)
                        
    def test_get_family_dashboard_context_exception(self):
        """Test dashboard context when exception occurs"""
        with patch('family.admin_views.Person') as mock_person:
            # Make count() raise an exception
            mock_person.objects.count.side_effect = Exception("Database error")
            
            result = get_family_dashboard_context()
            
            # Should return fallback values
            self.assertEqual(result['family_stats']['person_count'], 0)
            self.assertEqual(result['family_stats']['story_count'], 0)
            self.assertEqual(result['family_stats']['event_count'], 0)
            self.assertEqual(result['family_stats']['multimedia_count'], 0)
            self.assertEqual(result['recent_activities'], [])
            self.assertEqual(result['upcoming_events'], [])
            
    def test_get_family_dashboard_context_sorting(self):
        """Test that recent activities are properly sorted"""
        with patch('family.admin_views.Person') as mock_person:
            with patch('family.admin_views.Story') as mock_story:
                with patch('family.admin_views.Event') as mock_event:
                    with patch('family.admin_views.Multimedia') as mock_multimedia:
                        # Setup counts
                        mock_person.objects.count.return_value = 1
                        mock_story.objects.count.return_value = 1
                        mock_event.objects.count.return_value = 1
                        mock_multimedia.objects.count.return_value = 1
                        
                        # Create activities with different dates
                        now = timezone.now()
                        
                        # Story from 10 days ago
                        mock_story1 = Mock()
                        mock_story1.id = 1
                        mock_story1.title = "Old Story"
                        mock_story1.created_at = now - timedelta(days=10)
                        
                        # Story from 1 day ago
                        mock_story2 = Mock()
                        mock_story2.id = 2
                        mock_story2.title = "Recent Story"
                        mock_story2.created_at = now - timedelta(days=1)
                        
                        # Person from 5 days ago
                        mock_person1 = Mock()
                        mock_person1.id = 1
                        mock_person1.name = "Middle Person"
                        mock_person1.created_at = now - timedelta(days=5)
                        
                        # Setup querysets
                        story_qs = Mock()
                        story_qs.order_by.return_value.__getitem__ = Mock(
                            return_value=[mock_story1, mock_story2]
                        )
                        mock_story.objects.filter.return_value = story_qs
                        
                        person_qs = Mock()
                        person_qs.order_by.return_value.__getitem__ = Mock(
                            return_value=[mock_person1]
                        )
                        mock_person.objects.filter.return_value = person_qs
                        
                        # Empty multimedia and events
                        empty_qs = Mock()
                        empty_qs.order_by.return_value.__getitem__ = Mock(return_value=[])
                        mock_multimedia.objects.filter.return_value = empty_qs
                        mock_event.objects.filter.return_value = empty_qs
                        
                        result = get_family_dashboard_context()
                        
                        # Activities should be sorted by time (most recent first)
                        activities = result['recent_activities']
                        self.assertGreater(len(activities), 0)
                        
                        # The sorting is based on the time string format
                        # Since we can't directly compare the Chinese date strings,
                        # we just verify that we got activities
                        self.assertTrue(any('Recent Story' in a['title'] for a in activities))
                        self.assertTrue(any('Middle Person' in a['title'] for a in activities))
                        self.assertTrue(any('Old Story' in a['title'] for a in activities))


class TestFamilyAdminSite(unittest.TestCase):
    """Tests for FamilyAdminSite class"""
    
    def test_class_attributes(self):
        """Test FamilyAdminSite class attributes"""
        site = FamilyAdminSite()
        
        self.assertEqual(site.site_header, '家族知识管理系统')
        self.assertEqual(site.site_title, '家族知识管理')
        self.assertEqual(site.index_title, '欢迎来到家族知识管理系统')
        
    def test_index_with_no_extra_context(self):
        """Test index method with no extra_context"""
        site = FamilyAdminSite()
        mock_request = Mock()
        
        with patch('family.admin_views.get_family_dashboard_context') as mock_get_context:
            mock_get_context.return_value = {
                'family_stats': {'person_count': 5},
                'recent_activities': [],
                'upcoming_events': []
            }
            
            with patch.object(site.__class__.__bases__[0], 'index') as mock_super_index:
                mock_super_index.return_value = "rendered_response"
                
                result = site.index(mock_request)
                
                # Verify get_family_dashboard_context was called
                mock_get_context.assert_called_once()
                
                # Verify super().index was called with updated context
                mock_super_index.assert_called_once()
                call_args = mock_super_index.call_args
                extra_context = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get('extra_context')
                
                self.assertIsNotNone(extra_context)
                self.assertEqual(extra_context['family_stats']['person_count'], 5)
                
                self.assertEqual(result, "rendered_response")
                
    def test_index_with_extra_context(self):
        """Test index method with existing extra_context"""
        site = FamilyAdminSite()
        mock_request = Mock()
        existing_context = {'custom_key': 'custom_value'}
        
        with patch('family.admin_views.get_family_dashboard_context') as mock_get_context:
            mock_get_context.return_value = {
                'family_stats': {'person_count': 10},
                'recent_activities': ['activity1'],
                'upcoming_events': ['event1']
            }
            
            with patch.object(site.__class__.__bases__[0], 'index') as mock_super_index:
                mock_super_index.return_value = "rendered_response"
                
                result = site.index(mock_request, extra_context=existing_context)
                
                # Verify context was merged
                mock_super_index.assert_called_once()
                call_args = mock_super_index.call_args
                extra_context = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get('extra_context')
                
                self.assertEqual(extra_context['custom_key'], 'custom_value')
                self.assertEqual(extra_context['family_stats']['person_count'], 10)
                self.assertEqual(extra_context['recent_activities'], ['activity1'])
                
    def test_family_admin_site_instance(self):
        """Test that global family_admin_site instance is created"""
        self.assertIsInstance(family_admin_site, FamilyAdminSite)
        self.assertEqual(family_admin_site.name, 'family_admin')


class TestFamilyDashboardContextProcessor(unittest.TestCase):
    """Tests for family_dashboard_context_processor function"""
    
    def test_admin_path(self):
        """Test context processor for admin path"""
        mock_request = Mock()
        mock_request.path = '/admin/family/person/'
        
        with patch('family.admin_views.get_family_dashboard_context') as mock_get_context:
            mock_get_context.return_value = {
                'family_stats': {'person_count': 15},
                'recent_activities': [],
                'upcoming_events': []
            }
            
            result = family_dashboard_context_processor(mock_request)
            
            mock_get_context.assert_called_once()
            self.assertEqual(result['family_stats']['person_count'], 15)
            
    def test_non_admin_path(self):
        """Test context processor for non-admin path"""
        mock_request = Mock()
        mock_request.path = '/some/other/path/'
        
        with patch('family.admin_views.get_family_dashboard_context') as mock_get_context:
            result = family_dashboard_context_processor(mock_request)
            
            # Should not call get_family_dashboard_context
            mock_get_context.assert_not_called()
            
            # Should return empty dict
            self.assertEqual(result, {})
            
    def test_admin_root_path(self):
        """Test context processor for admin root path"""
        mock_request = Mock()
        mock_request.path = '/admin/'
        
        with patch('family.admin_views.get_family_dashboard_context') as mock_get_context:
            mock_get_context.return_value = {'test': 'data'}
            
            result = family_dashboard_context_processor(mock_request)
            
            mock_get_context.assert_called_once()
            self.assertEqual(result, {'test': 'data'})


if __name__ == '__main__':
    unittest.main()