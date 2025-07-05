"""
Comprehensive tests for family forms targeting 90%+ branch coverage
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
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from django import forms
from io import BytesIO

from family.forms import (
    PersonAdminForm, StoryAdminForm, EventAdminForm, MultimediaAdminForm,
    RelationshipAdminForm, HealthAdminForm, LocationAdminForm, InstitutionAdminForm,
    validate_family_photo, validate_chinese_name,
    GENDER_CHOICES, EVENT_TYPE_CHOICES, RELATIONSHIP_TYPE_CHOICES
)


class TestPersonAdminForm(unittest.TestCase):
    """Tests for PersonAdminForm"""
    
    def setUp(self):
        self.form_data = {
            'name': 'Test Person',
            'gender': 'male',
            'birth_date': date(1990, 1, 1),
        }
    
    def test_init_without_instance(self):
        """Test form initialization without instance"""
        form = PersonAdminForm(data=self.form_data)
        
        # Check widget attributes are set
        self.assertIn('placeholder', form.fields['name'].widget.attrs)
        self.assertIn('class', form.fields['gender'].widget.attrs)
        self.assertIn('placeholder', form.fields['bio'].widget.attrs)
        
    def test_init_with_instance_with_birthdate(self):
        """Test form initialization with instance that has birth_date"""
        mock_instance = Mock()
        mock_instance.pk = 1
        mock_instance.birth_date = date(1990, 1, 1)
        
        form = PersonAdminForm(instance=mock_instance)
        
        # Check age calculation help text is set
        expected_age = date.today().year - 1990 - ((date.today().month, date.today().day) < (1, 1))
        self.assertEqual(form.fields['birth_date'].help_text, f'当前年龄: {expected_age}岁')
    
    def test_calculate_age(self):
        """Test age calculation method"""
        form = PersonAdminForm()
        
        # Test age calculation for someone born on Jan 1, 1990
        birth_date = date(1990, 1, 1)
        age = form.calculate_age(birth_date)
        expected_age = date.today().year - 1990 - ((date.today().month, date.today().day) < (1, 1))
        self.assertEqual(age, expected_age)
        
        # Test age calculation for recent birth
        recent_birth = date.today() - timedelta(days=365)
        age = form.calculate_age(recent_birth)
        self.assertIn(age, [0, 1])  # Could be 0 or 1 depending on exact dates
    
    def test_clean_birth_date_valid(self):
        """Test clean_birth_date with valid date"""
        form = PersonAdminForm(data=self.form_data)
        form.is_valid()  # Trigger cleaning
        
        self.assertEqual(form.cleaned_data['birth_date'], date(1990, 1, 1))
    
    def test_clean_birth_date_future(self):
        """Test clean_birth_date with future date"""
        self.form_data['birth_date'] = date.today() + timedelta(days=1)
        form = PersonAdminForm(data=self.form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('birth_date', form.errors)
        self.assertEqual(form.errors['birth_date'][0], '出生日期不能是未来的日期')
    
    def test_clean_death_date_valid(self):
        """Test clean_death_date with valid date"""
        self.form_data['death_date'] = date(2020, 1, 1)
        form = PersonAdminForm(data=self.form_data)
        form.is_valid()  # Trigger cleaning
        
        self.assertEqual(form.cleaned_data['death_date'], date(2020, 1, 1))
    
    def test_clean_death_date_future(self):
        """Test clean_death_date with future date"""
        self.form_data['death_date'] = date.today() + timedelta(days=1)
        form = PersonAdminForm(data=self.form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('death_date', form.errors)
        self.assertEqual(form.errors['death_date'][0], '逝世日期不能是未来的日期')
    
    def test_clean_death_date_before_birth(self):
        """Test clean_death_date with date before birth"""
        self.form_data['birth_date'] = date(1990, 1, 1)
        self.form_data['death_date'] = date(1989, 1, 1)
        form = PersonAdminForm(data=self.form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('death_date', form.errors)
        self.assertEqual(form.errors['death_date'][0], '逝世日期不能早于出生日期')
    
    def test_clean_death_date_no_birth_date(self):
        """Test clean_death_date when birth_date is missing"""
        del self.form_data['birth_date']
        self.form_data['death_date'] = date(2020, 1, 1)
        form = PersonAdminForm(data=self.form_data)
        
        # Should not raise error when birth_date is missing
        form.is_valid()
        if 'death_date' in form.cleaned_data:
            self.assertEqual(form.cleaned_data['death_date'], date(2020, 1, 1))


class TestStoryAdminForm(unittest.TestCase):
    """Tests for StoryAdminForm"""
    
    def test_init_without_instance(self):
        """Test form initialization without instance"""
        form = StoryAdminForm()
        
        # Check widget attributes
        self.assertIn('placeholder', form.fields['title'].widget.attrs)
        self.assertIn('placeholder', form.fields['content'].widget.attrs)
        
        # Check default date is today
        self.assertEqual(form.fields['date_occurred'].initial, date.today())
    
    def test_init_with_instance(self):
        """Test form initialization with existing instance"""
        mock_instance = Mock()
        mock_instance.pk = 1
        
        form = StoryAdminForm(instance=mock_instance)
        
        # Should not set default date for existing instance
        self.assertNotEqual(form.fields['date_occurred'].initial, date.today())


class TestEventAdminForm(unittest.TestCase):
    """Tests for EventAdminForm"""
    
    def test_init(self):
        """Test form initialization"""
        form = EventAdminForm()
        
        # Check widget attributes
        self.assertIn('placeholder', form.fields['name'].widget.attrs)
        self.assertIn('class', form.fields['event_type'].widget.attrs)
        self.assertEqual(form.fields['start_date'].help_text, '可以是过去、今天或未来的日期')
    
    def test_clean_start_date_valid(self):
        """Test clean_start_date with valid date"""
        form_data = {
            'name': 'Test Event',
            'event_type': 'birthday',
            'start_date': date.today(),
        }
        form = EventAdminForm(data=form_data)
        form.is_valid()
        
        self.assertEqual(form.cleaned_data['start_date'], date.today())
    
    def test_clean_start_date_very_old(self):
        """Test clean_start_date with very old date"""
        form_data = {
            'name': 'Test Event',
            'event_type': 'birthday',
            'start_date': date.today() - timedelta(days=365*11),  # 11 years ago
        }
        form = EventAdminForm(data=form_data)
        form.is_valid()
        
        # Should still be valid (just a warning, not an error)
        self.assertEqual(form.cleaned_data['start_date'], form_data['start_date'])
    
    def test_clean_start_date_none(self):
        """Test clean_start_date with None value"""
        form_data = {
            'name': 'Test Event',
            'event_type': 'birthday',
        }
        form = EventAdminForm(data=form_data)
        form.is_valid()
        
        # Should handle None gracefully
        self.assertIsNone(form.cleaned_data.get('start_date'))


class TestMultimediaAdminForm(unittest.TestCase):
    """Tests for MultimediaAdminForm"""
    
    def test_init_without_instance(self):
        """Test form initialization without instance"""
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = timezone.now()
            form = MultimediaAdminForm()
            
            # Check widget attributes
            self.assertIn('placeholder', form.fields['title'].widget.attrs)
            self.assertIn('placeholder', form.fields['description'].widget.attrs)
            
            # Check default date is set
            self.assertEqual(form.fields['created_date'].initial, mock_now.return_value)
    
    def test_init_with_instance(self):
        """Test form initialization with existing instance"""
        mock_instance = Mock()
        mock_instance.pk = 1
        
        form = MultimediaAdminForm(instance=mock_instance)
        
        # Should not set default date for existing instance
        self.assertNotEqual(form.fields['created_date'].initial, timezone.now())
    
    def test_clean_file_valid(self):
        """Test clean_file with valid file"""
        mock_file = Mock()
        mock_file.size = 5 * 1024 * 1024  # 5MB
        mock_file.content_type = 'image/jpeg'
        
        form_data = {'title': 'Test Photo'}
        form = MultimediaAdminForm(data=form_data)
        form.cleaned_data = {'file': mock_file}
        
        result = form.clean_file()
        self.assertEqual(result, mock_file)
    
    def test_clean_file_too_large(self):
        """Test clean_file with file too large"""
        mock_file = Mock()
        mock_file.size = 11 * 1024 * 1024  # 11MB
        
        form = MultimediaAdminForm()
        form.cleaned_data = {'file': mock_file}
        
        with self.assertRaises(ValidationError) as cm:
            form.clean_file()
        self.assertEqual(str(cm.exception.messages[0]), '文件大小不能超过10MB')
    
    def test_clean_file_invalid_type(self):
        """Test clean_file with invalid file type"""
        mock_file = Mock()
        mock_file.size = 1 * 1024 * 1024  # 1MB
        mock_file.content_type = 'application/pdf'
        
        form = MultimediaAdminForm()
        form.cleaned_data = {'file': mock_file}
        
        with self.assertRaises(ValidationError) as cm:
            form.clean_file()
        self.assertEqual(str(cm.exception.messages[0]), '只支持 JPG, PNG, GIF 图片和 MP4, MOV 视频格式')
    
    def test_clean_file_no_content_type(self):
        """Test clean_file when file has no content_type attribute"""
        mock_file = Mock(spec=['size'])  # No content_type attribute
        mock_file.size = 1 * 1024 * 1024  # 1MB
        
        form = MultimediaAdminForm()
        form.cleaned_data = {'file': mock_file}
        
        # Should not raise error when content_type is missing
        result = form.clean_file()
        self.assertEqual(result, mock_file)
    
    def test_clean_file_none(self):
        """Test clean_file with None value"""
        form = MultimediaAdminForm()
        form.cleaned_data = {'file': None}
        
        result = form.clean_file()
        self.assertIsNone(result)


class TestRelationshipAdminForm(unittest.TestCase):
    """Tests for RelationshipAdminForm"""
    
    def test_init(self):
        """Test form initialization"""
        form = RelationshipAdminForm()
        
        # Check help texts are set
        self.assertEqual(form.fields['person_from'].help_text, '选择关系中的第一个人')
        self.assertEqual(form.fields['person_to'].help_text, '选择关系中的第二个人')
        self.assertEqual(form.fields['relationship_type'].help_text, '选择他们之间的关系类型')
    
    def test_clean_same_person(self):
        """Test clean when person_from and person_to are the same"""
        mock_person = Mock()
        mock_person.id = 1
        
        form_data = {
            'person_from': mock_person,
            'person_to': mock_person,
            'relationship_type': 'parent',
        }
        form = RelationshipAdminForm(data=form_data)
        form.cleaned_data = form_data
        
        with self.assertRaises(ValidationError) as cm:
            form.clean()
        self.assertEqual(str(cm.exception.messages[0]), '不能建立一个人与自己的关系')
    
    def test_clean_duplicate_relationship_new(self):
        """Test clean when duplicate relationship exists (new form)"""
        mock_person1 = Mock()
        mock_person1.id = 1
        mock_person2 = Mock()
        mock_person2.id = 2
        
        # Mock the model's objects.filter
        mock_queryset = Mock()
        mock_queryset.exists.return_value = True
        
        with patch('family.forms.Relationship') as mock_relationship:
            mock_relationship.objects.filter.return_value.exclude.return_value = mock_queryset
            
            form_data = {
                'person_from': mock_person1,
                'person_to': mock_person2,
                'relationship_type': 'parent',
            }
            form = RelationshipAdminForm(data=form_data)
            form.cleaned_data = form_data
            
            with self.assertRaises(ValidationError) as cm:
                form.clean()
            self.assertEqual(str(cm.exception.messages[0]), '这两个人之间已经存在关系记录')
    
    def test_clean_duplicate_relationship_edit(self):
        """Test clean when editing existing relationship"""
        mock_person1 = Mock()
        mock_person1.id = 1
        mock_person2 = Mock()
        mock_person2.id = 2
        
        mock_instance = Mock()
        mock_instance.pk = 10
        
        # Mock the model's objects.filter - should exclude current instance
        mock_queryset = Mock()
        mock_queryset.exists.return_value = False  # No duplicates when excluding self
        
        with patch('family.forms.Relationship') as mock_relationship:
            mock_relationship.objects.filter.return_value.exclude.return_value = mock_queryset
            
            form_data = {
                'person_from': mock_person1,
                'person_to': mock_person2,
                'relationship_type': 'parent',
            }
            form = RelationshipAdminForm(data=form_data, instance=mock_instance)
            form.cleaned_data = form_data
            
            # Should not raise error
            result = form.clean()
            self.assertEqual(result, form_data)
    
    def test_clean_valid(self):
        """Test clean with valid data"""
        mock_person1 = Mock()
        mock_person1.id = 1
        mock_person2 = Mock()
        mock_person2.id = 2
        
        # Mock no existing relationships
        mock_queryset = Mock()
        mock_queryset.exists.return_value = False
        
        with patch('family.forms.Relationship') as mock_relationship:
            mock_relationship.objects.filter.return_value.exclude.return_value = mock_queryset
            
            form_data = {
                'person_from': mock_person1,
                'person_to': mock_person2,
                'relationship_type': 'parent',
            }
            form = RelationshipAdminForm(data=form_data)
            form.cleaned_data = form_data
            
            result = form.clean()
            self.assertEqual(result, form_data)
    
    def test_clean_missing_persons(self):
        """Test clean when person fields are missing"""
        form_data = {
            'relationship_type': 'parent',
        }
        form = RelationshipAdminForm(data=form_data)
        form.cleaned_data = form_data
        
        # Should not raise error when persons are missing
        result = form.clean()
        self.assertEqual(result, form_data)


class TestHealthAdminForm(unittest.TestCase):
    """Tests for HealthAdminForm"""
    
    def test_init_without_instance(self):
        """Test form initialization without instance"""
        form = HealthAdminForm()
        
        # Check help text is set
        self.assertEqual(form.fields['description'].help_text, '健康信息将被安全保护，仅限家庭成员查看')
        
        # Check default date is today
        self.assertEqual(form.fields['date'].initial, date.today())
    
    def test_init_with_instance(self):
        """Test form initialization with existing instance"""
        mock_instance = Mock()
        mock_instance.pk = 1
        
        form = HealthAdminForm(instance=mock_instance)
        
        # Should not set default date for existing instance
        self.assertNotEqual(form.fields['date'].initial, date.today())


class TestLocationAdminForm(unittest.TestCase):
    """Tests for LocationAdminForm"""
    
    def test_init(self):
        """Test form initialization"""
        form = LocationAdminForm()
        
        # Check widget attributes
        self.assertIn('placeholder', form.fields['name'].widget.attrs)
        self.assertEqual(form.fields['name'].widget.attrs['placeholder'], '地点名称，如：北京市朝阳区')
        self.assertIn('placeholder', form.fields['address'].widget.attrs)
        self.assertEqual(form.fields['address'].widget.attrs['placeholder'], '详细地址（可选）')


class TestInstitutionAdminForm(unittest.TestCase):
    """Tests for InstitutionAdminForm"""
    
    def test_init(self):
        """Test form initialization"""
        form = InstitutionAdminForm()
        
        # Check widget attributes
        self.assertIn('placeholder', form.fields['name'].widget.attrs)
        self.assertEqual(form.fields['name'].widget.attrs['placeholder'], '机构名称，如：北京协和医院')
        self.assertIn('class', form.fields['institution_type'].widget.attrs)
        self.assertEqual(form.fields['institution_type'].widget.attrs['class'], 'form-control')


class TestValidationFunctions(unittest.TestCase):
    """Tests for validation helper functions"""
    
    def test_validate_family_photo_valid(self):
        """Test validate_family_photo with valid image"""
        mock_image = Mock()
        mock_image.size = 2 * 1024 * 1024  # 2MB
        
        # Mock PIL.Image
        with patch('family.forms.Image') as mock_pil:
            mock_img = Mock()
            mock_img.width = 500
            mock_img.height = 500
            mock_pil.open.return_value = mock_img
            
            # Should not raise error
            try:
                validate_family_photo(mock_image)
            except ValidationError:
                self.fail("validate_family_photo raised ValidationError unexpectedly")
    
    def test_validate_family_photo_too_large(self):
        """Test validate_family_photo with file too large"""
        mock_image = Mock()
        mock_image.size = 6 * 1024 * 1024  # 6MB
        
        with self.assertRaises(ValidationError) as cm:
            validate_family_photo(mock_image)
        self.assertEqual(str(cm.exception.messages[0]), '照片文件大小不能超过5MB')
    
    def test_validate_family_photo_too_small_dimensions(self):
        """Test validate_family_photo with dimensions too small"""
        mock_image = Mock()
        mock_image.size = 1 * 1024 * 1024  # 1MB
        
        with patch('family.forms.Image') as mock_pil:
            mock_img = Mock()
            mock_img.width = 50  # Too small
            mock_img.height = 50
            mock_pil.open.return_value = mock_img
            
            with self.assertRaises(ValidationError) as cm:
                validate_family_photo(mock_image)
            self.assertEqual(str(cm.exception.messages[0]), '照片尺寸太小，请上传至少100x100像素的图片')
    
    def test_validate_family_photo_too_large_dimensions(self):
        """Test validate_family_photo with dimensions too large"""
        mock_image = Mock()
        mock_image.size = 1 * 1024 * 1024  # 1MB
        
        with patch('family.forms.Image') as mock_pil:
            mock_img = Mock()
            mock_img.width = 5000  # Too large
            mock_img.height = 5000
            mock_pil.open.return_value = mock_img
            
            with self.assertRaises(ValidationError) as cm:
                validate_family_photo(mock_image)
            self.assertEqual(str(cm.exception.messages[0]), '照片尺寸太大，请上传小于4000x4000像素的图片')
    
    def test_validate_chinese_name_valid(self):
        """Test validate_chinese_name with valid names"""
        # Chinese name
        try:
            validate_chinese_name('张三')
        except ValidationError:
            self.fail("validate_chinese_name raised ValidationError unexpectedly")
        
        # English name
        try:
            validate_chinese_name('John Smith')
        except ValidationError:
            self.fail("validate_chinese_name raised ValidationError unexpectedly")
        
        # Mixed name
        try:
            validate_chinese_name('张John123')
        except ValidationError:
            self.fail("validate_chinese_name raised ValidationError unexpectedly")
    
    def test_validate_chinese_name_invalid_characters(self):
        """Test validate_chinese_name with invalid characters"""
        with self.assertRaises(ValidationError) as cm:
            validate_chinese_name('张@三')
        self.assertEqual(str(cm.exception.messages[0]), '姓名只能包含中文、英文、数字和空格')
    
    def test_validate_chinese_name_too_short(self):
        """Test validate_chinese_name with name too short"""
        with self.assertRaises(ValidationError) as cm:
            validate_chinese_name('A')
        self.assertEqual(str(cm.exception.messages[0]), '姓名至少需要2个字符')
        
        # Test with whitespace
        with self.assertRaises(ValidationError) as cm:
            validate_chinese_name('  ')
        self.assertEqual(str(cm.exception.messages[0]), '姓名至少需要2个字符')
    
    def test_validate_chinese_name_too_long(self):
        """Test validate_chinese_name with name too long"""
        with self.assertRaises(ValidationError) as cm:
            validate_chinese_name('A' * 21)
        self.assertEqual(str(cm.exception.messages[0]), '姓名不能超过20个字符')


class TestFormChoices(unittest.TestCase):
    """Tests for form field choices"""
    
    def test_gender_choices(self):
        """Test GENDER_CHOICES structure"""
        self.assertEqual(len(GENDER_CHOICES), 4)
        self.assertEqual(GENDER_CHOICES[0], ('', '请选择性别'))
        self.assertEqual(GENDER_CHOICES[1], ('male', '男性'))
        self.assertEqual(GENDER_CHOICES[2], ('female', '女性'))
        self.assertEqual(GENDER_CHOICES[3], ('other', '其他'))
    
    def test_event_type_choices(self):
        """Test EVENT_TYPE_CHOICES structure"""
        self.assertGreater(len(EVENT_TYPE_CHOICES), 5)
        self.assertEqual(EVENT_TYPE_CHOICES[0], ('', '请选择事件类型'))
        
        # Check some key event types
        event_dict = dict(EVENT_TYPE_CHOICES)
        self.assertIn('birthday', event_dict)
        self.assertIn('wedding', event_dict)
        self.assertIn('graduation', event_dict)
    
    def test_relationship_type_choices(self):
        """Test RELATIONSHIP_TYPE_CHOICES structure"""
        self.assertGreater(len(RELATIONSHIP_TYPE_CHOICES), 5)
        self.assertEqual(RELATIONSHIP_TYPE_CHOICES[0], ('', '请选择关系类型'))
        
        # Check some key relationship types
        rel_dict = dict(RELATIONSHIP_TYPE_CHOICES)
        self.assertIn('parent', rel_dict)
        self.assertIn('child', rel_dict)
        self.assertIn('spouse', rel_dict)


if __name__ == '__main__':
    unittest.main()