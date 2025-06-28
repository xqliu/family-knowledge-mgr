from django.contrib import admin
from .models import (
    Person, Location, Institution, Event, Story, Multimedia,
    Relationship, Health, Heritage, Planning, Career, Assets, Timeline
)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'gender', 'birth_date', 'email', 'created_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['name', 'email', 'bio']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'gender', 'birth_date', 'death_date', 'photo')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Additional Information', {
            'fields': ('bio',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'location_type', 'address', 'created_at']
    list_filter = ['location_type', 'created_at']
    search_fields = ['name', 'address', 'description']
    readonly_fields = ['created_at']


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ['name', 'institution_type', 'website', 'phone', 'created_at']
    list_filter = ['institution_type', 'created_at']
    search_fields = ['name', 'description', 'email']
    readonly_fields = ['created_at']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'event_type', 'start_date', 'location', 'created_at']
    list_filter = ['event_type', 'start_date', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['participants']
    date_hierarchy = 'start_date'
    fieldsets = (
        ('Event Information', {
            'fields': ('name', 'event_type', 'description')
        }),
        ('Time & Location', {
            'fields': ('start_date', 'end_date', 'location', 'institution')
        }),
        ('Participants', {
            'fields': ('participants',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'story_type', 'date_occurred', 'location', 'created_at']
    list_filter = ['story_type', 'date_occurred', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['people', 'events']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Story Information', {
            'fields': ('title', 'story_type', 'content')
        }),
        ('Context', {
            'fields': ('date_occurred', 'location')
        }),
        ('Relationships', {
            'fields': ('people', 'events')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Multimedia)
class MultimediaAdmin(admin.ModelAdmin):
    list_display = ['title', 'media_type', 'file', 'created_date', 'created_at']
    list_filter = ['media_type', 'created_date', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'file_size']
    filter_horizontal = ['people', 'events', 'stories']
    fieldsets = (
        ('Media Information', {
            'fields': ('title', 'media_type', 'description', 'file')
        }),
        ('Metadata', {
            'fields': ('file_size', 'created_date', 'location')
        }),
        ('Relationships', {
            'fields': ('people', 'events', 'stories')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    list_display = ['person_from', 'relationship_type', 'person_to', 'start_date', 'created_at']
    list_filter = ['relationship_type', 'start_date', 'created_at']
    search_fields = ['person_from__name', 'person_to__name', 'description']
    readonly_fields = ['created_at']


@admin.register(Health)
class HealthAdmin(admin.ModelAdmin):
    list_display = ['person', 'record_type', 'title', 'date', 'is_hereditary', 'created_at']
    list_filter = ['record_type', 'is_hereditary', 'date', 'created_at']
    search_fields = ['person__name', 'title', 'description', 'doctor']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'


@admin.register(Heritage)
class HeritageAdmin(admin.ModelAdmin):
    list_display = ['title', 'heritage_type', 'origin_person', 'importance', 'created_at']
    list_filter = ['heritage_type', 'importance', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at']
    filter_horizontal = ['inheritors', 'stories', 'events']


@admin.register(Planning)
class PlanningAdmin(admin.ModelAdmin):
    list_display = ['title', 'time_range', 'priority', 'status', 'target_date', 'created_at']
    list_filter = ['time_range', 'priority', 'status', 'created_at']
    search_fields = ['title', 'description', 'expected_outcome']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['involved_people']
    date_hierarchy = 'target_date'


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ['person', 'career_type', 'title', 'institution', 'start_date', 'end_date']
    list_filter = ['career_type', 'start_date', 'created_at']
    search_fields = ['person__name', 'title', 'description', 'achievements']
    readonly_fields = ['created_at']
    filter_horizontal = ['events']
    date_hierarchy = 'start_date'


@admin.register(Assets)
class AssetsAdmin(admin.ModelAdmin):
    list_display = ['name', 'asset_type', 'legal_status', 'estimated_value', 'importance', 'created_at']
    list_filter = ['asset_type', 'legal_status', 'importance', 'created_at']
    search_fields = ['name', 'description', 'location']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['owners', 'related_documents', 'plans']


@admin.register(Timeline)
class TimelineAdmin(admin.ModelAdmin):
    list_display = ['title', 'timeline_type', 'date', 'end_date', 'importance', 'created_at']
    list_filter = ['timeline_type', 'importance', 'date', 'created_at']
    search_fields = ['title', 'description', 'historical_context']
    readonly_fields = ['created_at']
    filter_horizontal = ['people', 'events', 'stories']
    date_hierarchy = 'date'