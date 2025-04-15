from django.urls import path
from . import views

app_name = 'reqs'

urlpatterns = [
    path('', views.request_list, name='list'),
    path('create/', views.request_create, name='create'),
    path('<int:pk>/', views.request_detail, name='detail'),
    path('<int:pk>/edit/', views.request_edit, name='edit'),
    path('<int:pk>/approval/', views.request_approval, name='approval'),
    path('<int:pk>/attachment/', views.add_attachment, name='add_attachment'),
    path('attachment/<int:pk>/delete/', views.delete_attachment, name='delete_attachment'),
]