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
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Add inline creation widgets to specified fields
        for field_name in self.inline_create_fields:
            if field_name in form.base_fields:
                field = form.base_fields[field_name]
                related_model = None
                
                # Get related model for ForeignKey or ManyToMany fields
                if hasattr(field, 'queryset') and field.queryset is not None:
                    related_model = field.queryset.model
                
                if related_model:
                    # Add custom widget with create button
                    field.widget = self.get_inline_create_widget(field.widget, related_model)
        
        return form
    
    def get_inline_create_widget(self, original_widget, related_model):
        """
        Create a widget wrapper that includes an inline create button
        """
        app_label = related_model._meta.app_label
        model_name = related_model._meta.model_name
        
        class InlineCreateWidget(original_widget.__class__):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.related_model = related_model
                self.app_label = app_label
                self.model_name = model_name
            
            def render(self, name, value, attrs=None, renderer=None):
                # Get the original widget HTML
                original_html = super().render(name, value, attrs, renderer)
                
                # Add the create button
                create_url = reverse(f'admin:{app_label}_{model_name}_add')
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
            
            class Media:
                css = {
                    'all': ('admin/css/inline_create.css',)
                }
                js = ('admin/js/inline_create.js',)
        
        return InlineCreateWidget()


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