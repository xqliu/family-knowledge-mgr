"""
Custom widgets for Family Knowledge Management System
Enhanced form widgets with family-friendly features
"""

from django import forms
from django.forms.widgets import Widget
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.templatetags.static import static
import json


class FamilyAutoCompleteWidget(forms.TextInput):
    """
    Auto-complete widget for family member names
    """
    def __init__(self, model=None, attrs=None):
        self.model = model
        default_attrs = {
            'class': 'family-autocomplete',
            'autocomplete': 'off',
            'placeholder': '开始输入姓名...'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def format_value(self, value):
        if value and hasattr(value, '__iter__') and not isinstance(value, str):
            return ', '.join(str(v) for v in value)
        return super().format_value(value)
    
    class Media:
        css = {
            'all': ('admin/css/family_autocomplete.css',)
        }
        js = ('admin/js/family_autocomplete.js',)


class LocationAutoCompleteWidget(forms.TextInput):
    """
    Auto-complete widget for locations
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'location-autocomplete',
            'autocomplete': 'off',
            'placeholder': '输入地点名称...'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    class Media:
        css = {
            'all': ('admin/css/family_autocomplete.css',)
        }
        js = ('admin/js/location_autocomplete.js',)


class InstitutionAutoCompleteWidget(forms.TextInput):
    """
    Auto-complete widget for institutions (hospitals, schools, companies)
    """
    def __init__(self, institution_type=None, attrs=None):
        self.institution_type = institution_type
        default_attrs = {
            'class': 'institution-autocomplete',
            'autocomplete': 'off',
            'placeholder': '输入机构名称...',
            'data-institution-type': institution_type or 'all'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    class Media:
        css = {
            'all': ('admin/css/family_autocomplete.css',)
        }
        js = ('admin/js/institution_autocomplete.js',)


class FamilyDateWidget(forms.DateInput):
    """
    Enhanced date picker with quick options
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'family-date-picker',
            'type': 'date'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        
        quick_dates_html = '''
        <div class="quick-dates-wrapper">
            <div class="quick-dates">
                <button type="button" class="quick-date-btn" data-days="0">今天</button>
                <button type="button" class="quick-date-btn" data-days="-1">昨天</button>
                <button type="button" class="quick-date-btn" data-days="-7">一周前</button>
                <button type="button" class="quick-date-btn" data-days="-30">一月前</button>
                <button type="button" class="quick-date-btn" data-clear="true">清除</button>
            </div>
        </div>
        '''
        
        return mark_safe(html + quick_dates_html)
    
    class Media:
        css = {
            'all': ('admin/css/family_date_widget.css',)
        }
        js = ('admin/js/family_date_widget.js',)


class FamilyPhotoWidget(forms.ClearableFileInput):
    """
    Enhanced photo upload widget with preview and drag-drop
    """
    template_name = 'admin/widgets/family_photo_widget.html'
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'family-photo-upload',
            'accept': 'image/*',
            'multiple': False
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        # Get the base file input
        input_html = super().render(name, value, attrs, renderer)
        
        # Add preview and drag-drop functionality
        preview_html = '''
        <div class="photo-upload-wrapper">
            <div class="photo-drop-zone" ondrop="handlePhotoDrop(event)" ondragover="handlePhotoDragOver(event)" ondragleave="handlePhotoDragLeave(event)">
                <div class="drop-zone-content">
                    <div class="upload-icon">📸</div>
                    <div class="upload-text">
                        <p><strong>点击选择照片</strong> 或 拖拽照片到这里</p>
                        <p class="upload-hint">支持 JPG, PNG, GIF 格式</p>
                    </div>
                </div>
                <div class="photo-preview" style="display: none;">
                    <img class="preview-image" src="" alt="预览">
                    <div class="preview-info">
                        <span class="file-name"></span>
                        <span class="file-size"></span>
                    </div>
                    <button type="button" class="remove-photo" onclick="removePhotoPreview(this)">×</button>
                </div>
            </div>
        </div>
        '''
        
        return mark_safe(preview_html + input_html)
    
    class Media:
        css = {
            'all': ('admin/css/family_photo_widget.css',)
        }
        js = ('admin/js/family_photo_widget.js',)


class RelationshipSelectorWidget(forms.SelectMultiple):
    """
    Visual relationship selector with family tree interface
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'relationship-selector',
            'size': '6'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        # Get the base select widget
        select_html = super().render(name, value, attrs, renderer)
        
        # Add visual relationship interface
        visual_html = '''
        <div class="relationship-visual">
            <div class="family-tree-mini">
                <div class="tree-level" data-generation="2">
                    <div class="tree-node grandparents">祖父母辈</div>
                </div>
                <div class="tree-level" data-generation="1">
                    <div class="tree-node parents">父母辈</div>
                </div>
                <div class="tree-level current" data-generation="0">
                    <div class="tree-node self">本人</div>
                </div>
                <div class="tree-level" data-generation="-1">
                    <div class="tree-node children">子女辈</div>
                </div>
                <div class="tree-level" data-generation="-2">
                    <div class="tree-node grandchildren">孙辈</div>
                </div>
            </div>
            <div class="relationship-types">
                <div class="relationship-category">
                    <h4>血缘关系</h4>
                    <div class="relationship-options">
                        <button type="button" class="relation-btn" data-relation="父亲">父亲</button>
                        <button type="button" class="relation-btn" data-relation="母亲">母亲</button>
                        <button type="button" class="relation-btn" data-relation="儿子">儿子</button>
                        <button type="button" class="relation-btn" data-relation="女儿">女儿</button>
                        <button type="button" class="relation-btn" data-relation="兄弟">兄弟</button>
                        <button type="button" class="relation-btn" data-relation="姐妹">姐妹</button>
                    </div>
                </div>
                <div class="relationship-category">
                    <h4>姻亲关系</h4>
                    <div class="relationship-options">
                        <button type="button" class="relation-btn" data-relation="配偶">配偶</button>
                        <button type="button" class="relation-btn" data-relation="岳父">岳父</button>
                        <button type="button" class="relation-btn" data-relation="岳母">岳母</button>
                        <button type="button" class="relation-btn" data-relation="女婿">女婿</button>
                        <button type="button" class="relation-btn" data-relation="儿媳">儿媳</button>
                    </div>
                </div>
                <div class="relationship-category">
                    <h4>其他关系</h4>
                    <div class="relationship-options">
                        <button type="button" class="relation-btn" data-relation="朋友">朋友</button>
                        <button type="button" class="relation-btn" data-relation="同事">同事</button>
                        <button type="button" class="relation-btn" data-relation="邻居">邻居</button>
                        <button type="button" class="relation-btn" data-relation="其他">其他</button>
                    </div>
                </div>
            </div>
        </div>
        '''
        
        return mark_safe(visual_html + select_html)
    
    class Media:
        css = {
            'all': ('admin/css/relationship_widget.css',)
        }
        js = ('admin/js/relationship_widget.js',)


class RichTextWidget(forms.Textarea):
    """
    Simple rich text editor for story content
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'rich-text-editor',
            'rows': 8
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        textarea_html = super().render(name, value, attrs, renderer)
        
        toolbar_html = '''
        <div class="rich-text-toolbar">
            <div class="toolbar-group">
                <button type="button" class="toolbar-btn" data-command="bold" title="粗体">
                    <strong>B</strong>
                </button>
                <button type="button" class="toolbar-btn" data-command="italic" title="斜体">
                    <em>I</em>
                </button>
                <button type="button" class="toolbar-btn" data-command="underline" title="下划线">
                    <u>U</u>
                </button>
            </div>
            <div class="toolbar-group">
                <button type="button" class="toolbar-btn" data-command="heading" title="标题">
                    H
                </button>
                <button type="button" class="toolbar-btn" data-command="paragraph" title="段落">
                    P
                </button>
            </div>
            <div class="toolbar-group">
                <button type="button" class="toolbar-btn" data-command="quote" title="引用">
                    "
                </button>
                <button type="button" class="toolbar-btn" data-command="list" title="列表">
                    •
                </button>
            </div>
            <div class="toolbar-group">
                <button type="button" class="toolbar-btn" data-command="photo" title="插入照片">
                    📷
                </button>
                <button type="button" class="toolbar-btn" data-command="emoji" title="表情">
                    😊
                </button>
            </div>
        </div>
        '''
        
        return mark_safe(toolbar_html + textarea_html)
    
    class Media:
        css = {
            'all': ('admin/css/rich_text_widget.css',)
        }
        js = ('admin/js/rich_text_widget.js',)


class TagsWidget(forms.TextInput):
    """
    Widget for entering tags with auto-suggestions
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'tags-input',
            'placeholder': '输入标签，用逗号分隔...'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        input_html = super().render(name, value, attrs, renderer)
        
        tags_html = '''
        <div class="tags-wrapper">
            <div class="tags-container"></div>
            <div class="tags-suggestions">
                <div class="suggestion-category">
                    <h5>常用标签</h5>
                    <div class="tag-suggestions">
                        <span class="tag-suggestion">生日</span>
                        <span class="tag-suggestion">节日</span>
                        <span class="tag-suggestion">旅行</span>
                        <span class="tag-suggestion">聚会</span>
                        <span class="tag-suggestion">成长</span>
                        <span class="tag-suggestion">纪念</span>
                    </div>
                </div>
                <div class="suggestion-category">
                    <h5>情感标签</h5>
                    <div class="tag-suggestions">
                        <span class="tag-suggestion">温馨</span>
                        <span class="tag-suggestion">感动</span>
                        <span class="tag-suggestion">快乐</span>
                        <span class="tag-suggestion">怀念</span>
                        <span class="tag-suggestion">骄傲</span>
                        <span class="tag-suggestion">感恩</span>
                    </div>
                </div>
            </div>
        </div>
        '''
        
        return mark_safe(tags_html + input_html)
    
    class Media:
        css = {
            'all': ('admin/css/tags_widget.css',)
        }
        js = ('admin/js/tags_widget.js',)