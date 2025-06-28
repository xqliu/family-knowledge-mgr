"""
Custom admin views and context processors for Family Knowledge Management System
"""

from django.contrib import admin
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import Person, Story, Event, Multimedia, Timeline


def get_family_dashboard_context():
    """
    Generate context data for the family dashboard
    """
    try:
        # Family statistics
        family_stats = {
            'person_count': Person.objects.count(),
            'story_count': Story.objects.count(),
            'event_count': Event.objects.count(),
            'multimedia_count': Multimedia.objects.count(),
        }
        
        # Recent activities (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        recent_activities = []
        
        # Recent stories
        recent_stories = Story.objects.filter(
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')[:3]
        
        for story in recent_stories:
            recent_activities.append({
                'icon': '📖',
                'title': f'新故事: {story.title[:30]}...' if len(story.title) > 30 else f'新故事: {story.title}',
                'time': story.created_at.strftime('%m月%d日'),
                'url': f'/admin/family/story/{story.id}/change/',
            })
        
        # Recent people
        recent_people = Person.objects.filter(
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')[:2]
        
        for person in recent_people:
            recent_activities.append({
                'icon': '👥',
                'title': f'新成员: {person.name}',
                'time': person.created_at.strftime('%m月%d日'),
                'url': f'/admin/family/person/{person.id}/change/',
            })
        
        # Recent multimedia
        recent_media = Multimedia.objects.filter(
            uploaded_at__gte=thirty_days_ago
        ).order_by('-uploaded_at')[:2]
        
        for media in recent_media:
            recent_activities.append({
                'icon': '📸',
                'title': f'新照片: {media.title or "未命名"}',
                'time': media.uploaded_at.strftime('%m月%d日'),
                'url': f'/admin/family/multimedia/{media.id}/change/',
            })
        
        # Sort by time (most recent first)
        recent_activities.sort(key=lambda x: x['time'], reverse=True)
        recent_activities = recent_activities[:5]  # Limit to 5 items
        
        # Upcoming events (next 60 days)
        upcoming_date = timezone.now() + timedelta(days=60)
        upcoming_events = Event.objects.filter(
            date__gte=timezone.now().date(),
            date__lte=upcoming_date.date()
        ).order_by('date')[:5]
        
        return {
            'family_stats': family_stats,
            'recent_activities': recent_activities,
            'upcoming_events': upcoming_events,
        }
        
    except Exception as e:
        # Fallback in case of any errors
        return {
            'family_stats': {
                'person_count': 0,
                'story_count': 0,
                'event_count': 0,
                'multimedia_count': 0,
            },
            'recent_activities': [],
            'upcoming_events': [],
        }


class FamilyAdminSite(admin.AdminSite):
    """
    Custom admin site with family-specific customizations
    """
    site_header = '家族知识管理系统'
    site_title = '家族知识管理'
    index_title = '欢迎来到家族知识管理系统'
    
    def index(self, request, extra_context=None):
        """
        Override the admin index to include family dashboard data
        """
        if extra_context is None:
            extra_context = {}
        
        # Add family dashboard context
        dashboard_context = get_family_dashboard_context()
        extra_context.update(dashboard_context)
        
        return super().index(request, extra_context)


# Create custom admin site instance
family_admin_site = FamilyAdminSite(name='family_admin')


def family_dashboard_context_processor(request):
    """
    Context processor to provide family dashboard data to templates
    """
    if request.path.startswith('/admin/'):
        return get_family_dashboard_context()
    return {}