from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

admin.site.site_header = 'ONLINE EXAM API'
admin.site.site_title = 'ONLINE EXAM API'
admin.site.index_title = 'Welcome to dashboard'

schema_view = get_schema_view(
    openapi.Info(
        title="ONLINE EXAM APIv1",
        default_version="v1",
        description="API for project Online Exam",
        terms_of_service="",
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/exam/', include('exam.urls')),

    re_path(r'static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r"^swagger/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
