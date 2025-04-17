from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    # 企業一覧・管理
    path('', views.company_list, name='list'),
    path('<int:pk>/', views.company_detail, name='detail'),
    path('<int:pk>/edit/', views.company_edit, name='edit'),
    path('create/', views.company_create, name='create'),
    
    # 企業招待・参加
    path('invite/', views.company_invite, name='invite'),
    path('join/', views.company_join, name='join'),
    
    # 企業間連携
    path('connect/', views.company_connect, name='connection_create'),  
    path('connections/', views.connection_list, name='connections'),
    path('connections/<int:pk>/respond/', views.connection_respond, name='connection_respond'),
]