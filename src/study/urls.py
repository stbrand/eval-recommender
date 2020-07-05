from django.urls import path
from . import views
from .views import *

app_name='study'
urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('start/', views.start_view, name='start'),
    path('rating/<int:id>/', views.item_rating_view, name='rating_detail'),
    path('reclist_rating/', views.reclist_view, name='reclist_rating'),
    path('reclist_rating/<int:id>/', views.reclist_rating_view, name='reclist_rating_detail'),
    path('stop/', views.stop_view, name='stop'),

]
