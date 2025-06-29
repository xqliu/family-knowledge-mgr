import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal
from datetime import date, datetime

from family.models import (
    Person, Location, Institution, Event, Story, Multimedia,
    Relationship, Health, Heritage, Planning, Career, Assets, Timeline
)
from family.tests.factories import (
    PersonFactory, LocationFactory, InstitutionFactory, EventFactory,
    StoryFactory, MultimediaFactory, RelationshipFactory, HealthFactory,
    HeritageFactory, PlanningFactory, CareerFactory, AssetsFactory, TimelineFactory
)


@pytest.mark.django_db
class TestPersonModel:
    
    def test_person_creation(self):
        person = PersonFactory()
        assert person.name
        assert person.created_at
        assert person.updated_at
        assert str(person) == person.name
    
    def test_person_gender_choices(self):
        person = PersonFactory(gender='M')
        assert person.gender == 'M'
        
        person = PersonFactory(gender='F')
        assert person.gender == 'F'
        
        person = PersonFactory(gender='O')
        assert person.gender == 'O'
    
    def test_person_optional_fields(self):
        person = PersonFactory(
            birth_date=None,
            death_date=None,
            photo='',
            email='',
            phone=''
        )
        assert person.birth_date is None
        assert person.death_date is None
        assert person.photo == ''
        assert person.email == ''
        assert person.phone == ''
    
    def test_person_ordering(self):
        person1 = PersonFactory(name='Alice')
        person2 = PersonFactory(name='Bob')
        person3 = PersonFactory(name='Charlie')
        
        people = Person.objects.all()
        assert people[0].name == 'Alice'
        assert people[1].name == 'Bob'
        assert people[2].name == 'Charlie'


@pytest.mark.django_db
class TestLocationModel:
    
    def test_location_creation(self):
        location = LocationFactory()
        assert location.name
        assert location.created_at
        assert str(location) == location.name
    
    def test_location_coordinates(self):
        location = LocationFactory(
            latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0060')
        )
        assert location.latitude == Decimal('40.7128')
        assert location.longitude == Decimal('-74.0060')
    
    def test_location_type_choices(self):
        for location_type, _ in Location.LOCATION_TYPES:
            location = LocationFactory(location_type=location_type)
            assert location.location_type == location_type


@pytest.mark.django_db
class TestEventModel:
    
    def test_event_creation(self):
        event = EventFactory()
        assert event.name
        assert event.start_date
        assert event.created_at
        assert event.updated_at
        assert str(event) == f"{event.name} ({event.start_date.year})"
    
    def test_event_with_participants(self):
        event = EventFactory()
        person1 = PersonFactory()
        person2 = PersonFactory()
        
        event.participants.add(person1, person2)
        
        assert event.participants.count() == 2
        assert person1 in event.participants.all()
        assert person2 in event.participants.all()
    
    def test_event_ordering(self):
        event1 = EventFactory(start_date=datetime(2023, 1, 1))
        event2 = EventFactory(start_date=datetime(2024, 1, 1))
        
        events = Event.objects.all()
        assert events[0] == event2  # Most recent first
        assert events[1] == event1


@pytest.mark.django_db
class TestStoryModel:
    
    def test_story_creation(self):
        story = StoryFactory()
        assert story.title
        assert story.content
        assert story.created_at
        assert story.updated_at
        assert str(story) == story.title
    
    def test_story_with_relationships(self):
        story = StoryFactory()
        person = PersonFactory()
        event = EventFactory()
        
        story.people.add(person)
        story.events.add(event)
        
        assert story.people.count() == 1
        assert story.events.count() == 1
        assert person in story.people.all()
        assert event in story.events.all()
    
    def test_story_ordering(self):
        story1 = StoryFactory()
        story2 = StoryFactory()
        
        stories = Story.objects.all()
        # Most recently created first
        assert stories[0].created_at >= stories[1].created_at


