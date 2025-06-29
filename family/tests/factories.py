import factory
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory, LazyAttribute
from decimal import Decimal
from datetime import date, datetime

from family.models import (
    Person, Location, Institution, Event, Story, Multimedia,
    Relationship, Health, Heritage, Planning, Career, Assets, Timeline
)


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = Faker('user_name')
    email = Faker('email')
    first_name = Faker('first_name')
    last_name = Faker('last_name')


class PersonFactory(DjangoModelFactory):
    class Meta:
        model = Person
    
    name = Faker('name')
    birth_date = Faker('date_of_birth', minimum_age=0, maximum_age=100)
    gender = factory.Iterator(['M', 'F', 'O'])
    bio = Faker('text', max_nb_chars=500)
    email = Faker('email')
    phone = Faker('phone_number')


class LocationFactory(DjangoModelFactory):
    class Meta:
        model = Location
    
    name = Faker('city')
    address = Faker('address')
    latitude = Faker('latitude')
    longitude = Faker('longitude')
    location_type = factory.Iterator(['home', 'work', 'school', 'hospital', 'travel', 'other'])
    description = Faker('text', max_nb_chars=200)


class InstitutionFactory(DjangoModelFactory):
    class Meta:
        model = Institution
    
    name = Faker('company')
    institution_type = factory.Iterator(['hospital', 'school', 'company', 'government', 'religious', 'other'])
    website = Faker('url')
    phone = Faker('phone_number')
    email = Faker('email')
    address = Faker('address')
    established_date = Faker('date_between', start_date='-50y', end_date='today')
    description = Faker('text', max_nb_chars=300)


class EventFactory(DjangoModelFactory):
    class Meta:
        model = Event
    
    name = Faker('sentence', nb_words=4)
    description = Faker('text', max_nb_chars=500)
    event_type = factory.Iterator(['birthday', 'wedding', 'graduation', 'funeral', 'reunion', 'holiday', 'milestone', 'other'])
    start_date = Faker('date_time_between', start_date='-10y', end_date='+1y')
    location = SubFactory(LocationFactory)
    institution = SubFactory(InstitutionFactory)


class StoryFactory(DjangoModelFactory):
    class Meta:
        model = Story
    
    title = Faker('sentence', nb_words=6)
    content = Faker('text', max_nb_chars=1000)
    story_type = factory.Iterator(['memory', 'legend', 'experience', 'wisdom', 'tradition', 'other'])
    date_occurred = Faker('date_between', start_date='-30y', end_date='today')
    location = SubFactory(LocationFactory)


class MultimediaFactory(DjangoModelFactory):
    class Meta:
        model = Multimedia
    
    title = Faker('sentence', nb_words=4)
    description = Faker('text', max_nb_chars=300)
    media_type = factory.Iterator(['photo', 'video', 'audio', 'document', 'other'])
    file = factory.django.FileField(filename='test_file.jpg')
    file_size = Faker('random_int', min=1024, max=10485760)  # 1KB to 10MB
    created_date = Faker('date_time_between', start_date='-5y', end_date='today')
    location = SubFactory(LocationFactory)


class RelationshipFactory(DjangoModelFactory):
    class Meta:
        model = Relationship
    
    person_from = SubFactory(PersonFactory)
    person_to = SubFactory(PersonFactory)
    relationship_type = factory.Iterator(['parent', 'child', 'spouse', 'sibling', 'grandparent', 'grandchild', 'friend', 'colleague', 'other'])
    start_date = Faker('date_between', start_date='-30y', end_date='today')
    description = Faker('text', max_nb_chars=200)


class HealthFactory(DjangoModelFactory):
    class Meta:
        model = Health
    
    person = SubFactory(PersonFactory)
    record_type = factory.Iterator(['checkup', 'illness', 'medication', 'surgery', 'allergy', 'genetic', 'other'])
    title = Faker('sentence', nb_words=4)
    description = Faker('text', max_nb_chars=500)
    date = Faker('date_between', start_date='-10y', end_date='today')
    doctor = Faker('name')
    institution = SubFactory(InstitutionFactory)
    is_hereditary = Faker('boolean', chance_of_getting_true=20)


class HeritageFactory(DjangoModelFactory):
    class Meta:
        model = Heritage
    
    title = Faker('sentence', nb_words=4)
    heritage_type = factory.Iterator(['values', 'tradition', 'wisdom', 'skill', 'recipe', 'other'])
    description = Faker('text', max_nb_chars=500)
    origin_person = SubFactory(PersonFactory)
    importance = factory.Iterator([1, 2, 3, 4])


class PlanningFactory(DjangoModelFactory):
    class Meta:
        model = Planning
    
    title = Faker('sentence', nb_words=5)
    description = Faker('text', max_nb_chars=500)
    time_range = factory.Iterator(['short', 'medium', 'long'])
    priority = factory.Iterator([1, 2, 3, 4])
    status = factory.Iterator(['planned', 'in_progress', 'completed', 'cancelled'])
    target_date = Faker('date_between', start_date='today', end_date='+5y')
    expected_outcome = Faker('text', max_nb_chars=300)


class CareerFactory(DjangoModelFactory):
    class Meta:
        model = Career
    
    person = SubFactory(PersonFactory)
    career_type = factory.Iterator(['education', 'work', 'volunteer', 'internship', 'other'])
    title = Faker('job')
    institution = SubFactory(InstitutionFactory)
    start_date = Faker('date_between', start_date='-20y', end_date='-1y')
    end_date = Faker('date_between', start_date='-1y', end_date='today')
    description = Faker('text', max_nb_chars=400)
    achievements = Faker('text', max_nb_chars=300)
    salary_range = Faker('random_element', elements=['20-30K', '30-50K', '50-80K', '80K+'])


class AssetsFactory(DjangoModelFactory):
    class Meta:
        model = Assets
    
    name = Faker('sentence', nb_words=3)
    asset_type = factory.Iterator(['property', 'vehicle', 'jewelry', 'insurance', 'investment', 'document', 'other'])
    description = Faker('text', max_nb_chars=300)
    estimated_value = Faker('pydecimal', left_digits=8, right_digits=2, positive=True)
    acquisition_date = Faker('date_between', start_date='-20y', end_date='today')
    location = Faker('address')
    legal_status = factory.Iterator(['owned', 'leased', 'shared', 'trust', 'other'])
    importance = factory.Iterator([1, 2, 3, 4])


class TimelineFactory(DjangoModelFactory):
    class Meta:
        model = Timeline
    
    title = Faker('sentence', nb_words=5)
    description = Faker('text', max_nb_chars=400)
    timeline_type = factory.Iterator(['personal', 'family', 'historical', 'other'])
    date = Faker('date_between', start_date='-50y', end_date='today')
    importance = factory.Iterator([1, 2, 3, 4])
    historical_context = Faker('text', max_nb_chars=300)