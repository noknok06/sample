from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('dashboard.urls')),
    path('companies/', include('companies.urls')),
    path('requests/', include('reqs.urls')),
    path('profile/', include('accounts.urls')),
    path('notifications/', include('notifications.urls')),
    path('comments/', include('comments.urls')),  # コメントURLパターンを追加
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)