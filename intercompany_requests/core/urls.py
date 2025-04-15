# urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ダッシュボード関連
    path('', views.dashboard, name='dashboard'),
    path('activity/', views.activity_list, name='activity_list'),
    
    # 要望関連
    path('requests/', views.request_list, name='request_list'),
    path('requests/new/', views.new_request, name='new_request'),
    path('requests/<int:pk>/', views.request_detail, name='request_detail'),
    path('requests/<int:pk>/status/', views.request_status, name='request_status'),
    path('requests/<int:pk>/update-status/', views.update_request_status, name='update_request_status'),
    
    # コメント関連
    path('requests/<int:request_id>/comments/', views.add_comment, name='add_comment'),
    path('comments/<int:pk>/like/', views.like_comment, name='like_comment'),
    path('comments/<int:pk>/reply/<int:request_id>/', views.reply_form, name='reply_form'),
    path('comment-form/<int:request_id>/', views.comment_form, name='comment_form'),
    
    # 会社関連
    path('companies/', views.company_list, name='company_list'),
    path('companies/new/', views.company_new, name='company_new'),
    path('companies/<int:pk>/', views.company_detail, name='company_detail'),
    path('companies/<int:pk>/edit/', views.company_edit, name='company_edit'),
    path('companies/invite/', views.company_invite, name='company_invite'),
    
    # ユーザー関連
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    
    # 認証関連
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    
    # その他
    path('features/', views.features, name='features'),
    path('pricing/', views.pricing, name='pricing'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # パスワードリセット関連
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='auth/password_reset.html'), 
         name='password_reset'),
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), 
         name='password_reset_complete'),
]