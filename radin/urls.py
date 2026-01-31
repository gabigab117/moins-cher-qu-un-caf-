from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('vote/<int:pk>/<str:vote_type>/', views.vote, name='vote'),
]
