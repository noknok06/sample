from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('request/<int:request_id>/add/', views.add_comment, name='add'),
    path('<int:pk>/edit/', views.edit_comment, name='edit'),
    path('<int:pk>/delete/', views.delete_comment, name='delete'),
]