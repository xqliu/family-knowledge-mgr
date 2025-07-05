"""
Comprehensive tests for family admin mixins targeting 90%+ branch coverage
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
from django.http import JsonResponse
from django import forms
import json


class TestInlineCreateMixin(unittest.TestCase):
    """Comprehensive tests for InlineCreateMixin functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Import here to avoid Django setup issues
        from family.admin_mixins import InlineCreateMixin
        
        self.mixin = InlineCreateMixin()
        self.mixin.inline_create_fields = ['person', 'location', 'people']
        
        # Create mock model
        self.mock_model = Mock()
        self.mock_model._meta = Mock()
        self.mock_model._meta.app_label = 'family'
        self.mock_model._meta.model_name = 'person'
        self.mock_model._meta.verbose_name = 'Person'
        
        # Mock request
        self.request = Mock()
        
    def test_formfield_for_foreignkey_not_in_inline_fields(self):
        """Test formfield_for_foreignkey with field not in inline_create_fields"""
        mock_db_field = Mock()
        mock_db_field.name = 'other_field'
        mock_db_field.related_model = self.mock_model
        
        # Mock the super call
        mock_formfield = Mock()
        with patch('family.admin_mixins.super') as mock_super:
            mock_super.return_value.formfield_for_foreignkey.return_value = mock_formfield
            
            result = self.mixin.formfield_for_foreignkey(mock_db_field, self.request)
            
            # Should return the original formfield without modification
            self.assertEqual(result, mock_formfield)
            
    def test_formfield_for_foreignkey_in_inline_fields(self):
        """Test formfield_for_foreignkey with field in inline_create_fields"""
        mock_db_field = Mock()
        mock_db_field.name = 'person'
        mock_db_field.related_model = self.mock_model
        
        mock_formfield = Mock()
        mock_widget = Mock()
        mock_formfield.widget = mock_widget
        
        with patch('family.admin_mixins.super') as mock_super:
            mock_super.return_value.formfield_for_foreignkey.return_value = mock_formfield
            
            with patch.object(self.mixin, 'get_inline_create_widget') as mock_get_widget:
                mock_new_widget = Mock()
                mock_get_widget.return_value = mock_new_widget
                
                result = self.mixin.formfield_for_foreignkey(mock_db_field, self.request)
                
                # Should call get_inline_create_widget and set widget
                mock_get_widget.assert_called_once_with(mock_widget, self.mock_model)
                self.assertEqual(result.widget, mock_new_widget)
                
    def test_formfield_for_manytomany_not_in_inline_fields(self):
        """Test formfield_for_manytomany with field not in inline_create_fields"""
        mock_db_field = Mock()
        mock_db_field.name = 'other_field'
        mock_db_field.related_model = self.mock_model
        
        mock_formfield = Mock()
        with patch('family.admin_mixins.super') as mock_super:
            mock_super.return_value.formfield_for_manytomany.return_value = mock_formfield
            
            result = self.mixin.formfield_for_manytomany(mock_db_field, self.request)
            
            # Should return the original formfield without modification
            self.assertEqual(result, mock_formfield)
            
    def test_formfield_for_manytomany_in_inline_fields(self):
        """Test formfield_for_manytomany with field in inline_create_fields"""
        mock_db_field = Mock()
        mock_db_field.name = 'people'  # Many-to-many field
        mock_db_field.related_model = self.mock_model
        
        mock_formfield = Mock()
        mock_widget = Mock()
        mock_formfield.widget = mock_widget
        
        with patch('family.admin_mixins.super') as mock_super:
            mock_super.return_value.formfield_for_manytomany.return_value = mock_formfield
            
            with patch.object(self.mixin, 'get_inline_create_widget') as mock_get_widget:
                mock_new_widget = Mock()
                mock_get_widget.return_value = mock_new_widget
                
                result = self.mixin.formfield_for_manytomany(mock_db_field, self.request)
                
                # Should call get_inline_create_widget and set widget
                mock_get_widget.assert_called_once_with(mock_widget, self.mock_model)
                self.assertEqual(result.widget, mock_new_widget)
                
    def test_get_inline_create_widget_creates_wrapper(self):
        """Test get_inline_create_widget method creates proper wrapper"""
        mock_widget = Mock()
        mock_widget.render = Mock(return_value='<select></select>')
        
        wrapper = self.mixin.get_inline_create_widget(mock_widget, self.mock_model)
        
        # Should return a wrapper with correct properties
        self.assertEqual(wrapper.widget, mock_widget)
        self.assertEqual(wrapper.related_model, self.mock_model)
        self.assertEqual(wrapper.app_label, 'family')
        self.assertEqual(wrapper.model_name, 'person')
    
    def test_inline_create_widget_wrapper_render_regular_widget(self):
        """Test InlineCreateWidgetWrapper render method for regular widgets"""
        mock_widget = Mock()
        mock_widget.render = Mock(return_value='<select></select>')
        
        with patch('family.admin_mixins.reverse') as mock_reverse:
            mock_reverse.return_value = '/admin/family/person/add/'
            
            wrapper = self.mixin.get_inline_create_widget(mock_widget, self.mock_model)
            result = wrapper.render('person', None, {})
            
            # Should contain the create button elements
            self.assertIn('inline-create-wrapper', result)
            self.assertIn('inline-create-btn', result)
            self.assertIn('新建', result)
            self.assertIn('showInlineCreatePopup', result)
            mock_reverse.assert_called_once_with('admin:family_person_add')
    
    def test_inline_create_widget_wrapper_render_transfer_widget(self):
        """Test InlineCreateWidgetWrapper render method for transfer widgets"""
        # Create a mock transfer widget with proper type name
        from django.contrib.admin.widgets import FilteredSelectMultiple
        mock_widget = Mock(spec=FilteredSelectMultiple)
        mock_widget.render = Mock(return_value='<div class="selector-available">Available</div>')
        
        with patch('family.admin_mixins.reverse') as mock_reverse:
            mock_reverse.return_value = '/admin/family/person/add/'
            
            wrapper = self.mixin.get_inline_create_widget(mock_widget, self.mock_model)
            result = wrapper.render('people', None, {})
            
            # Should detect transfer widget and inject button
            self.assertIn('transfer-widget-create-btn', result)
            self.assertIn('selector-available', result)
    
    def test_inline_create_widget_wrapper_inject_button_filter_pattern(self):
        """Test _inject_button_into_transfer_widget with filter pattern match"""
        mock_widget = Mock()
        wrapper = self.mixin.get_inline_create_widget(mock_widget, self.mock_model)
        
        original_html = '<input id="id_people_input" type="text"><div>Other content</div>'
        create_url = '/admin/family/person/add/'
        field_name = 'people'
        verbose_name = 'Person'
        
        result = wrapper._inject_button_into_transfer_widget(
            original_html, create_url, field_name, verbose_name
        )
        
        # Should inject the create button after the filter input
        self.assertIn('id="id_people_input"', result)
        self.assertIn('transfer-widget-create-btn', result)
        # Button should appear after input
        input_pos = result.find('id="id_people_input"')
        button_pos = result.find('transfer-widget-create-btn')
        self.assertGreater(button_pos, input_pos)
        
    def test_inline_create_widget_wrapper_inject_button_available_pattern(self):
        """Test _inject_button_into_transfer_widget with available header pattern"""
        mock_widget = Mock()
        wrapper = self.mixin.get_inline_create_widget(mock_widget, self.mock_model)
        
        original_html = '<h2>可选的项目</h2><div>Content</div>'
        create_url = '/admin/family/person/add/'
        field_name = 'people'
        verbose_name = 'Person'
        
        result = wrapper._inject_button_into_transfer_widget(
            original_html, create_url, field_name, verbose_name
        )
        
        # Should inject the create button after the header
        self.assertIn('可选', result)
        self.assertIn('transfer-widget-create-btn', result)
        
    def test_inline_create_widget_wrapper_inject_button_selector_div_pattern(self):
        """Test _inject_button_into_transfer_widget with selector-available div pattern"""
        mock_widget = Mock()
        wrapper = self.mixin.get_inline_create_widget(mock_widget, self.mock_model)
        
        original_html = '<div class="selector-available">Available items</div>'
        create_url = '/admin/family/person/add/'
        field_name = 'people'
        verbose_name = 'Person'
        
        result = wrapper._inject_button_into_transfer_widget(
            original_html, create_url, field_name, verbose_name
        )
        
        # Should inject the create button inside the selector-available div
        self.assertIn('selector-available', result)
        self.assertIn('transfer-widget-create-btn', result)
        
    def test_inline_create_widget_wrapper_inject_button_fallback(self):
        """Test _inject_button_into_transfer_widget fallback case"""
        mock_widget = Mock()
        wrapper = self.mixin.get_inline_create_widget(mock_widget, self.mock_model)
        
        original_html = '<div>No matching patterns here</div>'
        create_url = '/admin/family/person/add/'
        field_name = 'people'
        verbose_name = 'Person'
        
        result = wrapper._inject_button_into_transfer_widget(
            original_html, create_url, field_name, verbose_name
        )
        
        # Should wrap the entire widget as fallback
        self.assertIn('inline-create-wrapper transfer-widget', result)
        self.assertIn('transfer-widget-create-btn', result)
        self.assertIn('No matching patterns here', result)
        
    def test_inline_create_widget_wrapper_inject_button_help_pattern(self):
        """Test _inject_button_into_transfer_widget with help text pattern"""
        mock_widget = Mock()
        wrapper = self.mixin.get_inline_create_widget(mock_widget, self.mock_model)
        
        original_html = '<p class="help">可选的人员</p><div>Content</div>'
        create_url = '/admin/family/person/add/'
        field_name = 'people'
        verbose_name = 'Person'
        
        result = wrapper._inject_button_into_transfer_widget(
            original_html, create_url, field_name, verbose_name
        )
        
        # Should inject the create button after the help text
        self.assertIn('可选', result)
        self.assertIn('transfer-widget-create-btn', result)
        
    def test_inline_create_widget_wrapper_inject_button_label_pattern(self):
        """Test _inject_button_into_transfer_widget with label pattern"""
        mock_widget = Mock()
        wrapper = self.mixin.get_inline_create_widget(mock_widget, self.mock_model)
        
        original_html = '<label>Filter</label><input type="text">'
        create_url = '/admin/family/person/add/'
        field_name = 'people'
        verbose_name = 'Person'
        
        result = wrapper._inject_button_into_transfer_widget(
            original_html, create_url, field_name, verbose_name
        )
        
        # Should inject the create button after the label
        self.assertIn('Filter', result)
        self.assertIn('transfer-widget-create-btn', result)
        
    def test_inline_create_widget_wrapper_getattr_delegation(self):
        """Test InlineCreateWidgetWrapper __getattr__ delegation"""
        mock_widget = Mock()
        mock_widget.custom_attr = 'custom_value'
        mock_widget.choices = [('1', 'Choice 1')]
        
        wrapper = self.mixin.get_inline_create_widget(mock_widget, self.mock_model)
        
        # Should delegate to the wrapped widget
        self.assertEqual(wrapper.custom_attr, 'custom_value')
        self.assertEqual(wrapper.choices, [('1', 'Choice 1')])
    
    def test_inline_create_widget_wrapper_media_property(self):
        """Test InlineCreateWidgetWrapper media property combination"""
        mock_widget = Mock()
        # Create a mock Media object
        mock_media = Mock()
        mock_media.__str__ = Mock(return_value='<script src="widget.js"></script><link href="widget.css">')
        mock_media.__add__ = Mock(return_value=mock_media)
        mock_widget.media = mock_media
        
        wrapper = self.mixin.get_inline_create_widget(mock_widget, self.mock_model)
        
        # Access media property
        media = wrapper.media
        self.assertIsNotNone(media)
        
    def test_inline_create_widget_wrapper_media_property_no_widget_media(self):
        """Test InlineCreateWidgetWrapper media property when widget has no media"""
        # Create a mock widget with no media attribute
        mock_widget = Mock(spec=['render'])
        
        wrapper = self.mixin.get_inline_create_widget(mock_widget, self.mock_model)
        
        # Should still return custom media
        media = wrapper.media
        self.assertIsNotNone(media)
        # Check that custom media files are included
        media_str = str(media)
        self.assertIn('admin/css/inline_create.css', media_str)
        self.assertIn('admin/js/inline_create.js', media_str)


