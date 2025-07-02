from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.static import serve
from django.conf import settings
import os


@login_required
def protected_react_serve(request):
    """Protected view to serve React app - requires authentication"""
    # If user is not authenticated, login_required decorator will redirect to login
    # Once authenticated, serve the React index.html
    document_root = os.path.join(settings.STATIC_ROOT, 'react')
    return serve(request, 'index.html', document_root=document_root)
