"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from family.views import protected_react_serve
import os

urlpatterns = [
    # Django Admin - 保持原有访问路径
    path('admin/', admin.site.urls),
    
    # API路由 - 为前端提供接口
    path('api/', include('api.urls')),
    
    # AI Integration - AI功能接口
    path('api/ai/', include('ai_integration.urls')),
    
    # React静态资源服务 - 为/app/路径下的资源提供服务
    re_path(r'^app/assets/(?P<path>.*)$', serve, {'document_root': os.path.join(settings.BASE_DIR, 'static/react/assets')}, name='react_assets'),
    re_path(r'^app/vite\.svg$', serve, {'document_root': os.path.join(settings.BASE_DIR, 'static/react'), 'path': 'vite.svg'}, name='react_vite_svg'),
    
    # React SPA - 仅在/app/路径下提供前端 (需要认证)
    re_path(r'^app/.*$', protected_react_serve, name='frontend'),
    
    # 根路径重定向到app
    path('', TemplateView.as_view(template_name='redirect.html'), name='root_redirect'),
]

# 静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # 生产环境：确保React静态文件服务优先级高于WhiteNoise
    pass