class TestQuickCreateMixin(unittest.TestCase):
    """Comprehensive tests for QuickCreateMixin functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        from family.admin_mixins import QuickCreateMixin
        from django.contrib.admin import AdminSite
        
        self.mixin = QuickCreateMixin()
        
        # Mock the model
        self.mock_model = Mock()
        self.mock_model._meta = Mock()
        self.mock_model._meta.app_label = 'family'
        self.mock_model._meta.model_name = 'person'
        self.mock_model._meta.verbose_name = 'Person'
        self.mixin.model = self.mock_model
        
        # Mock admin site
        self.mixin.admin_site = AdminSite()
        
    def test_get_urls_adds_custom_url(self):
        """Test get_urls method adds custom URL"""
        with patch('family.admin_mixins.super') as mock_super:
            mock_super.return_value.get_urls.return_value = []
            
            urls = self.mixin.get_urls()
            
            # Should add one custom URL
            self.assertEqual(len(urls), 1)
            self.assertIn('quick_create', str(urls[0].pattern))
            
    def test_quick_create_view_get_request_success(self):
        """Test quick_create_view with GET request"""
        request = Mock()
        request.method = 'GET'
        
        # Mock model admin
        mock_model_admin = Mock()
        mock_form_class = Mock()
        mock_form_instance = Mock()
        mock_form_class.return_value = mock_form_instance
        mock_model_admin.get_form.return_value = mock_form_class
        
        # Mock apps.get_model and render
        with patch('django.apps.apps.get_model') as mock_get_model:
            mock_get_model.return_value = self.mock_model
            self.mixin.admin_site._registry = {self.mock_model: mock_model_admin}
            
            with patch('family.admin_mixins.render') as mock_render:
                mock_render.return_value = Mock()
                
                result = self.mixin.quick_create_view(request, 'person')
                
                # Should render the form
                mock_render.assert_called_once()
                call_args = mock_render.call_args[0]
                self.assertEqual(call_args[0], request)
                self.assertEqual(call_args[1], 'admin/quick_create_form.html')
                
                # Check context
                context = mock_render.call_args[0][2]
                self.assertEqual(context['form'], mock_form_instance)
                self.assertEqual(context['model_name'], 'person')
                self.assertEqual(context['verbose_name'], 'Person')
                self.assertEqual(context['opts'], self.mock_model._meta)
    
    def test_quick_create_view_post_request_valid(self):
        """Test quick_create_view with valid POST request"""
        request = Mock()
        request.method = 'POST'
        request.POST = {'name': 'Test Person'}
        
        # Mock the form submission chain
        mock_model_admin = Mock()
        mock_form_class = Mock()
        mock_form_instance = Mock()
        mock_form_instance.is_valid.return_value = True
        
        # Mock saved object
        mock_obj = Mock()
        mock_obj.pk = 1
        mock_obj.__str__ = Mock(return_value='Test Person')
        mock_form_instance.save.return_value = mock_obj
        
        mock_form_class.return_value = mock_form_instance
        mock_model_admin.get_form.return_value = mock_form_class
        
        with patch('django.apps.apps.get_model') as mock_get_model:
            mock_get_model.return_value = self.mock_model
            self.mixin.admin_site._registry = {self.mock_model: mock_model_admin}
            
            result = self.mixin.quick_create_view(request, 'person')
            
            # Should return success JSON response
            self.assertIsInstance(result, JsonResponse)
            
            # Decode JSON response
            content = json.loads(result.content.decode('utf-8'))
            self.assertTrue(content['success'])
            self.assertEqual(content['id'], 1)
            self.assertEqual(content['name'], 'Test Person')
            self.assertEqual(content['model'], 'person')
    
    def test_quick_create_view_post_request_invalid(self):
        """Test quick_create_view with invalid POST request"""
        request = Mock()
        request.method = 'POST'
        request.POST = {'name': ''}
        
        # Mock form validation failure
        mock_model_admin = Mock()
        mock_form_class = Mock()
        mock_form_instance = Mock()
        mock_form_instance.is_valid.return_value = False
        mock_form_instance.errors = {'name': ['This field is required.']}
        
        mock_form_class.return_value = mock_form_instance
        mock_model_admin.get_form.return_value = mock_form_class
        
        with patch('django.apps.apps.get_model') as mock_get_model:
            mock_get_model.return_value = self.mock_model
            self.mixin.admin_site._registry = {self.mock_model: mock_model_admin}
            
            result = self.mixin.quick_create_view(request, 'person')
            
            # Should return error JSON response
            self.assertIsInstance(result, JsonResponse)
            
            content = json.loads(result.content.decode('utf-8'))
            self.assertFalse(content['success'])
            self.assertEqual(content['errors'], {'name': ['This field is required.']})
    
    def test_quick_create_view_model_admin_not_found(self):
        """Test quick_create_view when model admin not found"""
        request = Mock()
        request.method = 'GET'
        
        with patch('django.apps.apps.get_model') as mock_get_model:
            mock_get_model.return_value = self.mock_model
            # Empty registry - no model admin
            self.mixin.admin_site._registry = {}
            
            result = self.mixin.quick_create_view(request, 'person')
            
            # Should return 404 error
            self.assertIsInstance(result, JsonResponse)
            self.assertEqual(result.status_code, 404)
            
            content = json.loads(result.content.decode('utf-8'))
            self.assertEqual(content['error'], 'Model admin not found')
    
    def test_quick_create_view_exception_handling(self):
        """Test quick_create_view exception handling"""
        request = Mock()
        request.method = 'GET'
        
        # Mock apps.get_model to raise exception
        with patch('django.apps.apps.get_model') as mock_get_model:
            mock_get_model.side_effect = Exception('Model loading error')
            
            result = self.mixin.quick_create_view(request, 'person')
            
            # Should return 500 error
            self.assertIsInstance(result, JsonResponse)
            self.assertEqual(result.status_code, 500)
            
            content = json.loads(result.content.decode('utf-8'))
            self.assertEqual(content['error'], 'Model loading error')


class TestFamilyAdminMixin(unittest.TestCase):
    """Comprehensive tests for FamilyAdminMixin functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        from family.admin_mixins import FamilyAdminMixin, InlineCreateMixin, QuickCreateMixin
        from django.contrib.admin import AdminSite
        
        self.mixin = FamilyAdminMixin()
        
        # Store classes for inheritance testing
        self.InlineCreateMixin = InlineCreateMixin
        self.QuickCreateMixin = QuickCreateMixin
        
        # Mock model
        self.mock_model = Mock()
        self.mock_model._meta = Mock()
        self.mock_model._meta.app_label = 'family'
        self.mock_model._meta.model_name = 'person'
        self.mixin.model = self.mock_model
        
        # Mock admin site
        self.mixin.admin_site = AdminSite()
        
    def test_inheritance(self):
        """Test that FamilyAdminMixin inherits from both mixins"""
        # Testing class inheritance
        self.assertIsInstance(self.mixin, self.InlineCreateMixin)
        self.assertIsInstance(self.mixin, self.QuickCreateMixin)
        
    def test_combined_functionality_inline_create(self):
        """Test that combined functionality works for inline create"""
        # Set inline create fields
        self.mixin.inline_create_fields = ['location']
        
        # Since FamilyAdminMixin inherits from InlineCreateMixin, it should have the method
        self.assertTrue(hasattr(self.mixin, 'formfield_for_foreignkey'))
        self.assertTrue(hasattr(self.mixin, 'get_inline_create_widget'))
        
    def test_combined_functionality_quick_create(self):
        """Test that combined functionality works for quick create"""
        # Since FamilyAdminMixin inherits from QuickCreateMixin, it should have the methods
        self.assertTrue(hasattr(self.mixin, 'get_urls'))
        self.assertTrue(hasattr(self.mixin, 'quick_create_view'))
        
    def test_no_method_conflicts(self):
        """Test that there are no method conflicts between mixins"""
        # Get all methods from both parent mixins
        inline_methods = [m for m in dir(self.InlineCreateMixin) if not m.startswith('_')]
        quick_methods = [m for m in dir(self.QuickCreateMixin) if not m.startswith('_')]
        
        # Check that there are no overlapping method names
        common_methods = set(inline_methods) & set(quick_methods)
        
        # Should have no conflicting methods
        self.assertEqual(len(common_methods), 0)


if __name__ == '__main__':
    unittest.main()