from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Person(models.Model):
    """Family members and important individuals"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='people/', blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Location(models.Model):
    """Geographic information and places"""
    LOCATION_TYPES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('school', 'School'),
        ('hospital', 'Hospital'),
        ('travel', 'Travel'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPES, default='other')
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class Institution(models.Model):
    """External organizations"""
    INSTITUTION_TYPES = [
        ('hospital', 'Hospital'),
        ('school', 'School'),
        ('company', 'Company'),
        ('government', 'Government'),
        ('religious', 'Religious'),
        ('restaurant', 'Restaurant'),
        ('entertainment', 'Entertainment'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    institution_type = models.CharField(max_length=20, choices=INSTITUTION_TYPES)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    established_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class Event(models.Model):
    """Important milestones and activities"""
    EVENT_TYPES = [
        ('birthday', 'Birthday'),
        ('wedding', 'Wedding'),
        ('graduation', 'Graduation'),
        ('funeral', 'Funeral'),
        ('reunion', 'Family Reunion'),
        ('holiday', 'Holiday'),
        ('milestone', 'Milestone'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Many-to-many relationships
    participants = models.ManyToManyField(Person, related_name='events', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} ({self.start_date.year})"


class Story(models.Model):
    """Family memories, anecdotes, and experiences"""
    STORY_TYPES = [
        ('memory', 'Memory'),
        ('legend', 'Family Legend'),
        ('experience', 'Life Experience'),
        ('wisdom', 'Wisdom'),
        ('tradition', 'Tradition'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    story_type = models.CharField(max_length=20, choices=STORY_TYPES, default='memory')
    date_occurred = models.DateField(null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Many-to-many relationships
    people = models.ManyToManyField(Person, related_name='stories', blank=True)
    events = models.ManyToManyField(Event, related_name='stories', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Stories"
    
    def __str__(self):
        return self.title


class Multimedia(models.Model):
    """Photos, videos, documents, audio files"""
    MEDIA_TYPES = [
        ('photo', 'Photo'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    file = models.FileField(upload_to='media/')
    file_size = models.PositiveIntegerField(null=True, blank=True)
    created_date = models.DateTimeField(null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Many-to-many relationships
    people = models.ManyToManyField(Person, related_name='media', blank=True)
    events = models.ManyToManyField(Event, related_name='media', blank=True)
    stories = models.ManyToManyField(Story, related_name='media', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Multimedia"
    
    def __str__(self):
        return self.title


class Relationship(models.Model):
    """Network of relationships between people"""
    RELATIONSHIP_TYPES = [
        ('parent', 'Parent'),
        ('child', 'Child'),
        ('spouse', 'Spouse'),
        ('sibling', 'Sibling'),
        ('grandparent', 'Grandparent'),
        ('grandchild', 'Grandchild'),
        ('friend', 'Friend'),
        ('colleague', 'Colleague'),
        ('other', 'Other'),
    ]
    
    person_from = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='relationships_from')
    person_to = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='relationships_to')
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['person_from', 'person_to', 'relationship_type']
    
    def __str__(self):
        return f"{self.person_from} -> {self.person_to} ({self.relationship_type})"


class Health(models.Model):
    """Personal and family health records"""
    RECORD_TYPES = [
        ('checkup', 'Medical Checkup'),
        ('illness', 'Illness'),
        ('medication', 'Medication'),
        ('surgery', 'Surgery'),
        ('allergy', 'Allergy'),
        ('genetic', 'Genetic Condition'),
        ('other', 'Other'),
    ]
    
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='health_records')
    record_type = models.CharField(max_length=20, choices=RECORD_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    doctor = models.CharField(max_length=100, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True, blank=True)
    is_hereditary = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.person.name} - {self.title}"


class Heritage(models.Model):
    """Family values, traditions, and wisdom"""
    HERITAGE_TYPES = [
        ('values', 'Family Values'),
        ('tradition', 'Tradition'),
        ('wisdom', 'Wisdom'),
        ('skill', 'Skill'),
        ('recipe', 'Recipe'),
        ('other', 'Other'),
    ]
    
    IMPORTANCE_LEVELS = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Critical'),
    ]
    
    title = models.CharField(max_length=200)
    heritage_type = models.CharField(max_length=20, choices=HERITAGE_TYPES)
    description = models.TextField()
    origin_person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, related_name='heritage_originated')
    inheritors = models.ManyToManyField(Person, related_name='heritage_inherited', blank=True)
    importance = models.IntegerField(choices=IMPORTANCE_LEVELS, default=2)
    
    # Relationships
    stories = models.ManyToManyField(Story, related_name='heritage', blank=True)
    events = models.ManyToManyField(Event, related_name='heritage', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title


class Planning(models.Model):
    """Future goals and family vision"""
    TIME_RANGES = [
        ('short', 'Short-term (< 1 year)'),
        ('medium', 'Medium-term (1-5 years)'),
        ('long', 'Long-term (> 5 years)'),
    ]
    
    PRIORITY_LEVELS = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    time_range = models.CharField(max_length=10, choices=TIME_RANGES)
    priority = models.IntegerField(choices=PRIORITY_LEVELS, default=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    target_date = models.DateField(null=True, blank=True)
    expected_outcome = models.TextField(blank=True)
    
    # Relationships
    involved_people = models.ManyToManyField(Person, related_name='plans', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title


class Career(models.Model):
    """Work and education history"""
    CAREER_TYPES = [
        ('education', 'Education'),
        ('work', 'Work'),
        ('volunteer', 'Volunteer'),
        ('internship', 'Internship'),
        ('other', 'Other'),
    ]
    
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='career_history')
    career_type = models.CharField(max_length=20, choices=CAREER_TYPES)
    title = models.CharField(max_length=200)
    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    salary_range = models.CharField(max_length=50, blank=True)
    
    # Relationships
    events = models.ManyToManyField(Event, related_name='careers', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.person.name} - {self.title}"


class Assets(models.Model):
    """Important property and documents"""
    ASSET_TYPES = [
        ('property', 'Real Estate'),
        ('vehicle', 'Vehicle'),
        ('jewelry', 'Jewelry'),
        ('insurance', 'Insurance'),
        ('investment', 'Investment'),
        ('document', 'Important Document'),
        ('other', 'Other'),
    ]
    
    LEGAL_STATUS = [
        ('owned', 'Owned'),
        ('leased', 'Leased'),
        ('shared', 'Shared Ownership'),
        ('trust', 'In Trust'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    description = models.TextField(blank=True)
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    acquisition_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    legal_status = models.CharField(max_length=20, choices=LEGAL_STATUS, default='owned')
    importance = models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Critical')], default=2)
    
    # Relationships
    owners = models.ManyToManyField(Person, related_name='assets')
    related_documents = models.ManyToManyField(Multimedia, related_name='assets', blank=True)
    plans = models.ManyToManyField(Planning, related_name='assets', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Assets"
    
    def __str__(self):
        return self.name


class Timeline(models.Model):
    """Time-based organization of information"""
    TIMELINE_TYPES = [
        ('personal', 'Personal Milestone'),
        ('family', 'Family Event'),
        ('historical', 'Historical Context'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    timeline_type = models.CharField(max_length=20, choices=TIMELINE_TYPES)
    date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    importance = models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Critical')], default=2)
    historical_context = models.TextField(blank=True)
    
    # Relationships (generic foreign keys could be used here for more flexibility)
    people = models.ManyToManyField(Person, related_name='timeline_entries', blank=True)
    events = models.ManyToManyField(Event, related_name='timeline_entries', blank=True)
    stories = models.ManyToManyField(Story, related_name='timeline_entries', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.title} ({self.date})"