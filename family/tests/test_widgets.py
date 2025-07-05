"""
Comprehensive tests for family widgets targeting 90%+ branch coverage
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
from django.utils.safestring import SafeString

from family.widgets import (
    FamilyAutoCompleteWidget, LocationAutoCompleteWidget, 
    InstitutionAutoCompleteWidget, FamilyDateWidget,
    FamilyPhotoWidget, RelationshipSelectorWidget,
    RichTextWidget, TagsWidget
)


class TestFamilyAutoCompleteWidget(unittest.TestCase):
    """Tests for FamilyAutoCompleteWidget"""
    
    def test_init_default_attrs(self):
        """Test widget initialization with default attributes"""
        widget = FamilyAutoCompleteWidget()
        
        self.assertEqual(widget.attrs['class'], 'family-autocomplete')
        self.assertEqual(widget.attrs['autocomplete'], 'off')
        self.assertEqual(widget.attrs['placeholder'], '开始输入姓名...')
        self.assertIsNone(widget.model)
    
    def test_init_with_model_and_attrs(self):
        """Test widget initialization with model and custom attributes"""
        custom_attrs = {'class': 'custom-class', 'data-test': 'value'}
        widget = FamilyAutoCompleteWidget(model='Person', attrs=custom_attrs)
        
        self.assertEqual(widget.model, 'Person')
        self.assertEqual(widget.attrs['class'], 'custom-class')
        self.assertEqual(widget.attrs['data-test'], 'value')
        self.assertEqual(widget.attrs['autocomplete'], 'off')
    
    def test_format_value_string(self):
        """Test format_value with string input"""
        widget = FamilyAutoCompleteWidget()
        result = widget.format_value('John Doe')
        self.assertEqual(result, 'John Doe')
    
    def test_format_value_none(self):
        """Test format_value with None input"""
        widget = FamilyAutoCompleteWidget()
        result = widget.format_value(None)
        self.assertIsNone(result)
    
    def test_format_value_list(self):
        """Test format_value with list input"""
        widget = FamilyAutoCompleteWidget()
        result = widget.format_value(['John', 'Jane', 'Bob'])
        self.assertEqual(result, 'John, Jane, Bob')
    
    def test_format_value_tuple(self):
        """Test format_value with tuple input"""
        widget = FamilyAutoCompleteWidget()
        result = widget.format_value(('Alice', 'Bob'))
        self.assertEqual(result, 'Alice, Bob')
    
    def test_format_value_empty_list(self):
        """Test format_value with empty list"""
        widget = FamilyAutoCompleteWidget()
        result = widget.format_value([])
        self.assertEqual(result, '[]')  # Django's default TextInput behavior
    
    def test_media(self):
        """Test widget media files"""
        widget = FamilyAutoCompleteWidget()
        media = widget.media
        
        self.assertIn('admin/css/family_autocomplete.css', str(media))
        self.assertIn('admin/js/family_autocomplete.js', str(media))


class TestLocationAutoCompleteWidget(unittest.TestCase):
    """Tests for LocationAutoCompleteWidget"""
    
    def test_init_default_attrs(self):
        """Test widget initialization with default attributes"""
        widget = LocationAutoCompleteWidget()
        
        self.assertEqual(widget.attrs['class'], 'location-autocomplete')
        self.assertEqual(widget.attrs['autocomplete'], 'off')
        self.assertEqual(widget.attrs['placeholder'], '输入地点名称...')
    
    def test_init_with_custom_attrs(self):
        """Test widget initialization with custom attributes"""
        custom_attrs = {'class': 'custom-location', 'readonly': True}
        widget = LocationAutoCompleteWidget(attrs=custom_attrs)
        
        self.assertEqual(widget.attrs['class'], 'custom-location')
        self.assertTrue(widget.attrs['readonly'])
        self.assertEqual(widget.attrs['autocomplete'], 'off')
    
    def test_media(self):
        """Test widget media files"""
        widget = LocationAutoCompleteWidget()
        media = widget.media
        
        self.assertIn('admin/css/family_autocomplete.css', str(media))
        self.assertIn('admin/js/location_autocomplete.js', str(media))


class TestInstitutionAutoCompleteWidget(unittest.TestCase):
    """Tests for InstitutionAutoCompleteWidget"""
    
    def test_init_default(self):
        """Test widget initialization with defaults"""
        widget = InstitutionAutoCompleteWidget()
        
        self.assertEqual(widget.attrs['class'], 'institution-autocomplete')
        self.assertEqual(widget.attrs['data-institution-type'], 'all')
        self.assertIsNone(widget.institution_type)
    
    def test_init_with_institution_type(self):
        """Test widget initialization with institution type"""
        widget = InstitutionAutoCompleteWidget(institution_type='hospital')
        
        self.assertEqual(widget.institution_type, 'hospital')
        self.assertEqual(widget.attrs['data-institution-type'], 'hospital')
    
    def test_init_with_custom_attrs(self):
        """Test widget initialization with custom attributes"""
        custom_attrs = {'placeholder': 'Search hospitals...'}
        widget = InstitutionAutoCompleteWidget(
            institution_type='school', 
            attrs=custom_attrs
        )
        
        self.assertEqual(widget.attrs['placeholder'], 'Search hospitals...')
        self.assertEqual(widget.attrs['data-institution-type'], 'school')
    
    def test_media(self):
        """Test widget media files"""
        widget = InstitutionAutoCompleteWidget()
        media = widget.media
        
        self.assertIn('admin/css/family_autocomplete.css', str(media))
        self.assertIn('admin/js/institution_autocomplete.js', str(media))


class TestFamilyDateWidget(unittest.TestCase):
    """Tests for FamilyDateWidget"""
    
    def test_init_default(self):
        """Test widget initialization with defaults"""
        widget = FamilyDateWidget()
        
        self.assertEqual(widget.attrs['class'], 'family-date-picker')
        self.assertEqual(widget.input_type, 'date')
    
    def test_init_with_attrs(self):
        """Test widget initialization with custom attributes"""
        custom_attrs = {'class': 'custom-date', 'min': '2020-01-01'}
        widget = FamilyDateWidget(attrs=custom_attrs)
        
        self.assertEqual(widget.attrs['class'], 'custom-date')
        self.assertEqual(widget.attrs['min'], '2020-01-01')
        self.assertEqual(widget.input_type, 'date')
    
    def test_render_basic(self):
        """Test basic render functionality"""
        widget = FamilyDateWidget()
        with patch.object(widget.__class__.__bases__[0], 'render') as mock_super_render:
            mock_super_render.return_value = '<input type="date" name="test_date">'
            
            result = widget.render('test_date', '2023-01-01')
            
            # Check it returns SafeString
            self.assertIsInstance(result, SafeString)
            
            # Check it contains the wrapper div
            self.assertIn('family-date-container', result)
            self.assertIn('data-field-name="test_date"', result)
            
            # Check quick date buttons
            self.assertIn('今天', result)
            self.assertIn('昨天', result)
            self.assertIn('一周前', result)
            self.assertIn('一月前', result)
            self.assertIn('清除', result)
            
            # Check onclick handlers
            self.assertIn("setFamilyDate(this, 'test_date', 0)", result)
            self.assertIn("setFamilyDate(this, 'test_date', -1)", result)
            self.assertIn("clearFamilyDate(this, 'test_date')", result)
    
    def test_render_with_renderer(self):
        """Test render with renderer parameter"""
        widget = FamilyDateWidget()
        mock_renderer = Mock()
        
        with patch.object(widget.__class__.__bases__[0], 'render') as mock_super_render:
            mock_super_render.return_value = '<input>'
            
            result = widget.render('field_name', None, renderer=mock_renderer)
            mock_super_render.assert_called_once_with('field_name', None, None, mock_renderer)
    
    def test_media(self):
        """Test widget media files"""
        widget = FamilyDateWidget()
        media = widget.media
        
        self.assertIn('admin/css/family_date_widget.css', str(media))
        self.assertIn('admin/js/family_date_widget.js', str(media))


class TestFamilyPhotoWidget(unittest.TestCase):
    """Tests for FamilyPhotoWidget"""
    
    def test_init_default(self):
        """Test widget initialization with defaults"""
        widget = FamilyPhotoWidget()
        
        self.assertEqual(widget.attrs['class'], 'family-photo-upload')
        self.assertEqual(widget.attrs['accept'], 'image/*')
        self.assertFalse(widget.attrs['multiple'])
    
    def test_init_with_attrs(self):
        """Test widget initialization with custom attributes"""
        custom_attrs = {'accept': 'image/jpeg,image/png', 'data-test': 'value'}
        widget = FamilyPhotoWidget(attrs=custom_attrs)
        
        self.assertEqual(widget.attrs['accept'], 'image/jpeg,image/png')
        self.assertEqual(widget.attrs['data-test'], 'value')
        self.assertEqual(widget.attrs['class'], 'family-photo-upload')
        # Note: 'multiple' is False by default and cannot be overridden in ClearableFileInput
    
    def test_render(self):
        """Test render functionality"""
        widget = FamilyPhotoWidget()
        with patch.object(widget.__class__.__bases__[0], 'render') as mock_super_render:
            mock_super_render.return_value = '<input type="file">'
            
            result = widget.render('photo', None)
            
            # Check it returns SafeString
            self.assertIsInstance(result, SafeString)
            
            # Check photo upload wrapper elements
            self.assertIn('photo-upload-wrapper', result)
            self.assertIn('photo-drop-zone', result)
            self.assertIn('ondrop="handlePhotoDrop(event)"', result)
            self.assertIn('ondragover="handlePhotoDragOver(event)"', result)
            
            # Check upload UI elements
            self.assertIn('📸', result)
            self.assertIn('点击选择照片', result)
            self.assertIn('拖拽照片到这里', result)
            self.assertIn('支持 JPG, PNG, GIF 格式', result)
            
            # Check preview elements
            self.assertIn('photo-preview', result)
            self.assertIn('preview-image', result)
            self.assertIn('onclick="removePhotoPreview(this)"', result)
    
    def test_media(self):
        """Test widget media files"""
        widget = FamilyPhotoWidget()
        media = widget.media
        
        self.assertIn('admin/css/family_photo_widget.css', str(media))
        self.assertIn('admin/js/family_photo_widget.js', str(media))


class TestRelationshipSelectorWidget(unittest.TestCase):
    """Tests for RelationshipSelectorWidget"""
    
    def test_init_default(self):
        """Test widget initialization with defaults"""
        widget = RelationshipSelectorWidget()
        
        self.assertEqual(widget.attrs['class'], 'relationship-selector')
        self.assertEqual(widget.attrs['size'], '6')
    
    def test_init_with_attrs(self):
        """Test widget initialization with custom attributes"""
        custom_attrs = {'class': 'custom-rel', 'size': '10'}
        widget = RelationshipSelectorWidget(attrs=custom_attrs)
        
        self.assertEqual(widget.attrs['class'], 'custom-rel')
        self.assertEqual(widget.attrs['size'], '10')
    
    def test_render(self):
        """Test render functionality"""
        widget = RelationshipSelectorWidget()
        with patch.object(widget.__class__.__bases__[0], 'render') as mock_super_render:
            mock_super_render.return_value = '<select name="rel_type"></select>'
            
            result = widget.render('rel_type', 'parent')
            
            # Check it returns SafeString
            self.assertIsInstance(result, SafeString)
            
            # Check container elements
            self.assertIn('relationship-widget-container', result)
            self.assertIn('relationship-header', result)
            
            # Check sections
            self.assertIn('血缘关系', result)
            self.assertIn('姻亲关系', result)
            self.assertIn('其他关系', result)
            
            # Check specific relationship buttons
            self.assertIn('父子', result)
            self.assertIn('母女', result)
            self.assertIn('夫妻', result)
            self.assertIn('朋友', result)
            
            # Check clear button
            self.assertIn("clearSelection('rel_type')", result)
            
            # Check hidden select wrapper
            self.assertIn('hidden-select-wrapper', result)
            self.assertIn('<select name="rel_type"></select>', result)
    
    def test_media(self):
        """Test widget media files"""
        widget = RelationshipSelectorWidget()
        media = widget.media
        
        self.assertIn('admin/css/relationship_widget.css', str(media))
        self.assertIn('admin/js/relationship_widget.js', str(media))


class TestRichTextWidget(unittest.TestCase):
    """Tests for RichTextWidget"""
    
    def test_init_default(self):
        """Test widget initialization with defaults"""
        widget = RichTextWidget()
        
        self.assertEqual(widget.attrs['class'], 'rich-text-editor')
        self.assertEqual(widget.attrs['rows'], 8)
    
    def test_init_with_attrs(self):
        """Test widget initialization with custom attributes"""
        custom_attrs = {'rows': 12, 'placeholder': 'Enter story...'}
        widget = RichTextWidget(attrs=custom_attrs)
        
        self.assertEqual(widget.attrs['rows'], 12)
        self.assertEqual(widget.attrs['placeholder'], 'Enter story...')
        self.assertEqual(widget.attrs['class'], 'rich-text-editor')
    
    def test_render(self):
        """Test render functionality"""
        widget = RichTextWidget()
        with patch.object(widget.__class__.__bases__[0], 'render') as mock_super_render:
            mock_super_render.return_value = '<textarea name="content"></textarea>'
            
            result = widget.render('content', 'Test content')
            
            # Check it returns SafeString
            self.assertIsInstance(result, SafeString)
            
            # Check container and toolbar
            self.assertIn('rich-text-container', result)
            self.assertIn('rich-text-toolbar', result)
            
            # Check toolbar buttons
            self.assertIn('data-command="bold"', result)
            self.assertIn('data-command="italic"', result)
            self.assertIn('data-command="underline"', result)
            self.assertIn('data-command="heading"', result)
            self.assertIn('data-command="quote"', result)
            self.assertIn('data-command="list"', result)
            self.assertIn('data-command="photo"', result)
            self.assertIn('data-command="emoji"', result)
            
            # Check button labels
            self.assertIn('<strong>B</strong>', result)
            self.assertIn('<em>I</em>', result)
            self.assertIn('<u>U</u>', result)
            self.assertIn('📷', result)
            self.assertIn('😊', result)
            
            # Check textarea is included
            self.assertIn('<textarea name="content"></textarea>', result)
    
    def test_media(self):
        """Test widget media files"""
        widget = RichTextWidget()
        media = widget.media
        
        self.assertIn('admin/css/rich_text_widget.css', str(media))
        self.assertIn('admin/js/rich_text_widget.js', str(media))


class TestTagsWidget(unittest.TestCase):
    """Tests for TagsWidget"""
    
    def test_init_default(self):
        """Test widget initialization with defaults"""
        widget = TagsWidget()
        
        self.assertEqual(widget.attrs['class'], 'tags-input')
        self.assertEqual(widget.attrs['placeholder'], '输入标签，用逗号分隔...')
    
    def test_init_with_attrs(self):
        """Test widget initialization with custom attributes"""
        custom_attrs = {'class': 'custom-tags', 'maxlength': 100}
        widget = TagsWidget(attrs=custom_attrs)
        
        self.assertEqual(widget.attrs['class'], 'custom-tags')
        self.assertEqual(widget.attrs['maxlength'], 100)
        self.assertEqual(widget.attrs['placeholder'], '输入标签，用逗号分隔...')
    
    def test_render(self):
        """Test render functionality"""
        widget = TagsWidget()
        with patch.object(widget.__class__.__bases__[0], 'render') as mock_super_render:
            mock_super_render.return_value = '<input name="tags">'
            
            result = widget.render('tags', 'tag1,tag2')
            
            # Check it returns SafeString
            self.assertIsInstance(result, SafeString)
            
            # Check wrapper elements
            self.assertIn('tags-wrapper', result)
            self.assertIn('tags-container', result)
            self.assertIn('tags-suggestions', result)
            
            # Check suggestion categories
            self.assertIn('常用标签', result)
            self.assertIn('情感标签', result)
            
            # Check specific tag suggestions
            self.assertIn('生日', result)
            self.assertIn('节日', result)
            self.assertIn('旅行', result)
            self.assertIn('温馨', result)
            self.assertIn('感动', result)
            self.assertIn('快乐', result)
            
            # Check input is included
            self.assertIn('<input name="tags">', result)
    
    def test_media(self):
        """Test widget media files"""
        widget = TagsWidget()
        media = widget.media
        
        self.assertIn('admin/css/tags_widget.css', str(media))
        self.assertIn('admin/js/tags_widget.js', str(media))


if __name__ == '__main__':
    unittest.main()