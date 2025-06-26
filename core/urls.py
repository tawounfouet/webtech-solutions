"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static

from . import views
from .ckeditor_cloudinary import ckeditor_upload_file, test_cloudinary_config
from .ckeditor5_views import upload_file as ckeditor5_upload

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("authentication.urls")),
    path("projects/", include("projects.urls")),
    # URL personnalisée pour l'upload CKEditor5 (doit être avant l'inclusion de ckeditor5)
    path("ckeditor5/image_upload/", ckeditor5_upload, name='ckeditor5_upload_override'),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path("ckeditor5/upload/", ckeditor_upload_file, name='ckeditor5_upload'),
    path("test-cloudinary/", test_cloudinary_config, name='test_cloudinary'),
    path("", views.index, name="index"),
]

# Ajouter les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
