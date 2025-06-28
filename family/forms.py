"""
Custom forms for Family Knowledge Management System
Enhanced forms with family-friendly widgets and validation
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from .models import (
    Person, Story, Event, Multimedia, Relationship, 
    Location, Institution, Health, Heritage, Planning
)
from .widgets import (
    FamilyAutoCompleteWidget, LocationAutoCompleteWidget, 
    InstitutionAutoCompleteWidget, FamilyDateWidget,
    FamilyPhotoWidget, RelationshipSelectorWidget,
    RichTextWidget, TagsWidget
)


class PersonAdminForm(forms.ModelForm):
    """
    Enhanced form for Person model with family-friendly widgets
    """
    
    class Meta:
        model = Person
        fields = '__all__'
        widgets = {
            'birth_date': FamilyDateWidget(),
            'death_date': FamilyDateWidget(),
            'photo': FamilyPhotoWidget(),
            'birth_place': LocationAutoCompleteWidget(),
            'current_location': LocationAutoCompleteWidget(),
            'description': RichTextWidget(attrs={'rows': 4}),
            'tags': TagsWidget(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add helpful placeholders and labels
        self.fields['name'].widget.attrs.update({
            'placeholder': '请输入姓名',
            'class': 'form-control'
        })
        
        self.fields['nickname'].widget.attrs.update({
            'placeholder': '昵称或小名'
        })
        
        self.fields['gender'].widget.attrs.update({
            'class': 'form-control'
        })
        
        # Add age calculation help text
        if self.instance and self.instance.birth_date:
            age = self.calculate_age(self.instance.birth_date)
            self.fields['birth_date'].help_text = f'当前年龄: {age}岁'
    
    def calculate_age(self, birth_date):
        """Calculate age from birth date"""
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date > date.today():
            raise ValidationError('出生日期不能是未来的日期')
        return birth_date
    
    def clean_death_date(self):
        death_date = self.cleaned_data.get('death_date')
        birth_date = self.cleaned_data.get('birth_date')
        
        if death_date:
            if death_date > date.today():
                raise ValidationError('逝世日期不能是未来的日期')
            if birth_date and death_date < birth_date:
                raise ValidationError('逝世日期不能早于出生日期')
        
        return death_date


class StoryAdminForm(forms.ModelForm):
    """
    Enhanced form for Story model with rich text editing
    """
    
    class Meta:
        model = Story
        fields = '__all__'
        widgets = {
            'content': RichTextWidget(attrs={'rows': 8}),
            'date': FamilyDateWidget(),
            'location': LocationAutoCompleteWidget(),
            'tags': TagsWidget(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['title'].widget.attrs.update({
            'placeholder': '给这个故事起个温暖的标题...',
            'class': 'form-control'
        })
        
        self.fields['content'].widget.attrs.update({
            'placeholder': '在这里记录您的家族故事...\n\n例如：\n• 那个难忘的春节聚会\n• 爷爷教我下棋的午后\n• 全家一起包饺子的温馨时光'
        })
        
        # Set default date to today
        if not self.instance.pk:
            self.fields['date'].initial = date.today()


class EventAdminForm(forms.ModelForm):
    """
    Enhanced form for Event model with smart date handling
    """
    
    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'date': FamilyDateWidget(),
            'location': LocationAutoCompleteWidget(),
            'description': RichTextWidget(attrs={'rows': 4}),
            'tags': TagsWidget(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['title'].widget.attrs.update({
            'placeholder': '活动名称，如：小明生日聚会',
            'class': 'form-control'
        })
        
        self.fields['event_type'].widget.attrs.update({
            'class': 'form-control'
        })
        
        # Add future date validation help
        self.fields['date'].help_text = '可以是过去、今天或未来的日期'
    
    def clean_date(self):
        event_date = self.cleaned_data.get('date')
        if event_date:
            # Allow past, present and future dates for events
            # But warn for very old dates
            if event_date < date.today() - timedelta(days=365*10):
                # This is just a warning, not an error
                pass
        return event_date


class MultimediaAdminForm(forms.ModelForm):
    """
    Enhanced form for Multimedia model with photo preview
    """
    
    class Meta:
        model = Multimedia
        fields = '__all__'
        widgets = {
            'file': FamilyPhotoWidget(),
            'uploaded_at': FamilyDateWidget(),
            'location': LocationAutoCompleteWidget(),
            'description': RichTextWidget(attrs={'rows': 3}),
            'tags': TagsWidget(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['title'].widget.attrs.update({
            'placeholder': '照片或视频的标题...'
        })
        
        self.fields['description'].widget.attrs.update({
            'placeholder': '描述这张照片的故事...'
        })
        
        # Set default upload date to today
        if not self.instance.pk:
            self.fields['uploaded_at'].initial = date.today()
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError('文件大小不能超过10MB')
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'video/mp4', 'video/mov']
            if hasattr(file, 'content_type') and file.content_type not in allowed_types:
                raise ValidationError('只支持 JPG, PNG, GIF 图片和 MP4, MOV 视频格式')
        
        return file


class RelationshipAdminForm(forms.ModelForm):
    """
    Enhanced form for Relationship model with visual selector
    """
    
    class Meta:
        model = Relationship
        fields = '__all__'
        widgets = {
            'relationship_type': RelationshipSelectorWidget(),
            'start_date': FamilyDateWidget(),
            'end_date': FamilyDateWidget(),
            'description': RichTextWidget(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text for relationship fields
        self.fields['person1'].help_text = '选择关系中的第一个人'
        self.fields['person2'].help_text = '选择关系中的第二个人'
        self.fields['relationship_type'].help_text = '选择他们之间的关系类型'
    
    def clean(self):
        cleaned_data = super().clean()
        person1 = cleaned_data.get('person1')
        person2 = cleaned_data.get('person2')
        
        if person1 and person2 and person1 == person2:
            raise ValidationError('不能建立一个人与自己的关系')
        
        # Check for duplicate relationships
        if person1 and person2:
            existing = Relationship.objects.filter(
                person1=person1, person2=person2
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise ValidationError('这两个人之间已经存在关系记录')
        
        return cleaned_data


class HealthAdminForm(forms.ModelForm):
    """
    Enhanced form for Health model with privacy considerations
    """
    
    class Meta:
        model = Health
        fields = '__all__'
        widgets = {
            'record_date': FamilyDateWidget(),
            'institution': InstitutionAutoCompleteWidget(institution_type='hospital'),
            'notes': RichTextWidget(attrs={'rows': 4}),
            'tags': TagsWidget(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add privacy notice
        self.fields['notes'].help_text = '健康信息将被安全保护，仅限家庭成员查看'
        
        # Set default date to today
        if not self.instance.pk:
            self.fields['record_date'].initial = date.today()


class LocationAdminForm(forms.ModelForm):
    """
    Enhanced form for Location model
    """
    
    class Meta:
        model = Location
        fields = '__all__'
        widgets = {
            'description': RichTextWidget(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['name'].widget.attrs.update({
            'placeholder': '地点名称，如：北京市朝阳区'
        })
        
        self.fields['address'].widget.attrs.update({
            'placeholder': '详细地址（可选）'
        })


class InstitutionAdminForm(forms.ModelForm):
    """
    Enhanced form for Institution model
    """
    
    class Meta:
        model = Institution
        fields = '__all__'
        widgets = {
            'location': LocationAutoCompleteWidget(),
            'description': RichTextWidget(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['name'].widget.attrs.update({
            'placeholder': '机构名称，如：北京协和医院'
        })
        
        self.fields['institution_type'].widget.attrs.update({
            'class': 'form-control'
        })


# Helper functions for form validation

def validate_family_photo(image):
    """Validate uploaded family photos"""
    # Check file size
    if image.size > 5 * 1024 * 1024:  # 5MB
        raise ValidationError('照片文件大小不能超过5MB')
    
    # Check image dimensions
    from PIL import Image
    img = Image.open(image)
    if img.width < 100 or img.height < 100:
        raise ValidationError('照片尺寸太小，请上传至少100x100像素的图片')
    
    if img.width > 4000 or img.height > 4000:
        raise ValidationError('照片尺寸太大，请上传小于4000x4000像素的图片')


def validate_chinese_name(name):
    """Validate Chinese names"""
    import re
    if not re.match(r'^[\u4e00-\u9fff\w\s]+$', name):
        raise ValidationError('姓名只能包含中文、英文、数字和空格')
    
    if len(name.strip()) < 2:
        raise ValidationError('姓名至少需要2个字符')
    
    if len(name.strip()) > 20:
        raise ValidationError('姓名不能超过20个字符')


# Form field choices with Chinese labels
GENDER_CHOICES = [
    ('', '请选择性别'),
    ('male', '男性'),
    ('female', '女性'),
    ('other', '其他'),
]

EVENT_TYPE_CHOICES = [
    ('', '请选择事件类型'),
    ('birthday', '🎂 生日'),
    ('anniversary', '💒 纪念日'),
    ('graduation', '🎓 毕业'),
    ('wedding', '💍 婚礼'),
    ('travel', '✈️ 旅行'),
    ('festival', '🎊 节日'),
    ('achievement', '🏆 成就'),
    ('family_gathering', '👨‍👩‍👧‍👦 家庭聚会'),
    ('other', '📝 其他'),
]

RELATIONSHIP_TYPE_CHOICES = [
    ('', '请选择关系类型'),
    ('parent', '父母'),
    ('child', '子女'),
    ('sibling', '兄弟姐妹'),
    ('spouse', '配偶'),
    ('grandparent', '祖父母/外祖父母'),
    ('grandchild', '孙子女/外孙子女'),
    ('uncle_aunt', '叔伯/姑姨'),
    ('cousin', '堂兄弟姐妹/表兄弟姐妹'),
    ('friend', '朋友'),
    ('colleague', '同事'),
    ('neighbor', '邻居'),
    ('other', '其他'),
]