@pytest.mark.django_db
class TestRelationshipModel:
    
    def test_relationship_creation(self):
        person1 = PersonFactory()
        person2 = PersonFactory()
        relationship = RelationshipFactory(
            person_from=person1,
            person_to=person2,
            relationship_type='parent'
        )
        
        assert relationship.person_from == person1
        assert relationship.person_to == person2
        assert relationship.relationship_type == 'parent'
        assert str(relationship) == f"{person1} -> {person2} (parent)"
    
    def test_relationship_unique_constraint(self):
        person1 = PersonFactory()
        person2 = PersonFactory()
        
        # First relationship should be created successfully
        RelationshipFactory(
            person_from=person1,
            person_to=person2,
            relationship_type='parent'
        )
        
        # Second identical relationship should raise IntegrityError
        with pytest.raises(IntegrityError):
            RelationshipFactory(
                person_from=person1,
                person_to=person2,
                relationship_type='parent'
            )


@pytest.mark.django_db
class TestHealthModel:
    
    def test_health_record_creation(self):
        health = HealthFactory()
        assert health.person
        assert health.title
        assert health.description
        assert health.date
        assert str(health) == f"{health.person.name} - {health.title}"
    
    def test_health_record_ordering(self):
        person = PersonFactory()
        health1 = HealthFactory(person=person, date=date(2023, 1, 1))
        health2 = HealthFactory(person=person, date=date(2024, 1, 1))
        
        records = Health.objects.filter(person=person)
        assert records[0] == health2  # Most recent first
        assert records[1] == health1


@pytest.mark.django_db
class TestHeritageModel:
    
    def test_heritage_creation(self):
        heritage = HeritageFactory()
        assert heritage.title
        assert heritage.description
        assert heritage.origin_person
        assert str(heritage) == heritage.title
    
    def test_heritage_with_inheritors(self):
        heritage = HeritageFactory()
        person1 = PersonFactory()
        person2 = PersonFactory()
        
        heritage.inheritors.add(person1, person2)
        
        assert heritage.inheritors.count() == 2
        assert person1 in heritage.inheritors.all()
        assert person2 in heritage.inheritors.all()


@pytest.mark.django_db
class TestPlanningModel:
    
    def test_planning_creation(self):
        plan = PlanningFactory()
        assert plan.title
        assert plan.description
        assert plan.status == 'planned' or plan.status in ['in_progress', 'completed', 'cancelled']
        assert str(plan) == plan.title
    
    def test_planning_with_people(self):
        plan = PlanningFactory()
        person1 = PersonFactory()
        person2 = PersonFactory()
        
        plan.involved_people.add(person1, person2)
        
        assert plan.involved_people.count() == 2
        assert person1 in plan.involved_people.all()
        assert person2 in plan.involved_people.all()


@pytest.mark.django_db
class TestAssetsModel:
    
    def test_assets_creation(self):
        asset = AssetsFactory()
        assert asset.name
        assert asset.asset_type
        assert str(asset) == asset.name
    
    def test_assets_with_owners(self):
        asset = AssetsFactory()
        person1 = PersonFactory()
        person2 = PersonFactory()
        
        asset.owners.add(person1, person2)
        
        assert asset.owners.count() == 2
        assert person1 in asset.owners.all()
        assert person2 in asset.owners.all()


@pytest.mark.django_db
class TestTimelineModel:
    
    def test_timeline_creation(self):
        timeline = TimelineFactory()
        assert timeline.title
        assert timeline.date
        assert str(timeline) == f"{timeline.title} ({timeline.date})"
    
    def test_timeline_ordering(self):
        timeline1 = TimelineFactory(date=date(2023, 1, 1))
        timeline2 = TimelineFactory(date=date(2024, 1, 1))
        
        timelines = Timeline.objects.all()
        assert timelines[0] == timeline2  # Most recent first
        assert timelines[1] == timeline1
    
    def test_timeline_with_relationships(self):
        timeline = TimelineFactory()
        person = PersonFactory()
        event = EventFactory()
        story = StoryFactory()
        
        timeline.people.add(person)
        timeline.events.add(event)
        timeline.stories.add(story)
        
        assert timeline.people.count() == 1
        assert timeline.events.count() == 1
        assert timeline.stories.count() == 1