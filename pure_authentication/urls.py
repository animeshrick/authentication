"""
URL configuration for pure_authentication project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from pure_authentication.admin_views import admin_log_view, admin_dashboard_view, AdminLogListView
from django.http import JsonResponse, HttpResponse
import os
from django.conf import settings
import markdown

def readme_view(request):
    readme_path = os.path.join(settings.BASE_DIR, 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, encoding='utf-8') as f:
            text = f.read()
        html = markdown.markdown(text)
        return HttpResponse(html)
    return HttpResponse('<h1>README.md not found</h1>', status=404)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/api/", include("auth_api.urls")),
    path("product/", include("product.urls")),
    path("cart/", include("cart.urls")),
    # Admin logging URLs
    path("admin-logs/", admin_log_view, name="admin_logs"),
    path("admin-dashboard/", admin_dashboard_view, name="admin_dashboard"),
    path("admin-logs-list/", AdminLogListView.as_view(), name="admin_logs_list"),
    path('', readme_view, name='root'),
]
