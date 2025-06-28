"""
Admin mixins for Family Knowledge Management System
Enhanced admin functionality including inline creation
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.admin.views.main import ChangeList


class InlineCreateMixin:
    """
    Mixin to add inline creation capability to admin forms
    Adds '+' buttons next to foreign key and many-to-many fields
    """
    
    # Define which fields should have inline creation buttons
    inline_create_fields = []
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Override to add inline create button for foreign key fields
        """
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        
        if db_field.name in self.inline_create_fields:
            formfield.widget = self.get_inline_create_widget(
                formfield.widget, 
                db_field.related_model
            )
        
        return formfield
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Override to add inline create button for many-to-many fields
        """
        formfield = super().formfield_for_manytomany(db_field, request, **kwargs)
        
        if db_field.name in self.inline_create_fields:
            formfield.widget = self.get_inline_create_widget(
                formfield.widget, 
                db_field.related_model
            )
        
        return formfield
    
    def get_inline_create_widget(self, original_widget, related_model):
        """
        Create a widget wrapper that includes an inline create button
        """
        app_label = related_model._meta.app_label
        model_name = related_model._meta.model_name
        
        class InlineCreateWidgetWrapper:
            def __init__(self, widget):
                self.widget = widget
                self.related_model = related_model
                self.app_label = app_label
                self.model_name = model_name
            
            def render(self, name, value, attrs=None, renderer=None):
                # Get the original widget HTML
                original_html = self.widget.render(name, value, attrs, renderer)
                
                # Add the create button
                create_url = reverse(f'admin:{app_label}_{model_name}_add')
                # Check if this is a FilteredSelectMultiple widget (transfer widget)
                is_transfer_widget = 'FilteredSelectMultiple' in str(type(self.widget))
                
                if is_transfer_widget:
                    # For transfer widgets, inject the button into the available objects area
                    create_button = self._inject_button_into_transfer_widget(
                        original_html, create_url, name, related_model._meta.verbose_name
                    )
                else:
                    # For regular widgets, wrap normally
                    create_button = format_html(
                        '''
                        <div class="inline-create-wrapper">
                            {original}
                            <a href="{url}" class="inline-create-btn" 
                               onclick="return showInlineCreatePopup(this, '{field_name}');"
                               title="添加新{verbose_name}">
                                <span class="create-icon">+</span>
                                <span class="create-text">新建</span>
                            </a>
                        </div>
                        ''',
                        original=original_html,
                        url=create_url,
                        field_name=name,
                        verbose_name=related_model._meta.verbose_name
                    )
                
                return create_button
            
            def _inject_button_into_transfer_widget(self, original_html, create_url, field_name, verbose_name):
                """
                Inject the create button into the available objects section of transfer widget
                """
                # Look for the available objects section header or filter input
                import re
                
                # Try to find the "Available" header or filter input in the transfer widget
                available_pattern = r'(<h2[^>]*>.*?可选.*?</h2>|<p[^>]*class="help"[^>]*>.*?可选.*?</p>|<label[^>]*>.*?Filter.*?</label>)'
                filter_pattern = r'(<input[^>]*id="id_' + re.escape(field_name) + r'_input"[^>]*>)'
                
                create_button_html = format_html(
                    '''
                    <div class="transfer-widget-create-btn">
                        <a href="{url}" class="inline-create-btn compact" 
                           onclick="return showInlineCreatePopup(this, '{field_name}');"
                           title="添加新{verbose_name}">
                            <span class="create-icon">+</span>
                            <span class="create-text">新建{verbose_name}</span>
                        </a>
                    </div>
                    ''',
                    url=create_url,
                    field_name=field_name,
                    verbose_name=verbose_name
                )
                
                # Try to inject after the filter input
                modified_html = re.sub(
                    filter_pattern,
                    r'\1' + str(create_button_html),
                    original_html,
                    count=1
                )
                
                # If that didn't work, try to inject after any available objects header
                if modified_html == original_html:
                    modified_html = re.sub(
                        available_pattern,
                        r'\1' + str(create_button_html),
                        original_html,
                        count=1,
                        flags=re.IGNORECASE
                    )
                
                # If still no match, inject at the beginning of the selector-available div
                if modified_html == original_html:
                    available_div_pattern = r'(<div[^>]*class="[^"]*selector-available[^"]*"[^>]*>)'
                    modified_html = re.sub(
                        available_div_pattern,
                        r'\1' + str(create_button_html),
                        original_html,
                        count=1
                    )
                
                # Final fallback: wrap the entire widget
                if modified_html == original_html:
                    modified_html = format_html(
                        '''
                        <div class="inline-create-wrapper transfer-widget">
                            {create_button}
                            {original}
                        </div>
                        ''',
                        create_button=create_button_html,
                        original=original_html
                    )
                
                return modified_html
            
            def __getattr__(self, name):
                # Delegate attribute access to the wrapped widget
                return getattr(self.widget, name)
            
            @property
            def media(self):
                # Combine original widget media with our custom media
                from django import forms
                widget_media = getattr(self.widget, 'media', forms.Media())
                custom_media = forms.Media(
                    css={'all': ('admin/css/inline_create.css',)},
                    js=('admin/js/inline_create.js',)
                )
                return widget_media + custom_media
        
        return InlineCreateWidgetWrapper(original_widget)


class QuickCreateMixin:
    """
    Mixin to handle quick creation of related objects via AJAX
    """
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('quick_create/<str:model_name>/', 
                 self.admin_site.admin_view(self.quick_create_view), 
                 name=f'{self.model._meta.app_label}_{self.model._meta.model_name}_quick_create'),
        ]
        return custom_urls + urls
    
    def quick_create_view(self, request, model_name):
        """
        Handle quick creation of related objects
        """
        # Import here to avoid circular imports
        from django.apps import apps
        
        try:
            model = apps.get_model(self.model._meta.app_label, model_name)
            model_admin = self.admin_site._registry.get(model)
            
            if not model_admin:
                return JsonResponse({'error': 'Model admin not found'}, status=404)
            
            if request.method == 'POST':
                # Handle form submission
                form = model_admin.get_form(request)()
                form = form.__class__(request.POST)
                
                if form.is_valid():
                    obj = form.save()
                    return JsonResponse({
                        'success': True,
                        'id': obj.pk,
                        'name': str(obj),
                        'model': model_name
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'errors': form.errors
                    })
            
            else:
                # Show form
                form = model_admin.get_form(request)()
                context = {
                    'form': form,
                    'model_name': model_name,
                    'verbose_name': model._meta.verbose_name,
                    'opts': model._meta,
                }
                return render(request, 'admin/quick_create_form.html', context)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class FamilyAdminMixin(InlineCreateMixin, QuickCreateMixin):
    """
    Combined mixin for family-friendly admin features
    """
    pass