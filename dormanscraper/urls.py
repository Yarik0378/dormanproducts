from django.urls import path
from dormanscraper import views
urlpatterns = [path('add', views.upload_file, name='home'),
               path('', views.index),
               path('delete/<int:projectid>/', views.delete)]
