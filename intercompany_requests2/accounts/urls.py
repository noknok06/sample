from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.profile_view, name='profile'),
    path('users/', views.company_users_view, name='company_users'),
    path('users/<int:pk>/role/', views.update_user_role, name='update_role'),
]