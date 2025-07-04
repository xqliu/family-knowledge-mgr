"""
Tests for family admin views and context processors
"""
import pytest
from django.test import TestCase, RequestFactory
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, Mock, MagicMock

from family.admin_views import (
    get_family_dashboard_context,
    FamilyAdminSite,
    family_admin_site,
    family_dashboard_context_processor
)


class TestGetFamilyDashboardContext(TestCase):
    """Test the get_family_dashboard_context function"""
    
    @patch('family.admin_views.Person.objects')
    @patch('family.admin_views.Story.objects')
    @patch('family.admin_views.Event.objects')
    @patch('family.admin_views.Multimedia.objects')
    def test_dashboard_context_with_no_data(self, mock_multimedia, mock_event, mock_story, mock_person):
        """Test dashboard context when no data exists"""
        # Mock count methods to return 0
        mock_person.count.return_value = 0
        mock_story.count.return_value = 0
        mock_event.count.return_value = 0
        mock_multimedia.count.return_value = 0
        
        # Mock filter methods to return empty querysets
        mock_story.filter.return_value.order_by.return_value.__getitem__.return_value = []
        mock_person.filter.return_value.order_by.return_value.__getitem__.return_value = []
        mock_multimedia.filter.return_value.order_by.return_value.__getitem__.return_value = []
        mock_event.filter.return_value.order_by.return_value.__getitem__.return_value = []
        
        context = get_family_dashboard_context()
        
        self.assertIn('family_stats', context)
        self.assertIn('recent_activities', context)
        self.assertIn('upcoming_events', context)
        
        # Check stats are zero
        stats = context['family_stats']
        self.assertEqual(stats['person_count'], 0)
        self.assertEqual(stats['story_count'], 0)
        self.assertEqual(stats['event_count'], 0)
        self.assertEqual(stats['multimedia_count'], 0)
        
        # Check empty lists
        self.assertEqual(len(context['recent_activities']), 0)
        self.assertEqual(len(context['upcoming_events']), 0)
    
    @patch('family.admin_views.Person.objects')
    @patch('family.admin_views.Story.objects')
    @patch('family.admin_views.Event.objects')
    @patch('family.admin_views.Multimedia.objects')
    @patch('family.admin_views.timezone')
    def test_dashboard_context_with_data(self, mock_timezone, mock_multimedia, mock_event, mock_story, mock_person):
        """Test dashboard context with mocked data"""
        # Mock current time
        mock_now = Mock()
        mock_now.date.return_value = Mock()
        mock_timezone.now.return_value = mock_now
        
        # Mock count methods
        mock_person.count.return_value = 1
        mock_story.count.return_value = 1
        mock_event.count.return_value = 1
        mock_multimedia.count.return_value = 1
        
        # Mock filter methods to return empty for recent activities
        mock_story.filter.return_value.order_by.return_value.__getitem__.return_value = []
        mock_person.filter.return_value.order_by.return_value.__getitem__.return_value = []
        mock_multimedia.filter.return_value.order_by.return_value.__getitem__.return_value = []
        mock_event.filter.return_value.order_by.return_value.__getitem__.return_value = []
        
        context = get_family_dashboard_context()
        
        # Check stats
        stats = context['family_stats']
        self.assertEqual(stats['person_count'], 1)
        self.assertEqual(stats['story_count'], 1)
        self.assertEqual(stats['event_count'], 1)
        self.assertEqual(stats['multimedia_count'], 1)
    
    @patch('family.admin_views.Person.objects')
    @patch('family.admin_views.Story.objects')
    @patch('family.admin_views.Event.objects')
    @patch('family.admin_views.Multimedia.objects')
    @patch('family.admin_views.timezone')
    def test_recent_activities_stories(self, mock_timezone, mock_multimedia, mock_event, mock_story, mock_person):
        """Test recent activities include recent stories"""
        # Mock current time
        mock_now = Mock()
        mock_now.date.return_value = Mock()
        mock_timezone.now.return_value = mock_now
        
        # Mock count methods
        mock_person.count.return_value = 0
        mock_story.count.return_value = 1
        mock_event.count.return_value = 0
        mock_multimedia.count.return_value = 0
        
        # Mock story object
        mock_story_obj = Mock()
        mock_story_obj.id = 1
        mock_story_obj.title = "最近的故事"
        mock_story_obj.created_at.strftime.return_value = "07月04日"
        
        # Mock story filter to return the story
        mock_story.filter.return_value.order_by.return_value.__getitem__.return_value = [mock_story_obj]
        
        # Mock other models to return empty
        mock_person.filter.return_value.order_by.return_value.__getitem__.return_value = []
        mock_multimedia.filter.return_value.order_by.return_value.__getitem__.return_value = []
        mock_event.filter.return_value.order_by.return_value.__getitem__.return_value = []
        
        context = get_family_dashboard_context()
        activities = context['recent_activities']
        
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities[0]['icon'], '📖')
        self.assertIn('新故事: 最近的故事', activities[0]['title'])
        self.assertIn('/admin/family/story/1/change/', activities[0]['url'])
    
    @patch('family.admin_views.Person.objects')
    @patch('family.admin_views.Story.objects')
    @patch('family.admin_views.Event.objects')
    @patch('family.admin_views.Multimedia.objects')
    @patch('family.admin_views.timezone')
    def test_recent_activities_long_story_title(self, mock_timezone, mock_multimedia, mock_event, mock_story, mock_person):
        """Test recent activities truncate long story titles"""
        # Mock current time
        mock_now = Mock()
        mock_now.date.return_value = Mock()
        mock_timezone.now.return_value = mock_now
        
        # Mock count methods
        mock_person.count.return_value = 0
        mock_story.count.return_value = 1
        mock_event.count.return_value = 0
        mock_multimedia.count.return_value = 0
        
        # Mock story with long title
        long_title = "这是一个非常非常长的故事标题，应该被截断到30个字符"
        mock_story_obj = Mock()
        mock_story_obj.id = 1
        mock_story_obj.title = long_title
        mock_story_obj.created_at.strftime.return_value = "07月04日"
        
        mock_story.filter.return_value.order_by.return_value.__getitem__.return_value = [mock_story_obj]
        mock_person.filter.return_value.order_by.return_value.__getitem__.return_value = []
        mock_multimedia.filter.return_value.order_by.return_value.__getitem__.return_value = []
        mock_event.filter.return_value.order_by.return_value.__getitem__.return_value = []
        
        context = get_family_dashboard_context()
        activities = context['recent_activities']
        
        self.assertEqual(len(activities), 1)
        self.assertTrue(activities[0]['title'].endswith('...'))
        self.assertEqual(len(activities[0]['title']), 34)  # "新故事: " + 30 chars + "..."
    
    @patch('family.admin_views.Person.objects')
    @patch('family.admin_views.Story.objects')
    @patch('family.admin_views.Event.objects')
    @patch('family.admin_views.Multimedia.objects')
    @patch('family.admin_views.timezone')
    def test_recent_activities_people(self, mock_timezone, mock_multimedia, mock_event, mock_story, mock_person):
        """Test recent activities include recent people"""
        # Mock current time
        mock_now = Mock()
        mock_now.date.return_value = Mock()
        mock_timezone.now.return_value = mock_now
        
        # Mock count methods
        mock_person.count.return_value = 1
        mock_story.count.return_value = 0
        mock_event.count.return_value = 0
        mock_multimedia.count.return_value = 0
        
        # Mock person object
        mock_person_obj = Mock()
        mock_person_obj.id = 1
        mock_person_obj.name = "新成员"
        mock_person_obj.created_at.strftime.return_value = "07月04日"
        
        mock_story.filter.return_value.order_by.return_value.__getitem__.return_value = []
        mock_person.filter.return_value.order_by.return_value.__getitem__.return_value = [mock_person_obj]
        mock_multimedia.filter.return_value.order_by.return_value.__getitem__.return_value = []
        mock_event.filter.return_value.order_by.return_value.__getitem__.return_value = []
        
        context = get_family_dashboard_context()
        activities = context['recent_activities']
        
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities[0]['icon'], '👥')
        self.assertEqual(activities[0]['title'], '新成员: 新成员')
        self.assertIn('/admin/family/person/1/change/', activities[0]['url'])
    
    @patch('family.admin_views.Person.objects')
    @patch('family.admin_views.Story.objects')
    @patch('family.admin_views.Event.objects')
    @patch('family.admin_views.Multimedia.objects')
    @patch('family.admin_views.timezone')
    def test_recent_activities_multimedia(self, mock_timezone, mock_multimedia, mock_event, mock_story, mock_person):
        """Test recent activities include recent multimedia"""
        # Mock current time
        mock_now = Mock()
        mock_now.date.return_value = Mock()
        mock_timezone.now.return_value = mock_now
        
        # Mock count methods
        mock_person.count.return_value = 0
        mock_story.count.return_value = 0
        mock_event.count.return_value = 0
        mock_multimedia.count.return_value = 1
        
        # Mock multimedia object
        mock_media_obj = Mock()
        mock_media_obj.id = 1
        mock_media_obj.title = "新照片"
        mock_media_obj.uploaded_at.strftime.return_value = "07月04日"
        
        mock_story.filter.return_value.order_by.return_value.__getitem__.return_value = []
        mock_person.filter.return_value.order_by.return_value.__getitem__.return_value = []
        mock_multimedia.filter.return_value.order_by.return_value.__getitem__.return_value = [mock_media_obj]
        mock_event.filter.return_value.order_by.return_value.__getitem__.return_value = []
        
        context = get_family_dashboard_context()
        activities = context['recent_activities']
        
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities[0]['icon'], '📸')
        self.assertEqual(activities[0]['title'], '新照片: 新照片')
        self.assertIn('/admin/family/multimedia/1/change/', activities[0]['url'])
    
    @patch('family.admin_views.Person.objects')
    @patch('family.admin_views.Story.objects')
    @patch('family.admin_views.Event.objects')
    @patch('family.admin_views.Multimedia.objects')
    @patch('family.admin_views.timezone')
    def test_recent_activities_multimedia_no_title(self, mock_timezone, mock_multimedia, mock_event, mock_story, mock_person):
        """Test recent activities handle multimedia without title"""
        # Mock current time
        mock_now = Mock()
        mock_now.date.return_value = Mock()
        mock_timezone.now.return_value = mock_now
        
        # Mock count methods
        mock_person.count.return_value = 0
        mock_story.count.return_value = 0
        mock_event.count.return_value = 0
        mock_multimedia.count.return_value = 1
        
        # Mock multimedia object without title
        mock_media_obj = Mock()
        mock_media_obj.id = 1
        mock_media_obj.title = None
        mock_media_obj.uploaded_at.strftime.return_value = "07月04日"
        
        mock_story.filter.return_value.order_by.return_value.__getitem__.return_value = []
        mock_person.filter.return_value.order_by.return_value.__getitem__.return_value = []
        mock_multimedia.filter.return_value.order_by.return_value.__getitem__.return_value = [mock_media_obj]
        mock_event.filter.return_value.order_by.return_value.__getitem__.return_value = []
        
        context = get_family_dashboard_context()
        activities = context['recent_activities']
        
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities[0]['title'], '新照片: 未命名')
    
    @patch('family.admin_views.Person.objects')
    @patch('family.admin_views.Story.objects')
    @patch('family.admin_views.Event.objects')
    @patch('family.admin_views.Multimedia.objects')
    @patch('family.admin_views.timezone')
    def test_upcoming_events(self, mock_timezone, mock_multimedia, mock_event, mock_story, mock_person):
        """Test upcoming events functionality"""
        # Mock current time
        mock_now = Mock()
        mock_now.date.return_value = Mock()
        mock_timezone.now.return_value = mock_now
        
        # Mock count methods
        mock_person.count.return_value = 0
        mock_story.count.return_value = 0
        mock_event.count.return_value = 1
        mock_multimedia.count.return_value = 0
        
        # Mock upcoming event
        mock_event_obj = Mock()
        mock_event_obj.title = "未来活动"
        
        # Mock recent activities to be empty
        mock_story.filter.return_value.order_by.return_value.__getitem__.return_value = []
        mock_person.filter.return_value.order_by.return_value.__getitem__.return_value = []
        mock_multimedia.filter.return_value.order_by.return_value.__getitem__.return_value = []
        
        # Mock upcoming events
        mock_event.filter.return_value.order_by.return_value.__getitem__.return_value = [mock_event_obj]
        
        context = get_family_dashboard_context()
        upcoming = context['upcoming_events']
        
        self.assertEqual(len(upcoming), 1)
        self.assertEqual(upcoming[0], mock_event_obj)
    
    @patch('family.admin_views.Story.objects')
    def test_dashboard_context_exception_handling(self, mock_story_objects):
        """Test exception handling in dashboard context"""
        # Mock an exception
        mock_story_objects.count.side_effect = Exception("Database error")
        
        context = get_family_dashboard_context()
        
        # Should return fallback data
        self.assertEqual(context['family_stats']['person_count'], 0)
        self.assertEqual(context['family_stats']['story_count'], 0)
        self.assertEqual(context['family_stats']['event_count'], 0)
        self.assertEqual(context['family_stats']['multimedia_count'], 0)
        self.assertEqual(len(context['recent_activities']), 0)
        self.assertEqual(len(context['upcoming_events']), 0)


