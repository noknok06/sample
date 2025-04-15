from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('activities/', views.activities, name='activities'),
    path('statistics/', views.statistics, name='statistics'),
]