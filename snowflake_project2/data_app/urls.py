from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('generate-proposal/', views.generate_proposal, name='generate-proposal'),
    path('negotiations/', views.NegotiationListView.as_view(), name='negotiation-list'),
    path('negotiations/<int:pk>/', views.NegotiationDetailView.as_view(), name='negotiation-detail'),
    path('negotiations/new/', views.NegotiationCreateView.as_view(), name='negotiation-create'),
    path('negotiations/<int:pk>/edit/', views.NegotiationUpdateView.as_view(), name='negotiation-update'),
]