class TestFamilyAdminSite(TestCase):
    """Test the FamilyAdminSite class"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = FamilyAdminSite(name='test_family_admin')
    
    def test_admin_site_attributes(self):
        """Test admin site custom attributes"""
        self.assertEqual(self.admin_site.site_header, '家族知识管理系统')
        self.assertEqual(self.admin_site.site_title, '家族知识管理')
        self.assertEqual(self.admin_site.index_title, '欢迎来到家族知识管理系统')
    
    @patch('family.admin_views.get_family_dashboard_context')
    def test_admin_site_index_adds_context(self, mock_get_context):
        """Test that admin site index adds dashboard context"""
        mock_context = {
            'family_stats': {'person_count': 5},
            'recent_activities': [],
            'upcoming_events': []
        }
        mock_get_context.return_value = mock_context
        
        # Mock user
        mock_user = Mock()
        mock_user.is_active = True
        mock_user.is_staff = True
        
        request = self.factory.get('/admin/')
        request.user = mock_user
        
        with patch.object(self.admin_site, 'has_permission', return_value=True):
            with patch('django.contrib.admin.site.AdminSite.index') as mock_super_index:
                mock_super_index.return_value = Mock()
                
                # Call index method
                response = self.admin_site.index(request)
                
                # Verify get_family_dashboard_context was called
                mock_get_context.assert_called_once()
    
    @patch('family.admin_views.get_family_dashboard_context')
    def test_admin_site_index_with_existing_context(self, mock_get_context):
        """Test admin site index with existing extra_context"""
        mock_user = Mock()
        mock_user.is_active = True
        mock_user.is_staff = True
        
        request = self.factory.get('/admin/')
        request.user = mock_user
        
        existing_context = {'custom_key': 'custom_value'}
        mock_get_context.return_value = {'family_stats': {}}
        
        with patch.object(self.admin_site, 'has_permission', return_value=True):
            with patch('django.contrib.admin.site.AdminSite.index') as mock_super_index:
                mock_super_index.return_value = Mock()
                
                # Call index with existing context
                response = self.admin_site.index(request, extra_context=existing_context)
                
                mock_get_context.assert_called_once()


class TestFamilyAdminSiteInstance(TestCase):
    """Test the family_admin_site instance"""
    
    def test_family_admin_site_instance(self):
        """Test that family_admin_site is properly configured"""
        self.assertIsInstance(family_admin_site, FamilyAdminSite)
        self.assertEqual(family_admin_site.name, 'family_admin')


class TestFamilyDashboardContextProcessor(TestCase):
    """Test the family_dashboard_context_processor function"""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    @patch('family.admin_views.get_family_dashboard_context')
    def test_context_processor_for_admin_paths(self, mock_get_context):
        """Test context processor returns data for admin paths"""
        mock_context = {
            'family_stats': {'person_count': 3},
            'recent_activities': [],
            'upcoming_events': []
        }
        mock_get_context.return_value = mock_context
        
        request = self.factory.get('/admin/')
        request.path = '/admin/'
        
        result = family_dashboard_context_processor(request)
        
        mock_get_context.assert_called_once()
        self.assertEqual(result, mock_context)
    
    @patch('family.admin_views.get_family_dashboard_context')
    def test_context_processor_for_admin_subpaths(self, mock_get_context):
        """Test context processor returns data for admin subpaths"""
        mock_context = {'family_stats': {}}
        mock_get_context.return_value = mock_context
        
        request = self.factory.get('/admin/family/person/')
        request.path = '/admin/family/person/'
        
        result = family_dashboard_context_processor(request)
        
        mock_get_context.assert_called_once()
        self.assertEqual(result, mock_context)
    
    @patch('family.admin_views.get_family_dashboard_context')
    def test_context_processor_for_non_admin_paths(self, mock_get_context):
        """Test context processor returns empty dict for non-admin paths"""
        request = self.factory.get('/api/health/')
        request.path = '/api/health/'
        
        result = family_dashboard_context_processor(request)
        
        mock_get_context.assert_not_called()
        self.assertEqual(result, {})
    
    @patch('family.admin_views.get_family_dashboard_context')
    def test_context_processor_for_app_paths(self, mock_get_context):
        """Test context processor returns empty dict for app paths"""
        request = self.factory.get('/app/')
        request.path = '/app/'
        
        result = family_dashboard_context_processor(request)
        
        mock_get_context.assert_not_called()
        self.assertEqual(result, {})